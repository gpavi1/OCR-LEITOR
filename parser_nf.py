import re
import unicodedata
from datetime import datetime

DATE_RE = re.compile(r"\b(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})\b")

FINANCE_KEYWORDS = [
    "FATURA", "BOLETO", "PAGAMENTO", "DUPLICATA", "VENCIMENTO",
    "VENC", "VCTO", "VENCTO", "PARCELA", "COBRANCA", "COBRANÇA"
]

DATE_EXCLUDE_KEYWORDS = [
    "EMISSAO", "EMISSÃO", "SAIDA", "SAÍDA", "TRANSPORTE", "ENTREGA",
    "PROTOCOLO", "AUTORIZACAO", "AUTORIZAÇÃO", "RECEBIMENTO"
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
    data = {
        "elemento": None,
        "nfe": None,
        "chave": None,
        "vencimento": None,
        "raw": text,
    }

    for line in text.split("\n"):
        line_clean = line.strip()
        if len(line_clean) > 5 and line_clean.isupper() and not re.search(r"\d", line_clean):
            data["elemento"] = line_clean
            break

    nfe_candidates = re.findall(r"\b\d{6,15}\b", text)
    if nfe_candidates:
        data["nfe"] = max(nfe_candidates, key=len)

    data["chave"] = extrair_chave_acesso(text)
    data["vencimento"] = extrair_vencimento_financeiro(text)

    return data
