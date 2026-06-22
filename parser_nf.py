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




EMPRESA_SUFFIX_LINES = {"LTDA", "LTDA.", "ME", "EIRELI", "EPP", "S/A", "SA"}

EMPRESA_CABECALHOS_BLOQUEADOS = [
    "DANFE",
    "NOTA FISCAL ELETRONICA",
    "DOCUMENTO AUXILIAR",
    "NATUREZA DA OPERACAO",
    "PROTOCOLO DE AUTORIZACAO",
    "INSCRICAO ESTADUAL",
    "DESTINATARIO",
    "REMETENTE",
    "NOME / RAZAO SOCIAL",
    "ENDERECO",
    "BAIRRO",
    "MUNICIPIO",
    "FATURAS",
    "DUPLICATAS",
    "CALCULO DO IMPOSTO",
    "BASE DE CALCULO",
    "VALOR DO ICMS",
    "VALOR TOTAL",
    "CHAVE DE ACESSO",
    "CONSULTA DE AUTENTICIDADE",
    "SEFAZ",
    "FOLHA",
    "SERIE",
]


def _limpar_espacos(texto: str) -> str:
    return re.sub(r"\s+", " ", (texto or "").strip())


def _eh_cabecalho_fiscal(linha_norm: str) -> bool:
    if not linha_norm or len(linha_norm) < 3:
        return True
    if any(cab in linha_norm for cab in EMPRESA_CABECALHOS_BLOQUEADOS):
        return True
    if re.search(r"\d", linha_norm):
        return True
    return False


def _parece_nome_empresa(candidato_norm: str) -> bool:
    candidato_norm = _limpar_espacos(candidato_norm)
    if _eh_cabecalho_fiscal(candidato_norm):
        return False

    palavras = [p for p in candidato_norm.split(" ") if p]
    if len(palavras) < 2:
        return False

    tem_sufixo = any(
        candidato_norm.endswith(f" {sufixo}") or candidato_norm == sufixo
        for sufixo in EMPRESA_SUFFIX_LINES
    )
    if tem_sufixo:
        return True

    return len(palavras) >= 3 and len(candidato_norm) >= 12


def extrair_empresa(texto: str):
    if not texto:
        return None

    linhas = [_limpar_espacos(linha) for linha in texto.splitlines()]
    linhas = [linha for linha in linhas if linha]

    # Emitente normalmente fica no topo da nota.
    # Limitamos a busca para evitar pegar destinatario/remetente.
    limite = linhas[:60]

    for idx, linha in enumerate(limite):
        linha_norm = _normalizar_texto(linha)
        if _eh_cabecalho_fiscal(linha_norm):
            continue

        proxima_norm = ""
        if idx + 1 < len(limite):
            proxima_norm = _normalizar_texto(limite[idx + 1])

        candidato = linha_norm

        # Caso comum em NF: nome em uma linha e LTDA/ME/EIRELI na linha seguinte.
        if proxima_norm in EMPRESA_SUFFIX_LINES:
            candidato = f"{linha_norm} {proxima_norm.replace('.', '')}"

        candidato = _limpar_espacos(candidato)

        if _parece_nome_empresa(candidato):
            return candidato

    return None


def extrair_numero_nf(texto: str):
    if not texto:
        return None

    texto_norm = _normalizar_texto(texto)

    # Número da nota normalmente aparece no cabeçalho.
    # Limitar evita pegar protocolo, CNPJ, fatura ou chave.
    janela_inicial = texto_norm[:2500]

    padroes_contextuais = [
        r"\bNRO\s*[:\-]?\s*(\d{1,9})\b",
        r"\bN[º°O]\s*[:\-]?\s*(\d{1,9})\b",
        r"\bNUMERO\s*(?:DA\s*)?(?:NF|NOTA)?\s*[:\-]?\s*(\d{1,9})\b",
        r"\bNF\s*[:\-]?\s*(\d{1,9})\b",
        r"\bNOTA\s+FISCAL\s*(?:NRO|N[º°O]|NUMERO)?\s*[:\-]?\s*(\d{1,9})\b",
    ]

    for padrao in padroes_contextuais:
        for match in re.finditer(padrao, janela_inicial):
            numero = re.sub(r"\D", "", match.group(1))
            if not numero:
                continue

            # Evita aceitar ano como número da NF.
            if re.fullmatch(r"(?:19|20)\d{2}", numero):
                continue

            return numero

    return None



def _parse_valor_brl(valor: str):
    if not valor:
        return None

    valor = valor.strip()
    valor = valor.replace("R$", "").replace(" ", "")

    # Formato BR: 1.234,56 ou 656,30
    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    else:
        # evita aceitar números longos sem centavos como valor
        if len(re.sub(r"\D", "", valor)) > 6:
            return None

    try:
        return float(valor)
    except ValueError:
        return None


def extrair_valor_total(texto: str):
    if not texto:
        return None

    texto_norm = _normalizar_texto(texto)

    padroes = [
        r"VALOR\s+TOTAL\s+DA\s+NOTA\s+FISCAL\s*[\r\n\s]+(?:R\$)?\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}|[0-9]+,[0-9]{2})",
        r"VALOR\s+TOTAL\s+DA\s+NOTA\s*[\r\n\s]+(?:R\$)?\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}|[0-9]+,[0-9]{2})",
        r"TOTAL\s+DA\s+NOTA\s+FISCAL\s*[\r\n\s]+(?:R\$)?\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}|[0-9]+,[0-9]{2})",
    ]

    for padrao in padroes:
        match = re.search(padrao, texto_norm, flags=re.IGNORECASE)
        if match:
            return _parse_valor_brl(match.group(1))

    # Fallback controlado: procura a linha do rótulo e pega o próximo valor monetário.
    linhas = [_normalizar_texto(linha) for linha in texto.splitlines()]
    for idx, linha in enumerate(linhas):
        if "VALOR TOTAL DA NOTA FISCAL" in linha or "VALOR TOTAL DA NOTA" in linha:
            janela = " ".join(linhas[idx:idx + 4])
            valores = re.findall(r"(?:R\$)?\s*([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}|[0-9]+,[0-9]{2})", janela)
            if valores:
                return _parse_valor_brl(valores[-1])

    return None

def parse_ocr(text):
    data = {
        "elemento": None,
        "nfe": None,
        "chave": None,
        "vencimento": None,
        "raw": text,
    }

    data["elemento"] = extrair_empresa(text)
    data["nfe"] = extrair_numero_nf(text)
    data["valor_total"] = extrair_valor_total(text)

    data["chave"] = extrair_chave_acesso(text)
    data["vencimento"] = extrair_vencimento_financeiro(text)

    return data
