# DIAG-OCR-01 - Auditoria Assistida da Extracao OCR/parser

## 1. Objetivo da fase

Criar uma ferramenta local de diagnostico para medir a qualidade da extracao atual do OCR-LEITOR com documentos reais, sem corrigir OCR/parser nesta fase.

## 2. O que o diagnostico faz

- Lê imagens privadas em `.jpg`, `.jpeg` e `.png`.
- Executa o OCR/parser atual apenas para diagnostico.
- Salva OCR bruto por arquivo.
- Salva JSON extraido por arquivo.
- Gera `relatorio_extracao.md`.
- Gera `relatorio_extracao.json`.
- Gera `comparativo_campos.csv`.
- Detecta campos ausentes, suspeitos e possiveis indicios ignorados pelo parser.

## 3. O que ele nao faz

- Nao corrige OCR/parser.
- Nao altera regras de extracao.
- Nao altera pipeline.
- Nao altera banco.
- Nao altera API.
- Nao altera UI.
- Nao envia arquivos para internet.

## 4. Como preparar amostras privadas

Use pastas locais ignoradas pelo Git:

```text
_amostras_privadas/ocr_real/imagens/
_amostras_privadas/ocr_real/esperado/
_amostras_privadas/ocr_real/relatorios/
```

Nao commitar documentos reais, imagens de cliente, JSON real de cliente ou relatorios com dados fiscais reais.

## 5. Como rodar sem gabarito

```bash
python scripts/auditar_extracao_ocr.py --amostras "_amostras_privadas/ocr_real/imagens" --saida "_amostras_privadas/ocr_real/relatorios"
```

## 6. Como rodar com gabarito

```bash
python scripts/auditar_extracao_ocr.py --amostras "_amostras_privadas/ocr_real/imagens" --esperado "_amostras_privadas/ocr_real/esperado" --saida "_amostras_privadas/ocr_real/relatorios"
```

Cada gabarito deve ter o mesmo nome base da imagem, por exemplo `nota1.jpeg` e `nota1.json`.

## 7. Como interpretar alertas

- `ausente`: campo nao foi extraido.
- `suspeito`: campo foi extraido, mas parece ruido ou termo generico.
- `encontrado_no_ocr_mas_nao_extraido`: o OCR bruto contem indicios que o parser atual nao aproveitou.
- `divergente_do_gabarito`: valor extraido difere do JSON esperado.

## 8. Como identificar problema de OCR bruto

O relatorio marca suspeita de OCR bruto quando ha pouco texto, muitos caracteres estranhos ou a imagem aparenta orientacao/recorte extremos. Nesse caso, a imagem ou o OCR pode ser a causa principal.

## 9. Como identificar problema de parser

Quando o OCR bruto contem dados como empresa, numero NF, datas ou valores, mas o JSON extraido fica vazio ou suspeito, a classificacao provavel aponta para parser.

## 10. Como identificar problema de imagem/orientacao

Alertas de proporcao de imagem, texto muito curto ou caracteres estranhos indicam possivel problema de qualidade, recorte ou orientacao.

## 11. Como usar o relatorio para planejar AJUSTE-OCR-01

Revise primeiro `relatorio_extracao.md` e `comparativo_campos.csv`. Agrupe os erros recorrentes por campo e por classificacao provavel. Somente depois disso abrir `AJUSTE-OCR-01` para correcoes cirurgicas.

## 12. Regras de seguranca para documentos reais

- DIAG-OCR-01 nao corrige OCR/parser.
- DIAG-OCR-01 so mede e relata.
- Ajustes so virao em `AJUSTE-OCR-01`.
- Documentos reais nao devem ser commitados.
- Relatorios com dados reais tambem nao devem ser commitados.
- Tudo deve permanecer local.
