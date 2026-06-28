from conectores.conector_simulado import exportar_json_simulado
from contratos.montador_documento_fiscal_v1 import montar_payload_documento_fiscal_v1


def exportar_documento_fiscal_v1_simulado(
    dados_documento,
    destino_dir,
    destino="fechames_fiscal",
):
    payload = montar_payload_documento_fiscal_v1(
        dados_documento,
        destino=destino,
        modo="simulado",
    )
    caminho_exportado = exportar_json_simulado(payload, destino_dir)

    return {
        "status": "exportado_simulado",
        "caminho": caminho_exportado,
        "destino": destino,
        "modo": "simulado",
    }
