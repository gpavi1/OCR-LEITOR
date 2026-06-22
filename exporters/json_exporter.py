import json
from pathlib import Path
from typing import Dict, Any


def salvar_json(documento: Dict[str, Any], output_dir: str, nome_base: str) -> str:
    pasta = Path(output_dir)
    pasta.mkdir(parents=True, exist_ok=True)

    safe_name = Path(nome_base).stem.replace(" ", "_")
    caminho = pasta / f"{safe_name}.json"

    contador = 1
    while caminho.exists():
        caminho = pasta / f"{safe_name}_{contador}.json"
        contador += 1

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(documento, f, ensure_ascii=False, indent=2)

    return str(caminho)
