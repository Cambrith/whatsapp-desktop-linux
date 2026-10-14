#!/usr/bin/env bash
# ==============================================================================
# Desinstalador do WhatsApp Desktop Linux (pt-BR)
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================================${NC}"
echo -e "${RED}     Desinstalador do WhatsApp Desktop Linux (pt-BR)  ${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons"
APP_DIR="$HOME/.local/share/applications"

echo "Removendo binários e scripts..."
rm -f "$BIN_DIR/whatsapp" "$BIN_DIR/zapzap"

echo "Removendo ícones..."
rm -f "$ICON_DIR/whatsapp.svg" "$ICON_DIR/whatsapp-window.svg"

echo "Removendo atalhos desktop..."
rm -f "$APP_DIR/whatsapp.desktop" "$APP_DIR/zapzap.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APP_DIR" 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}✔ Desinstalação concluída com sucesso.${NC}"
