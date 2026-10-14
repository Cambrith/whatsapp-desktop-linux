# WhatsApp Desktop para Linux (Edição Otimizada em Português)

<div align="center">

![WhatsApp Linux](icons/whatsapp.svg)

**Cliente Desktop do WhatsApp para distribuições Linux com tradução completa para o Português do Brasil (pt-BR), integração nativa com o sistema, badge dinâmico de notificações e renderização vetorial de alta definição sem distorções.**

[![Linux](https://img.shields.io/badge/Plataforma-Linux-FCC624?logo=linux&logoColor=black)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](#)
[![PyQt6](https://img.shields.io/badge/Interface-PyQt6-41CD52?logo=qt&logoColor=white)](#)
[![Licença](https://img.shields.io/badge/Licen%C3%A7a-GPLv3-blue.svg)](LICENSE)

</div>

---

## 🌟 Principais Recursos

- 🇧🇷 **Tradução Massiva para Português do Brasil (pt-BR)**:
  - **Interface Nativa**: Menus da barra de ferramentas, janelas de configurações, abas, diálogos de atalhos e tooltips totalmente traduzidos.
  - **WhatsApp Web (DOM / Navegador)**: Injeção de locale nativo no `DocumentCreation` e tradutor contínuo no `DocumentReady`, traduzindo campos de busca, abas de filtro, menus de contexto, rodapés de criptografia e botões.
- 🎨 **Ícones Vetoriais Otimizados e Nítidos**:
  - **Janela principal**: Sem barra de título e sem a barra de menus; a interface começa diretamente no conteúdo do aplicativo. Os atalhos continuam disponíveis. A conta selecionada tem fundo discreto, sem contorno verde.
  - **Bandeja do Sistema (Systray)**: Contador vermelho compacto no canto inferior direito, número branco em negrito e borda fina. O logo mantém seu tamanho e centro quando chegam mensagens.
  - **Barra de Tarefas / Dock**: Mesmo logo, sempre sem contador. A contagem de mensagens fica somente na bandeja, respeitando a preferência de contador do ZapZap.
- 🚫 **Livre de Distrações**:
  - Remoção completa de banners e telas de solicitação de apoio/doação do backend ZapZap.
  - Rebranding 100% limpo com nome oficial "WhatsApp".
- ⚡ **Desempenho e Leveza**:
  - Renderização direta via `QSvgRenderer` com *super-sampling* 4x em memória, garantindo bordas suaves e anti-aliasing de nível gráfico profissional.

---

## 📋 Pré-requisitos

Para executar este projeto, certifique-se de que sua distribuição possui o Python e o pacote base do ZapZap instalados:

### No Arch Linux / Manjaro:
```bash
sudo pacman -S python python-pyqt6 python-pyqt6-webengine
paru -S zapzap
```

### No Ubuntu / Debian / Pop!_OS:
```bash
sudo apt update
sudo apt install python3 python3-pyqt6 python3-pyqt6.qtwebengine
# Certifique-se de ter o pacote zapzap instalado via repositório ou flatpak
```

### No Fedora:
```bash
sudo dnf install python3 python3-qt6 python3-qt6-webengine
```

---

## 🚀 Instalação Rápida

Clone o repositório e execute o instalador automatizado:

```bash
git clone https://github.com/Cambrith/whatsapp-desktop-linux.git
cd whatsapp-desktop-linux
./install.sh
```

O script cuidará de:
1. Copiar o executável otimizado para `~/.local/bin/whatsapp`.
2. Instalar os ícones vetoriais em `~/.local/share/icons/`.
3. Criar e registrar o atalho `whatsapp.desktop` em `~/.local/share/applications/`.
4. Atualizar os bancos de dados de ícones e aplicativos do seu ambiente gráfico (KDE Plasma, GNOME, XFCE, etc.).

---

## 💻 Como Usar

- **Pelo Menu de Aplicativos**: Procure por **WhatsApp** no menu Iniciar/Kickoff.
- **Pelo Terminal**: Execute:
  ```bash
  whatsapp
  ```

---

## 📂 Estrutura do Repositório

```text
whatsapp-desktop-linux/
├── bin/
│   └── whatsapp                # Script executável do launcher com os patches
├── desktop/
│   └── whatsapp.desktop        # Entrada de aplicativo .desktop do padrão FreeDesktop
├── icons/
│   ├── whatsapp.svg            # Ícone vetorial oficial
│   └── whatsapp-window.svg     # Mesmo logo, mantido para compatibilidade
├── install.sh                  # Script de instalação automatizada
├── uninstall.sh                # Script de desinstalação
├── LICENSE                     # Licença GNU General Public License v3.0
└── README.md                   # Documentação do projeto
```

---

## 🗑️ Desinstalação

Caso queira remover as configurações instaladas:

```bash
./uninstall.sh
```

---

## 📄 Licença

Distribuído sob a licença [GPL-3.0](LICENSE). Consulte o arquivo `LICENSE` para mais informações.

## Verificação dos ícones

Com as dependências do aplicativo instaladas, execute:

```bash
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -v
```

Os testes verificam margens transparentes, contadores na bandeja, ausência de contador
na janela/barra de tarefas e o carregamento do SVG a partir do checkout.
A janela principal não exibe decoração nem barra de menus. No KDE, use `Alt+F4`
para fechar, a barra de tarefas para minimizar/restaurar e `Ctrl+P` para as
configurações do aplicativo.
