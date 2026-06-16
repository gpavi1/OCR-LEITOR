"""
Script de validação da instalação
Verifica se todos os componentes estão instalados corretamente
"""

import sys
import os
from pathlib import Path


def verificar_python():
    """Verifica versão do Python"""
    print("🔍 Verificando Python...")
    versao = sys.version_info
    if versao.major >= 3 and versao.minor >= 8:
        print(f"   ✅ Python {versao.major}.{versao.minor}.{versao.micro} - OK")
        return True
    else:
        print(f"   ❌ Python {versao.major}.{versao.minor} - Requer 3.8+")
        return False


def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print("\n🔍 Verificando dependências Python...")
    
    dependencias = {
        "pytesseract": "pytesseract",
        "cv2": "opencv-python",
        "pdf2image": "pdf2image",
        "PIL": "Pillow",
        "requests": "requests"
    }
    
    todas_ok = True
    
    for modulo, pacote in dependencias.items():
        try:
            __import__(modulo)
            print(f"   ✅ {pacote} - OK")
        except ImportError:
            print(f"   ❌ {pacote} - NÃO INSTALADO")
            print(f"      Instale com: pip install {pacote}")
            todas_ok = False
    
    return todas_ok


def verificar_tesseract():
    """Verifica se Tesseract OCR está instalado"""
    print("\n🔍 Verificando Tesseract OCR...")
    
    try:
        import pytesseract
        from PIL import Image
        
        # Tentar usar tesseract
        tesseract_cmd = pytesseract.pytesseract.pytesseract_cmd
        
        if tesseract_cmd:
            print(f"   ✅ Tesseract encontrado em: {tesseract_cmd}")
            return True
        else:
            # Tentar localizá-lo automaticamente
            import subprocess
            try:
                resultado = subprocess.run(
                    ["tesseract", "--version"],
                    capture_output=True,
                    text=True
                )
                if resultado.returncode == 0:
                    print(f"   ✅ Tesseract - OK (automático)")
                    return True
            except:
                pass
        
        print("   ❌ Tesseract OCR - NÃO ENCONTRADO")
        print("      Windows: choco install tesseract")
        print("      Linux:   sudo apt-get install tesseract-ocr")
        print("      macOS:   brew install tesseract")
        return False
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar Tesseract: {str(e)}")
        return False


def verificar_estrutura_pastas():
    """Verifica se as pastas necessárias existem"""
    print("\n🔍 Verificando estrutura de pastas...")
    
    pastas_necessarias = [
        "entrada",
        "processadas",
        "erro",
        "config",
        "logs",
        "src"
    ]
    
    todas_ok = True
    
    for pasta in pastas_necessarias:
        caminho = Path(pasta)
        if caminho.exists():
            print(f"   ✅ {pasta}/ - OK")
        else:
            print(f"   ❌ {pasta}/ - NÃO ENCONTRADO")
            todas_ok = False
    
    return todas_ok


def verificar_arquivos_config():
    """Verifica se os arquivos de configuração existem"""
    print("\n🔍 Verificando arquivos de configuração...")
    
    arquivos = {
        "config/settings.json": "Configurações (obrigatório)",
        "requirements.txt": "Dependências (obrigatório)",
        "README.md": "Documentação",
        "QUICKSTART.md": "Guia rápido",
        ".gitignore": "Git ignore"
    }
    
    todas_ok = True
    
    for arquivo, descricao in arquivos.items():
        caminho = Path(arquivo)
        if caminho.exists():
            print(f"   ✅ {arquivo} - OK ({descricao})")
        else:
            print(f"   ⚠️  {arquivo} - NÃO ENCONTRADO ({descricao})")
            if "obrigatório" in descricao:
                todas_ok = False
    
    return todas_ok


def verificar_credenciais_monday():
    """Verifica se as credenciais do Monday estão configuradas"""
    print("\n🔍 Verificando configuração Monday...")
    
    try:
        import json
        
        with open("config/settings.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        api_key = config.get("monday_api_key", "").strip()
        board_id = config.get("monday_board_id", "").strip()
        
        if api_key == "YOUR_MONDAY_API_KEY_HERE" or not api_key:
            print("   ⚠️  Monday API Key - NÃO CONFIGURADA")
            print("      (Automação funcionará em modo offline)")
        else:
            print("   ✅ Monday API Key - CONFIGURADA")
        
        if board_id == "YOUR_BOARD_ID_HERE" or not board_id:
            print("   ⚠️  Monday Board ID - NÃO CONFIGURADO")
        else:
            print("   ✅ Monday Board ID - CONFIGURADO")
        
        return True
        
    except FileNotFoundError:
        print("   ❌ config/settings.json não encontrado")
        return False
    except json.JSONDecodeError:
        print("   ❌ config/settings.json contém JSON inválido")
        return False
    except Exception as e:
        print(f"   ❌ Erro ao verificar configuração: {str(e)}")
        return False


def main():
    """Executa todas as verificações"""
    print("\n" + "="*60)
    print("VALIDAÇÃO DE INSTALAÇÃO - OCR LEITOR")
    print("="*60)
    
    resultados = {
        "Python": verificar_python(),
        "Dependências": verificar_dependencias(),
        "Tesseract OCR": verificar_tesseract(),
        "Estrutura Pastas": verificar_estrutura_pastas(),
        "Arquivos Config": verificar_arquivos_config(),
        "Monday": verificar_credenciais_monday()
    }
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    
    obrigatorios = ["Python", "Dependências", "Tesseract OCR", "Estrutura Pastas"]
    
    for item, ok in resultados.items():
        status = "✅ OK" if ok else "❌ ERRO"
        obrigatorio = " (obrigatório)" if item in obrigatorios else ""
        print(f"{item:.<40} {status}{obrigatorio}")
    
    # Verificar se pode continuar
    print("\n" + "="*60)
    
    if all(resultados[item] for item in obrigatorios):
        print("✅ INSTALAÇÃO VÁLIDA - Pronto para usar!")
        print("\nExecute: python -m src.main")
        return 0
    else:
        print("❌ INSTALAÇÃO INCOMPLETA")
        print("Por favor, resolva os erros acima antes de continuar.")
        return 1
    
    print("="*60 + "\n")


if __name__ == "__main__":
    sys.exit(main())
