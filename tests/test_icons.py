"""Renderização real em Qt, sem iniciar WhatsApp Web ou acessar conversas."""
import os
import textwrap
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt, QRectF, QSize
from PyQt6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "bin" / "whatsapp"


def load_icons():
    source = SOURCE.read_text()
    block = textwrap.dedent(source[source.index("    # 3. Ícones oficiais"):
                                    source.index("    # 4. Barra de título própria")])
    namespace = {"os": os, "__file__": str(SOURCE),
                 "QApplication": QApplication, "QIcon": QIcon, "QPixmap": QPixmap,
                 "QPainter": QPainter, "QRectF": QRectF, "QSvgRenderer": QSvgRenderer,
                 "QSize": QSize}
    exec(compile(block, str(SOURCE), "exec"), namespace)
    return namespace


class IconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A aplicação existe antes do patch; não se abre nenhuma janela.
        cls.app = QApplication.instance() or QApplication([])
        cls.icons = load_icons()

    def test_window_logo_is_centered_and_fits_inside_its_square(self):
        for size in (16, 20, 22):
            with self.subTest(size=size):
                image = self.icons["render_whatsapp_window_pixmap"](size).toImage()
                points = [(x, y) for x in range(size) for y in range(size)
                          if image.pixelColor(x, y).alpha() > 16]
                self.assertTrue(points)
                left = min(x for x, _ in points)
                right = size - 1 - max(x for x, _ in points)
                self.assertLessEqual(abs(left - right), 1)
                top = min(y for _, y in points)
                bottom = size - 1 - max(y for _, y in points)
                self.assertLessEqual(abs(top - bottom), 1)
                for pos in range(size):
                    for x, y in ((0, pos), (size-1, pos), (pos, 0), (pos, size-1)):
                        self.assertEqual(image.pixelColor(x, y).alpha(), 0)

    def test_window_icon_uses_the_same_proportional_logo_at_every_size(self):
        for size in (24, 32, 48, 64, 128, 256):
            image = self.icons["render_whatsapp_window_pixmap"](size).toImage()
            self.assertEqual(image.width(), size)
            self.assertEqual(image.height(), size)
            self.assertGreater(image.pixelColor(size // 2, size // 2).alpha(), 0)

    def test_counts_do_not_change_the_window_icon(self):
        for size in (16, 20, 22, 24, 32, 48, 64):
            clean = self.icons["create_whatsapp_clean_icon"]().pixmap(size).toImage()
            for count in (0, 1, 3, 12, 99, 100):
                self.assertEqual(self.icons["create_whatsapp_window_icon"](count).pixmap(size).toImage(), clean)

    def test_tray_counter_is_red_and_bottom_right(self):
        for count in (1, 3, 12, 99, 100):
            image = self.icons["create_whatsapp_tray_icon"](count).pixmap(64).toImage()
            red = [(x, y) for x in range(64) for y in range(64)
                   if (color := image.pixelColor(x, y)).alpha() > 128
                   and color.red() > 150 and color.green() < 100 and color.blue() < 100]
            self.assertTrue(red)
            self.assertGreater(min(y for _, y in red), 32)
            self.assertGreater(sum(x for x, _ in red) / len(red), 32)

    def test_counter_setting_and_native_badge(self):
        class Tray:
            def hide(self):
                self.hidden = True
        manager = SimpleNamespace(_settings=SimpleNamespace(notification_counter_enabled=True), _tray=Tray())
        from zapzap.features.tray.sys_tray_manager import SysTrayManager
        theme = self.icons["TrayIcon"].Type.Default
        if hasattr(QApplication, "setBadgeNumber"):
            with patch.object(QApplication, "setBadgeNumber") as badge:
                SysTrayManager._set_icon(manager, theme, 12)
                badge.assert_called_once_with(0)
        else:
            SysTrayManager._set_icon(manager, theme, 12)
        self.assertEqual(manager.current_icon, theme)
        manager._settings.notification_counter_enabled = False
        SysTrayManager._set_icon(manager, theme, 12)
        self.assertTrue(manager._tray.hidden)

    def test_missing_renderer_produces_transparent_pixels(self):
        with patch.dict(self.icons, {"OFFICIAL_WHATSAPP_SVG": "", "_svg_renderer": None}):
            for name in ("render_whatsapp_pixmap", "render_whatsapp_window_pixmap"):
                image = self.icons[name](16).toImage()
                self.assertTrue(all(image.pixelColor(x, y).alpha() == 0
                                    for x in range(16) for y in range(16)))

    def test_checkout_svg_fallback(self):
        real_open = open
        def source_open(path, *args, **kwargs):
            if str(path).startswith(os.path.expanduser("~/.local/share/icons/")):
                raise FileNotFoundError(path)
            return real_open(path, *args, **kwargs)
        with patch("builtins.open", side_effect=source_open):
            icons = load_icons()
        self.assertTrue(icons["get_svg_renderer"]().isValid())

    def test_window_icon_uses_the_same_logo_as_the_panel(self):
        icon = self.icons["create_whatsapp_clean_icon"]()
        image = icon.pixmap(QSize(48, 48)).toImage()
        self.assertFalse(icon.isNull())
        self.assertGreater(image.pixelColor(24, 24).alpha(), 0)


if __name__ == "__main__":
    unittest.main()
