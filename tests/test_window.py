"""Verifica a janela e os controles sem iniciar o navegador ou ler conversas."""
import os
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QColorDialog
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
        self.assertIn("border: none", view.menubar.styleSheet())
        self.assertEqual(host.title_bar.title_label.alignment(), Qt.AlignmentFlag.AlignCenter)
        for button, name in (
            (host.title_bar.minimize_button, "Minimizar"),
            (host.title_bar.maximize_button, "Maximizar"),
            (host.title_bar.close_button, "Fechar"),
        ):
            self.assertTrue(button.text() == "")
            self.assertFalse(button.icon().isNull())
            self.assertEqual(button.accessibleName(), name)
        for button in (host.title_bar.minimize_button, host.title_bar.maximize_button, host.title_bar.close_button):
            self.assertFalse(button.isHidden())

        maximize_icon = host.title_bar.maximize_button.icon().pixmap(18, 18).toImage()
        host.showMaximized()
        self.app.processEvents()
        self.assertTrue(host.isMaximized())
        self.assertEqual(host.title_bar.maximize_button.toolTip(), "Restaurar")
        restore_icon = host.title_bar.maximize_button.icon().pixmap(18, 18).toImage()
        self.assertNotEqual(maximize_icon, restore_icon)
        host.showNormal()
        self.app.processEvents()
        self.assertEqual(host.title_bar.maximize_button.toolTip(), "Maximizar")

        from zapzap.core.config.settings_manager import SettingsManager
        options = {
            "window/titlebar_separator/enabled": True,
            "window/titlebar_separator/thickness": 1,
            "window/titlebar_separator/width_percent": 100,
            "window/titlebar_separator/color": "#123456",
        }
        with patch.object(SettingsManager, "get",
                          side_effect=lambda key, default=None: options.get(key, default)):
            bar_image = host.title_bar.grab().toImage()
            left_separator = bar_image.pixelColor(0, bar_image.height() - 1)
            right_separator = bar_image.pixelColor(bar_image.width() - 1, bar_image.height() - 1)
            self.assertEqual(left_separator.name(), "#123456")
            self.assertEqual(right_separator, left_separator)

            options["window/titlebar_separator/enabled"] = False
            host.title_bar.update()
            self.app.processEvents()
            disabled_image = host.title_bar.grab().toImage()
            background = host.title_bar.palette().color(QPalette.ColorRole.Window)
            self.assertEqual(disabled_image.pixelColor(
                disabled_image.width() // 2, disabled_image.height() - 1), background)

            options["window/titlebar_separator/enabled"] = True
            options["window/titlebar_separator/thickness"] = 3
            options["window/titlebar_separator/width_percent"] = 50
            host.title_bar.update()
            self.app.processEvents()
            customized_image = host.title_bar.grab().toImage()
            center_x = customized_image.width() // 2
            for y in range(customized_image.height() - 3, customized_image.height()):
                self.assertEqual(customized_image.pixelColor(center_x, y).name(), "#123456")
            self.assertEqual(customized_image.pixelColor(2, customized_image.height() - 1), background)

        self.assertEqual(host.layout().contentsMargins().left(), 0)
        self.assertEqual(host.layout().contentsMargins().top(), 0)
        host.close()

    def test_appearance_settings_can_customize_and_persist_separator(self):
        from zapzap.core.config.settings_manager import SettingsManager
        controller_class = self.namespace["AppearanceSettingsController"]
        values = {}
        with patch.object(SettingsManager, "get",
                          side_effect=lambda key, default=None: values.get(key, default)), \
                patch.object(SettingsManager, "set",
                              side_effect=lambda key, value: values.__setitem__(key, value)):
            controller = controller_class()
            self.assertEqual(controller.titlebar_separator_thickness_row.combo.count(), 6)
            self.assertEqual(controller.titlebar_separator_width_row.combo.count(), 19)
            self.assertTrue(controller.titlebar_separator_enabled_row.checkbox.isChecked())

            controller.titlebar_separator_enabled_row.checkbox.setChecked(False)
            self.assertIs(values["window/titlebar_separator/enabled"], False)
            controller.titlebar_separator_enabled_row.checkbox.setChecked(True)
            thickness = controller.titlebar_separator_thickness_row.combo.findData(4)
            controller.titlebar_separator_thickness_row.combo.setCurrentIndex(thickness)
            width = controller.titlebar_separator_width_row.combo.findData(65)
            controller.titlebar_separator_width_row.combo.setCurrentIndex(width)
            with patch.object(QColorDialog, "getColor", return_value=QColor("#0f6abd")):
                controller.titlebar_separator_color_row.button.click()
            self.assertEqual(values["window/titlebar_separator/color"], "#0f6abd")
            controller.titlebar_separator_reset_color_row.button.click()

            self.assertIs(values["window/titlebar_separator/enabled"], True)
            self.assertEqual(values["window/titlebar_separator/thickness"], 4)
            self.assertEqual(values["window/titlebar_separator/width_percent"], 65)
            self.assertEqual(values["window/titlebar_separator/color"], "auto")
            controller.close()
