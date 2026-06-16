# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto segue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-16

### Adicionado

- ✨ **Fase 1 - Leitor OCR**: Suporte para leitura de imagens (JPG, PNG, GIF, BMP) e PDFs
- ✨ **Fase 2 - Extrator de Campos**: Extração automática de empresa, NF-e, chave e vencimento
- ✨ **Fase 3 - Conferência Manual**: Tela de validação interativa para o usuário
- ✨ **Fase 4 - Integração Monday**: API GraphQL para criar items e atualizar colunas
- ✨ **Fase 5 - Processamento em Lote**: Automação completa de múltiplos arquivos
- 📁 Gerenciamento automático de pastas (entrada, processadas, erro)
- 📝 Sistema de logging detalhado com arquivos de log
- ⚙️ Configuração via JSON com padrões regex customizáveis
- 📱 Menu interativo com opções de operação
- 🔍 Pré-processamento de imagens para melhorar OCR
- ✅ Validação de campos extraídos
- 🛡️ Tratamento robusto de erros
- 📚 Documentação completa (README, QUICKSTART, examples)
- 🔐 Suporte a variáveis de ambiente para credenciais

### Tecnologias

- Python 3.8+
- Tesseract OCR 5.0+
- OpenCV 4.8+
- pdf2image 1.16+
- Pillow 10.1+
- Requests 2.31+

### Documentação

- ✅ README.md - Documentação completa
- ✅ QUICKSTART.md - Guia de 5 minutos
- ✅ examples.py - 12 exemplos práticos
- ✅ copilot-instructions.md - Instruções para IA
- ✅ verificar_instalacao.py - Validação de setup

### Estrutura

```
OCR-LEITOR/
├── src/
│   ├── main.py           # Orquestrador principal
│   ├── leitor.py         # Leitor OCR
│   ├── extrator.py       # Extrator de campos
│   ├── monday_api.py     # API Monday
│   ├── uploader.py       # Gerenciador de arquivos
│   └── __init__.py
├── config/
│   └── settings.json     # Configurações
├── entrada/              # Arquivos de entrada
├── processadas/          # Arquivos processados
├── erro/                 # Arquivos com erro
├── logs/                 # Logs de execução
├── requirements.txt      # Dependências
├── README.md             # Documentação
├── QUICKSTART.md         # Início rápido
├── examples.py           # Exemplos de uso
├── verificar_instalacao.py # Validador
├── LICENSE.md            # MIT License
└── .gitignore           # Git ignore
```

## Versões Futuras

### [1.1.0] - Planejado

- [ ] Suporte para múltiplos idiomas (inglês, espanhol, francês)
- [ ] Cache de configurações para melhor performance
- [ ] Dashboard web para visualizar processamentos
- [ ] Exportação de relatórios em Excel/PDF
- [ ] Suporte a webhooks do Monday
- [ ] API REST para integração externa

### [1.2.0] - Planejado

- [ ] Detecção automática de layouts de notas
- [ ] Machine Learning para melhor extração
- [ ] Sincronização automática de múltiplos boards
- [ ] Backup automático de arquivos
- [ ] Histórico de processamentos

### [2.0.0] - Visão

- [ ] Interface gráfica (Electron/Tkinter)
- [ ] Aplicação mobile
- [ ] Cloud storage integration
- [ ] AI-powered validation
- [ ] Multi-language support

---

## Como Contribuir

1. Faça um Fork do projeto
2. Crie uma Branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Suporte

Para reportar bugs ou sugerir features, abra uma issue ou entre em contato.

---

**Desenvolvido com ❤️ para automação local e gratuita**

Última atualização: 2026-06-16
