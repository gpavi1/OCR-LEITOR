from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class CampoExtraido:
    valor: Any
    confianca: float
    fonte: Optional[str] = None


@dataclass
class DocumentoFiscalExtraido:
    schema: str
    status: str
    cliente_id: int
    documento: Dict[str, Any]
    arquivo: Dict[str, Any]
    ocr: Dict[str, Any]
    validacao: Dict[str, Any]
    integracoes: Dict[str, Any] = field(default_factory=dict)
    criado_em: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def data_br_para_iso(data: Optional[str]) -> Optional[str]:
    if not data:
        return None
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(data, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def montar_documento_fiscal(
    *,
    cliente_id: int,
    parsed: Dict[str, Any],
    texto_extraido: str,
    arquivo_nome: str,
    arquivo_origem: str,
    arquivo_hash: Optional[str],
    arquivo_destino: Optional[str] = None,
    engine: str = "tesseract",
    idiomas: Optional[List[str]] = None,
) -> DocumentoFiscalExtraido:
    empresa = parsed.get("elemento") or parsed.get("empresa")
    numero_nf = parsed.get("nfe") or parsed.get("numero_nf")
    chave = parsed.get("chave") or parsed.get("chave_acesso")
    vencimento_br = parsed.get("vencimento")
    vencimento_iso = data_br_para_iso(vencimento_br)

    valor_total = parsed.get("valor_total")
    try:
        valor_total = float(valor_total) if valor_total is not None else None
    except (TypeError, ValueError):
        valor_total = None

    chave_ok = bool(chave and len(str(chave)) == 44 and str(chave).isdigit())
    vencimento_ok = bool(vencimento_iso)
    obrigatorios_ok = bool(empresa and numero_nf and chave_ok and vencimento_ok)

    avisos: List[str] = []
    if not empresa:
        avisos.append("empresa_nao_extraida")
    if not numero_nf:
        avisos.append("numero_nf_nao_extraido")
    if not chave_ok:
        avisos.append("chave_acesso_invalida_ou_nao_extraida")
    if not vencimento_ok:
        avisos.append("vencimento_nao_validado")
    if valor_total is None:
        avisos.append("valor_total_nao_extraido")

    status = "sucesso" if obrigatorios_ok else "parcial"

    return DocumentoFiscalExtraido(
        schema="ocr_leitor.documento_fiscal.v1",
        status=status,
        cliente_id=cliente_id,
        documento={
            "tipo": "nota_fiscal",
            "empresa": asdict(CampoExtraido(empresa, 90 if empresa else 0, "parser_nf")),
            "numero_nf": asdict(CampoExtraido(numero_nf, 90 if numero_nf else 0, "parser_nf")),
            "chave_acesso": asdict(CampoExtraido(chave, 98 if chave_ok else 0, "sequencia_44_digitos")),
            "vencimento": asdict(CampoExtraido(vencimento_iso, 95 if vencimento_ok else 0, "contexto_financeiro")),
            "valor_total": asdict(CampoExtraido(valor_total, 95 if valor_total is not None else 0, "valor_total_nota_fiscal" if valor_total is not None else None)),
        },
        arquivo={
            "nome": arquivo_nome,
            "origem": arquivo_origem,
            "destino": arquivo_destino,
            "hash_sha256": arquivo_hash,
        },
        ocr={
            "engine": engine,
            "idiomas": idiomas or ["por", "eng"],
            "texto_extraido": texto_extraido,
        },
        validacao={
            "chave_acesso_valida": chave_ok,
            "vencimento_validado_por_palavra_chave": vencimento_ok,
            "campos_obrigatorios_ok": obrigatorios_ok,
            "avisos": avisos,
        },
        integracoes={
            "monday": {"enviado": False, "item_id": None, "erro": None}
        },
    )
