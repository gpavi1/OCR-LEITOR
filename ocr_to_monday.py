import os
import requests
import json
import time
import re
import mimetypes
import unicodedata
from datetime import datetime
from PIL import Image
import pytesseract

# -------------------------
# PATHS / CONFIG
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "settings.json")
INPUT_FOLDER = os.path.join(BASE_DIR, "input")
PROCESSED_FOLDER = os.path.join(BASE_DIR, "processed")
ERROR_FOLDER = os.path.join(BASE_DIR, "erro")

os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(ERROR_FOLDER, exist_ok=True)

config = json.load(open(CONFIG_PATH, encoding="utf-8"))

# -------------------------
# CONFIG OCR (Windows)
# -------------------------
tesseract_path = config.get("tesseract_path") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if tesseract_path and os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

OCR_LANGUAGE = config.get("ocr", {}).get("language", "por+eng")
if OCR_LANGUAGE == "por":
    OCR_LANGUAGE = "por+eng"

# -------------------------
# CONFIG MONDAY
# -------------------------
API_URL = "https://api.monday.com/v2"
API_FILE_URL = "https://api.monday.com/v2/file"

monday_cfg = config.get("monday", {})
API_TOKEN = monday_cfg.get("api_token") or config.get("monday_api_key", "")
BOARD_ID = monday_cfg.get("board_id") or config.get("monday_board_id", "")

DEFAULT_COLUMNS = {
    "nfe": "numeric_mkrscq8v",
    "chave": "text_mm1qqv4j",
    "vencimento": "date_mky1yfhg",
    "arquivo": "files",
}
COLUMN_IDS = DEFAULT_COLUMNS | monday_cfg.get("columns", {}) | monday_cfg.get("colunas", {})


def _auth_header_value() -> str:
    token = (API_TOKEN or "").strip()
    if token.lower().startswith("bearer "):
        return token
    return f"Bearer {token}"


HEADERS = {
    "Authorization": _auth_header_value(),
    "Content-Type": "application/json",
}

FILE_HEADERS = {
    "Authorization": _auth_header_value(),
}

# -------------------------
# OCR
# -------------------------
def extract_text(image_path):
    img = Image.open(image_path)
    return pytesseract.image_to_string(img, lang=OCR_LANGUAGE)

# -------------------------
# PARSER
# -------------------------
DATE_RE = re.compile(r"\b(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})\b")

FINANCE_KEYWORDS = [
    "FATURA", "BOLETO", "PAGAMENTO", "DUPLICATA", "VENCIMENTO",
    "VENC", "VCTO", "VENCTO", "PARCELA", "COBRANCA", "COBRANÇA",
]

DATE_EXCLUDE_KEYWORDS = [
    "EMISSAO", "EMISSÃO", "SAIDA", "SAÍDA", "TRANSPORTE", "ENTREGA",
    "PROTOCOLO", "AUTORIZACAO", "AUTORIZAÇÃO", "RECEBIMENTO",
]


def _normalizar_texto(texto: str) -> str:
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.upper()


def _corrigir_ocr_digitos(texto: str) -> str:
    tabela = str.maketrans({"O": "0", "o": "0", "I": "1", "i": "1", "l": "1", "S": "5", "s": "5"})
    return (texto or "").translate(tabela)


def extrair_chave_acesso(texto: str):
    if not texto:
        return None

    padrao_quebrado = re.compile(r"(?:[0-9][\s.\-/]*){44}")
    candidatos = []

    # 1) Caminho principal: dígitos reais, aceitando espaços/quebras/pontos/hífens.
    for match in padrao_quebrado.finditer(texto):
        apenas_digitos = re.sub(r"\D", "", match.group(0))
        if len(apenas_digitos) == 44:
            candidatos.append((match.start(), apenas_digitos))

    # 2) Fallback: somente linhas/blocos com muitos dígitos recebem correção OCR.
    # Isso evita transformar palavras como ACESSO em números falsos.
    if not candidatos:
        for linha in texto.splitlines():
            if len(re.sub(r"\D", "", linha)) < 30:
                continue
            linha_corrigida = _corrigir_ocr_digitos(linha)
            for match in padrao_quebrado.finditer(linha_corrigida):
                apenas_digitos = re.sub(r"\D", "", match.group(0))
                if len(apenas_digitos) == 44:
                    candidatos.append((0, apenas_digitos))

    # 3) Último fallback: compactar apenas os dígitos originais do documento.
    if not candidatos:
        compacto = re.sub(r"\D", "", texto)
        match = re.search(r"\d{44}", compacto)
        return match.group(0) if match else None

    texto_norm = _normalizar_texto(texto)
    palavras_chave = ["CHAVE", "ACESSO", "CHAVE DE ACESSO", "NFE", "NF-E", "DANFE"]

    def score(candidato):
        pos, _chave = candidato
        janela = texto_norm[max(0, pos - 250): pos + 250]
        score_base = 1000 + pos
        for palavra in palavras_chave:
            if palavra in janela:
                score_base -= 200
        return score_base

    candidatos.sort(key=score)
    return candidatos[0][1]


def _converter_data_ddmmyyyy(dia: str, mes: str, ano: str):
    try:
        d = int(dia)
        m = int(mes)
        y = int(ano)
        if y < 100:
            y = 2000 + y if y < 70 else 1900 + y
        if y < 2000 or y > 2100:
            return None
        return datetime(y, m, d).strftime("%d/%m/%Y")
    except ValueError:
        return None


def extrair_vencimento_financeiro(texto: str):
    if not texto:
        return None

    texto_norm = _normalizar_texto(texto)
    candidatos = []

    for match in DATE_RE.finditer(texto_norm):
        data_fmt = _converter_data_ddmmyyyy(match.group(1), match.group(2), match.group(3))
        if not data_fmt:
            continue

        inicio = max(0, match.start() - 160)
        fim = min(len(texto_norm), match.end() + 160)
        janela = texto_norm[inicio:fim]

        if not any(palavra in janela for palavra in FINANCE_KEYWORDS):
            continue

        menor_distancia = 9999
        for palavra in FINANCE_KEYWORDS:
            for kw_match in re.finditer(re.escape(palavra), janela):
                distancia = abs((inicio + kw_match.start()) - match.start())
                menor_distancia = min(menor_distancia, distancia)

        menor_exclusao = 9999
        for palavra in DATE_EXCLUDE_KEYWORDS:
            for ex_match in re.finditer(re.escape(palavra), janela):
                distancia = abs((inicio + ex_match.start()) - match.start())
                menor_exclusao = min(menor_exclusao, distancia)

        # Só ignora se a palavra fiscal/operacional estiver mais perto da data
        # do que o contexto financeiro. Isso evita descartar um vencimento real
        # apenas porque a nota também tem DATA DE EMISSAO em outro bloco.
        if menor_exclusao < menor_distancia:
            continue

        candidatos.append((menor_distancia, match.start(), data_fmt))

    if not candidatos:
        return None

    candidatos.sort(key=lambda item: (item[0], item[1]))
    return candidatos[0][2]


def parse_ocr(text):
    data = {"elemento": None, "nfe": None, "chave": None, "vencimento": None, "raw": text}

    for line in text.split("\n"):
        line_clean = line.strip()
        if len(line_clean) > 5 and line_clean.isupper():
            data["elemento"] = line_clean
            break

    nfe_candidates = re.findall(r"\b\d{6,15}\b", text)
    if nfe_candidates:
        data["nfe"] = max(nfe_candidates, key=len)

    data["chave"] = extrair_chave_acesso(text)
    data["vencimento"] = extrair_vencimento_financeiro(text)
    return data

# -------------------------
# CONVERSÃO DE DATA PARA MONDAY
# -------------------------
def format_date(date_str):
    if not date_str:
        return ""
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return ""

# -------------------------
# CREATE ITEM MONDAY
# -------------------------
def create_item(parsed, filename):
    item_name = parsed.get("elemento") or filename
    date_iso = format_date(parsed.get("vencimento"))

    column_values = {}
    if parsed.get("nfe"):
        column_values[COLUMN_IDS["nfe"]] = str(parsed["nfe"])
    if parsed.get("chave"):
        column_values[COLUMN_IDS["chave"]] = str(parsed["chave"])
    if date_iso:
        column_values[COLUMN_IDS["vencimento"]] = {"date": date_iso}

    query = """
    mutation ($board_id: ID!, $item_name: String!, $column_values: JSON) {
      create_item (board_id: $board_id, item_name: $item_name, column_values: $column_values) {
        id
      }
    }
    """

    variables = {
        "board_id": str(BOARD_ID),
        "item_name": item_name,
        "column_values": json.dumps(column_values, ensure_ascii=False),
    }

    response = requests.post(API_URL, json={"query": query, "variables": variables}, headers=HEADERS, timeout=30)

    try:
        data = response.json()
    except ValueError:
        return {"errors": [{"message": response.text}], "status_code": response.status_code}

    if response.status_code >= 400:
        data.setdefault("errors", []).append({"message": response.text, "status_code": response.status_code})

    return data

# -------------------------
# UPLOAD IMAGEM MONDAY
# -------------------------
def upload_file_to_monday(item_id, file_path):
    if not item_id:
        print("❌ Upload cancelado: item_id inválido")
        return False, "item_id inválido"

    if not os.path.exists(file_path):
        print("❌ Upload cancelado: arquivo não encontrado")
        return False, "arquivo não encontrado"

    column_id = COLUMN_IDS.get("arquivo", "files")
    filename = os.path.basename(file_path)
    mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

    query = f'''
    mutation ($file: File!) {{
      add_file_to_column (item_id: {item_id}, column_id: "{column_id}", file: $file) {{
        id
      }}
    }}
    '''

    variables = json.dumps({"file": None})
    map_payload = json.dumps({"file": ["variables.file"]})

    with open(file_path, "rb") as file:
        files = {
            "query": (None, query),
            "variables": (None, variables),
            "map": (None, map_payload),
            "file": (filename, file, mime_type),
        }
        response = requests.post(API_FILE_URL, headers=FILE_HEADERS, files=files, timeout=60)

    try:
        data = response.json()
    except ValueError:
        return False, response.text

    if response.status_code >= 400 or data.get("errors") or data.get("error_message"):
        return False, data

    return True, data

# -------------------------
# MOVIMENTAÇÃO SEGURA
# -------------------------
def move_unique(src, folder):
    os.makedirs(folder, exist_ok=True)
    filename = os.path.basename(src)
    dest = os.path.join(folder, filename)
    if os.path.exists(dest):
        base, ext = os.path.splitext(filename)
        dest = os.path.join(folder, f"{base}_{int(time.time())}{ext}")
    os.rename(src, dest)
    return dest

# -------------------------
# PROCESSAMENTO
# -------------------------
def process_images():
    print("🚀 SCRIPT INICIADO")
    print("📂 INPUT:", INPUT_FOLDER)

    if not API_TOKEN or not BOARD_ID:
        print("❌ Configuração Monday incompleta. Verifique config/settings.json")
        return

    files = os.listdir(INPUT_FOLDER)
    print("📦 ARQUIVOS:", files)

    for file in files:
        if not file.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        path = os.path.join(INPUT_FOLDER, file)
        try:
            print(f"\n🔍 Processando: {file}")
            text = extract_text(path)
            print("📄 OCR:", text[:300])

            parsed = parse_ocr(text)
            print("🧠 Dados:", {k: v for k, v in parsed.items() if k != "raw"})

            response = create_item(parsed, file)
            print("📤 Monday:", response)

            item_id = response.get("data", {}).get("create_item", {}).get("id")
            if not item_id:
                print("❌ Item não criado. Enviando arquivo para erro.")
                move_unique(path, ERROR_FOLDER)
                continue

            upload_ok, upload_result = upload_file_to_monday(item_id, path)
            print("📎 Upload:", upload_result)

            if not upload_ok:
                print("❌ Upload falhou. Item criado, mas arquivo movido para erro.")
                move_unique(path, ERROR_FOLDER)
                continue

            dest = move_unique(path, PROCESSED_FOLDER)
            print("✅ Processado:", dest)

        except Exception as e:
            print(f"❌ ERRO EM {file}: {e}")
            if os.path.exists(path):
                move_unique(path, ERROR_FOLDER)

# -------------------------
# EXECUÇÃO
# -------------------------
if __name__ == "__main__":
    process_images()
