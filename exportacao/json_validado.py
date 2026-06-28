import datetime
import json
from decimal import Decimal
from pathlib import Path

from contratos.montador_documento_fiscal_v1 import montar_payload_documento_fiscal_v1


STATUS_DOCUMENTO_EXPORTAVEL = {"pendente_integracao", "integrado"}
EXPORT_DIR_RELATIVO = Path("exports") / "json"
DESTINO_EXPORTACAO_LOCAL = "arquivo_local_json"
MODO_EXPORTACAO_LOCAL = "manual_local"


def _valor_json_seguro(valor):
    if valor is None:
        return None

    if isinstance(valor, Decimal):
        return format(valor, "f")

    if hasattr(valor, "isoformat"):
        try:
            return valor.isoformat(timespec="seconds")
        except TypeError:
            return valor.isoformat()

    return valor


def _normalizar_documento(documento):
    return {
        "id": documento.get("id"),
        "arquivo_nome": _valor_json_seguro(documento.get("arquivo_nome")),
        "empresa": _valor_json_seguro(documento.get("empresa")),
        "numero_nf": _valor_json_seguro(documento.get("numero_nf")),
        "chave_acesso": _valor_json_seguro(documento.get("chave_acesso")),
        "vencimento": _valor_json_seguro(documento.get("vencimento")),
        "valor_total": _valor_json_seguro(documento.get("valor_total")),
        "status": _valor_json_seguro(documento.get("status")),
        "revisado": documento.get("revisado") is True,
        "revisado_por": _valor_json_seguro(documento.get("revisado_por")),
        "revisado_em": _valor_json_seguro(documento.get("revisado_em")),
        "json_path": _valor_json_seguro(documento.get("json_path")),
        "gerado_em": _valor_json_seguro(
            documento.get("atualizado_em")
            or documento.get("revisado_em")
            or documento.get("criado_em")
        ),
    }


def _validar_documento_exportavel(documento):
    if not isinstance(documento, dict):
        raise ValueError("Documento inválido para exportação.")

    documento_id = documento.get("id")
    if documento_id in (None, ""):
        raise ValueError("Documento sem identificador para exportação.")

    if documento.get("revisado") is not True:
        raise ValueError("A exportação exige documento revisado/aprovado.")

    status = str(documento.get("status") or "").strip()
    if status not in STATUS_DOCUMENTO_EXPORTAVEL:
        raise ValueError(f"Status não permite exportação: {status or 'desconhecido'}.")


def gerar_nome_arquivo_exportacao(documento_id, agora=None):
    momento = agora or datetime.datetime.now()
    timestamp = momento.strftime("%Y%m%d%H%M%S")
    identificador = "".join(c for c in str(documento_id) if c.isdigit()) or "0"
    return f"documento_{identificador}_{timestamp}.json"


def montar_payload_exportacao_documento(documento):
    _validar_documento_exportavel(documento)
    dados = _normalizar_documento(documento)
    return montar_payload_documento_fiscal_v1(
        dados,
        destino=DESTINO_EXPORTACAO_LOCAL,
        modo=MODO_EXPORTACAO_LOCAL,
    )


def exportar_documento_revisado(documento_id, obter_documento, root_dir=None, agora=None):
    if not callable(obter_documento):
        raise ValueError("obter_documento deve ser chamável")

    documento = obter_documento(documento_id)
    if not documento:
        return {
            "ok": False,
            "status": "documento_nao_encontrado",
            "caminho_relativo": None,
            "erro": "Documento não encontrado.",
        }

    try:
        payload = montar_payload_exportacao_documento(documento)
        base_dir = Path(root_dir or Path(__file__).resolve().parents[1]).resolve()
        destino_dir = base_dir / EXPORT_DIR_RELATIVO
        destino_dir.mkdir(parents=True, exist_ok=True)

        nome_arquivo = gerar_nome_arquivo_exportacao(documento.get("id"), agora=agora)
        caminho_arquivo = destino_dir / nome_arquivo
        caminho_arquivo.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        caminho_relativo = caminho_arquivo.relative_to(base_dir).as_posix()
        return {
            "ok": True,
            "status": "exportado_local",
            "caminho_relativo": caminho_relativo,
            "erro": None,
        }
    except ValueError as exc:
        return {
            "ok": False,
            "status": "erro_validacao",
            "caminho_relativo": None,
            "erro": str(exc),
        }
    except Exception:
        return {
            "ok": False,
            "status": "erro_exportacao",
            "caminho_relativo": None,
            "erro": "Falha segura na exportação local do JSON validado.",
        }
