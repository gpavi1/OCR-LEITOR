"""
VALIDACAO-INTEGRACAO-OPERACIONAL-OCR-01: Validador operacional central da integracao Monday.

Nao chama API externa.
Nao importa requests.
Nao importa urllib.
Nao le .env diretamente.
Nao acessa banco diretamente.
Recebe tudo por parametro.
"""

from conectores.monday_payload import validar_documento_apto_monday


COLUNAS_OBRIGATORIAS = {
    "empresa",
    "numero_nf",
    "chave_acesso",
    "vencimento",
    "valor_total",
    "observacao_revisao",
}


def _classificar_valor_config(valor):
    if valor is None:
        return "AUSENTE"
    texto = str(valor).strip()
    if not texto:
        return "AUSENTE"
    texto_lower = texto.lower()
    placeholders = ("cole", "aqui", "exemplo", "nao_cole", "não_cole", "seu_")
    if any(p in texto_lower for p in placeholders):
        return "PLACEHOLDER"
    if texto_lower.startswith("exemplo_"):
        return "PLACEHOLDER"
    return "CONFIGURADO"


def _validar_config(token, board_id, mapa_colunas):
    bloqueios = []
    proximos_passos = []

    if _classificar_valor_config(token) != "CONFIGURADO":
        bloqueios.append("MONDAY_API_TOKEN ausente ou placeholder.")
        proximos_passos.append(
            "Configure MONDAY_API_TOKEN no arquivo .env com um token valido do Monday."
        )

    if _classificar_valor_config(board_id) != "CONFIGURADO":
        bloqueios.append("MONDAY_BOARD_ID ausente ou placeholder.")
        proximos_passos.append(
            "Configure MONDAY_BOARD_ID no arquivo .env com o ID do board Monday."
        )

    if not isinstance(mapa_colunas, dict) or not mapa_colunas:
        bloqueios.append("Mapa de colunas Monday ausente ou invalido.")
        proximos_passos.append(
            "Configure todas as colunas Monday no .env (MONDAY_COLUMN_*)."
        )
    else:
        for col in COLUNAS_OBRIGATORIAS:
            if col not in mapa_colunas or not mapa_colunas[col]:
                bloqueios.append(
                    f"Coluna obrigatoria nao configurada: {col}."
                )
                proximos_passos.append(
                    f"Configure MONDAY_COLUMN_{col.upper()} no .env com o ID da coluna Monday."
                )

    return bloqueios, proximos_passos


def _validar_duplicidade(tentativas):
    bloqueios = []
    avisos = []

    if not tentativas or not isinstance(tentativas, list):
        return bloqueios, avisos

    tem_sucesso = any(
        t.get("status") == "monday_envio_sucesso" for t in tentativas
    )
    tem_destino = any(
        t.get("destino_externo_id") for t in tentativas
    )

    if tem_sucesso:
        bloqueios.append(
            "Ja existe envio registrado para este documento. "
            "Verifique o historico antes de reenviar."
        )
    elif tem_destino:
        bloqueios.append(
            "Ja existe tentativa com destino externo para este documento. "
            "Verifique o historico."
        )
    else:
        tem_falha_sem_destino = any(
            t.get("status") in ("monday_envio_falha", "monday_envio_bloqueado")
            and not t.get("destino_externo_id")
            for t in tentativas
        )
        if tem_falha_sem_destino:
            avisos.append(
                "Falhas anteriores sem destino externo identificado. "
                "Pode tentar novamente."
            )

    return bloqueios, avisos


def validar_integracao_monday(
    documento=None,
    token="",
    board_id="",
    mapa_colunas=None,
    tentativas=None,
):
    resultado = {
        "config_ok": False,
        "documento_ok": False,
        "pode_simular": False,
        "pode_enviar": False,
        "bloqueios": [],
        "avisos": [],
        "proximos_passos": [],
    }

    bloqueios = []
    avisos = []
    proximos_passos = []

    config_bloqueios, config_passos = _validar_config(token, board_id, mapa_colunas)
    config_ok = len(config_bloqueios) == 0
    bloqueios.extend(config_bloqueios)
    proximos_passos.extend(config_passos)
    resultado["config_ok"] = config_ok

    if documento is not None and isinstance(documento, dict):
        try:
            apto, doc_bloqueios, doc_avisos = validar_documento_apto_monday(documento)
            resultado["documento_ok"] = apto
            if not apto:
                bloqueios.extend(doc_bloqueios)
                for b in doc_bloqueios:
                    b_lower = b.lower()
                    if "status" in b_lower:
                        proximos_passos.append(
                            "Revise o documento para avancar o status para 'Pendente integracao'."
                        )
                    elif "revisad" in b_lower:
                        proximos_passos.append(
                            "Aprove o documento na tela de detalhes antes de integrar."
                        )
                    elif "empresa" in b_lower:
                        proximos_passos.append(
                            "Preencha o campo 'Empresa' no documento."
                        )
                    elif "nf" in b_lower or "chave" in b_lower:
                        proximos_passos.append(
                            "Preencha o numero da NF e/ou chave de acesso no documento."
                        )
            avisos.extend(doc_avisos)
        except Exception:
            resultado["documento_ok"] = False
            bloqueios.append("Erro ao validar documento para integracao Monday.")
            proximos_passos.append("Verifique se o documento possui todos os campos necessarios.")
    else:
        resultado["documento_ok"] = False
        bloqueios.append("Nenhum documento informado para validacao.")
        proximos_passos.append("Selecione um documento revisado na fila de integracao.")

    dup_bloqueios, dup_avisos = _validar_duplicidade(tentativas)
    bloqueios.extend(dup_bloqueios)
    avisos.extend(dup_avisos)

    pode_simular = resultado["documento_ok"]

    if pode_simular and not config_ok:
        avisos.append(
            "Simulacao permitida, mas envio real bloqueado "
            "ate concluir a configuracao Monday."
        )
        proximos_passos.append("Complete a configuracao Monday para liberar o envio real.")

    pode_enviar = resultado["documento_ok"] and config_ok
    if any("Ja existe envio registrado" in b or "Ja existe tentativa" in b for b in bloqueios):
        pode_enviar = False

    resultado["pode_simular"] = pode_simular
    resultado["pode_enviar"] = pode_enviar
    resultado["bloqueios"] = bloqueios
    resultado["avisos"] = avisos
    resultado["proximos_passos"] = proximos_passos

    return resultado
