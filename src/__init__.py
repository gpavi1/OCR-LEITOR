"""
Pacote de módulos OCR LEITOR
"""

from .leitor import LeitorOCR
from .extrator import ExtratorCampos
from .monday_api import MondayAPI
from .uploader import Uploader

__version__ = "1.0.0"
__all__ = ["LeitorOCR", "ExtratorCampos", "MondayAPI", "Uploader"]
