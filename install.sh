#!/usr/bin/env bash
# ==============================================================================
# Instalador do WhatsApp Desktop Linux (pt-BR)
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sem cor

echo -e "${BLUE}======================================================${NC}"
echo -e "${GREEN}      Instalador do WhatsApp Desktop Linux (pt-BR)    ${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons"
APP_DIR="$HOME/.local/share/applications"

# 1. Garantir diretórios necessários
echo -e "${BLUE}[1/5]${NC} Criando diretórios do usuário..."
mkdir -p "$BIN_DIR" "$ICON_DIR" "$APP_DIR"

# 2. Copiar executável
echo -e "${BLUE}[2/5]${NC} Instalando binário em $BIN_DIR..."
cp "$SCRIPT_DIR/bin/whatsapp" "$BIN_DIR/whatsapp"
chmod +x "$BIN_DIR/whatsapp"
# Criar link para zapzap para compatibilidade com chamadas existentes
ln -sf "$BIN_DIR/whatsapp" "$BIN_DIR/zapzap"

# 3. Copiar ícones
echo -e "${BLUE}[3/5]${NC} Instalando ícones em $ICON_DIR..."
cp "$SCRIPT_DIR/icons/whatsapp.svg" "$ICON_DIR/whatsapp.svg"
cp "$SCRIPT_DIR/icons/whatsapp-window.svg" "$ICON_DIR/whatsapp-window.svg"

# 4. Copiar atalho desktop
echo -e "${BLUE}[4/5]${NC} Instalando atalho de aplicativo em $APP_DIR..."
cp "$SCRIPT_DIR/desktop/whatsapp.desktop" "$APP_DIR/whatsapp.desktop"
cp "$SCRIPT_DIR/desktop/whatsapp.desktop" "$APP_DIR/zapzap.desktop"

# Inicialização automática (abre escondido na bandeja do sistema)
mkdir -p "$HOME/.config/autostart"
cp "$SCRIPT_DIR/desktop/whatsapp-autostart.desktop" "$HOME/.config/autostart/whatsapp.desktop"

# 5. Atualizar caches do sistema
echo -e "${BLUE}[5/5]${NC} Atualizando bancos de dados de desktop e ícones..."
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$ICON_DIR" 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}✔ Instalação concluída com sucesso!${NC}"
echo -e "Você já pode abrir o WhatsApp pelo menu de aplicativos ou executando ${YELLOW}whatsapp${NC} no terminal."
