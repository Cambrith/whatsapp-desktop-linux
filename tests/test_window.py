"""Verifica a janela e os controles sem iniciar o navegador ou ler conversas."""
import os
import textwrap
import unittest
from pathlib import Path
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget
from PyQt6.QtGui import QIcon
QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)


class WindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        repo_root = Path(__file__).resolve().parents[1]
        source = (repo_root / "bin" / "whatsapp").read_text()
        block = source[source.index("    # 4. Barra de título própria"):source.index("    # 6. Scripts")]
        cls.namespace = {
            "Qt": Qt,
            "QHBoxLayout": QHBoxLayout,
            "QWidget": QWidget,
            "create_whatsapp_clean_icon": lambda: QIcon(str(repo_root / "icons" / "whatsapp.svg")),
        }
        exec(textwrap.dedent(block), cls.namespace)

    def test_main_window_hides_menubar_from_content_and_has_no_icon(self):
        view = self.namespace["MainWindowView"]()
        self.assertEqual(view.windowTitle(), "WhatsApp")
        self.assertTrue(view.menubar.isHidden())
        self.assertEqual(view.menubar.maximumHeight(), 0)
        view.retranslate_ui()
        self.assertTrue(view.menubar.isHidden())
        view.close()

    def test_shortcut_actions_remain_attached(self):
        view = self.namespace["MainWindowView"]()
        self.assertIn(view.actionSettings, view.actions())
        self.assertIn(view.actionQuit, view.actions())
        self.assertEqual(view.actionSettings.shortcut().toString(), "Ctrl+P")
        view.close()

    def test_client_side_titlebar_and_window_controls_are_visible(self):
        from zapzap.assets.themes.csr_button_theme_provider import CSRButtonTheme
        from unittest.mock import patch
        view = self.namespace["MainWindowView"]()
        cls = self.namespace["ClientSideWindow"]
        with patch.object(cls, "_resolve_button_theme", return_value=CSRButtonTheme.DEFAULT):
            host = cls(view)
        self.assertFalse(host.title_bar.isHidden())
        self.assertEqual(host.title_bar.title_label.text(), "WhatsApp")
        self.assertEqual(host.windowTitle(), "WhatsApp")
        self.assertEqual(view.menubar.parentWidget(), host.title_bar)
        self.assertFalse(view.menubar.isHidden())
        self.assertEqual(view.menubar.property("cambrithTitlebarMenu"), True)
        self.assertEqual(host.title_bar.title_label.alignment(), Qt.AlignmentFlag.AlignCenter)
        for button in (host.title_bar.minimize_button, host.title_bar.maximize_button, host.title_bar.close_button):
            self.assertFalse(button.isHidden())
        self.assertEqual(host.layout().contentsMargins().left(), 0)
        self.assertEqual(host.layout().contentsMargins().top(), 0)
        host.close()
