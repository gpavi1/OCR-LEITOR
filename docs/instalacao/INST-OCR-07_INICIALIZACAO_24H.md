# INST-OCR-07 — Inicialização Controlada 24h

## 1. Objetivo

Esta fase define uma forma segura de iniciar o OCR-LEITOR em uma máquina responsável, mantendo o painel web local disponível para operação controlada.

O foco é operação local, sem exposição de rede, sem serviço Windows automático e sem automação perigosa.

## 2. Modelo operacional recomendado

- Uma máquina responsável por cliente
- OCR-LEITOR instalado localmente
- MySQL ativo na mesma máquina
- Painel web local acessível via navegador
- Operador acessa e revisa documentos
- OCR gera dados/JSON validados
- FechaMes permanece separado (sem integração nesta fase)
- Sem API pública nesta fase

## 3. Atalho criado

`INICIAR_OCR_24H_LOCAL.bat`

Este atalho inicia o painel local com Waitress em:

```
http://127.0.0.1:5000
```

## 4. O que o atalho faz

1. Valida se o Python da `.venv` existe
2. Valida se `web/app.py` existe
3. Exibe o endereço do painel local
4. Inicia o Waitress local com `127.0.0.1:5000`
5. Mantém a execução visível no console
6. Permite encerramento manual fechando o terminal ou com Ctrl+C

## 5. O que o atalho não faz

- Não instala dependências
- Não cria banco
- Não executa migração
- Não cria serviço Windows
- Não cria tarefa agendada
- Não abre acesso público
- Não usa `0.0.0.0`
- Não mexe no FechaMes
- Não executa integração real

## 6. Por que usar 127.0.0.1 nesta fase

O endereço `127.0.0.1` (localhost) limita o acesso à própria máquina. Isso evita exposição indevida do painel antes de uma fase específica de configuração de rede interna.

Nenhuma outra máquina na rede consegue acessar o painel enquanto ele estiver rodando em `127.0.0.1`.

## 7. Operação 24h controlada

Para operação piloto 24h:

- A máquina precisa ficar ligada
- MySQL precisa estar ativo
- O terminal do OCR precisa permanecer aberto
- O operador deve monitorar o painel
- Logs e erros devem ser acompanhados
- Reinício deve ser manual nesta fase

Para reiniciar:

1. Fechar o terminal atual (ou Ctrl+C)
2. Executar `INICIAR_OCR_24H_LOCAL.bat` novamente

## 8. Evolução futura

Fases futuras podem criar:

- Modo rede interna controlado (liberação gradual)
- Serviço Windows para inicialização automática
- Tarefa agendada para reinício programado
- Monitoramento de integridade e alertas
- Reinício automático em falha

Nada disso faz parte desta fase.

## 9. Critérios de aprovação

- `.venv` local existe
- Dependências instaladas
- `scripts/doctor_instalacao.py` executa sem erro crítico
- `pytest` passa
- Waitress inicia sem erro
- Painel abre em `http://127.0.0.1:5000`
- Nenhum acesso externo indevido
- FechaMes intacto

## 10. Comando manual equivalente

```powershell
.\.venv\Scripts\python.exe -m waitress --listen=127.0.0.1:5000 web.app:app
```

Pode ser executado diretamente no terminal para testar sem o atalho.
