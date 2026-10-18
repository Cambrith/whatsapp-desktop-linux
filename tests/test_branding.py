"""O nome original não deve escapar pelas traduções da interface."""
import re
import textwrap
import unittest
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import zipfile
from unittest.mock import patch

from PyQt6.QtCore import QTranslator


class BrandingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        source = (root / "bin" / "whatsapp").read_text(encoding="utf-8")
        start = source.index("    # Substitui o nome original")
        end = source.index("    # 2. Dicionário massivo")

        class FakeUiElement:
            def setWindowTitle(self, value):
                self.title = value

            def setText(self, value):
                self.text = value

            def setPlainText(self, value):
                self.text = value

            def isReadOnly(self):
                return True

        class FakeAction(FakeUiElement):
            pass

        class FakeTrayIcon(FakeUiElement):
            pass

        namespace = {"re": re, "QTranslator": QTranslator}
        namespace.update({
            "QWidget": FakeUiElement,
            "QLabel": FakeUiElement,
            "QAbstractButton": FakeUiElement,
            "QGroupBox": FakeUiElement,
            "QMenu": FakeUiElement,
            "QAction": FakeAction,
            "QSystemTrayIcon": FakeTrayIcon,
            "QTextEdit": FakeUiElement,
            "QPlainTextEdit": FakeUiElement,
        })
        exec(compile(textwrap.dedent(source[start:end]), "branding", "exec"), namespace)
        cls.clean_brand_text = staticmethod(namespace["clean_brand_text"])
        cls.translator = namespace["_brand_translator"]
        cls.fake_ui_element = FakeUiElement

    def test_translation_and_case_variants_use_whatsapp_brand(self):
        self.assertEqual(self.clean_brand_text("ZapZap Settings"), "WhatsApp Settings")
        self.assertEqual(self.clean_brand_text("welcome to zapzap"), "welcome to WhatsApp")
        self.assertEqual(self.translator.translate("test", "ZapZap"), "WhatsApp")

    def test_about_disclaimer_remains_accurate(self):
        source = "ZapZap is an independent project and is not affiliated with WhatsApp or Meta."
        result = self.clean_brand_text(source)
        self.assertNotIn("ZapZap", result)
        self.assertIn("não é afiliado", result)

    def test_upstream_project_references_are_not_presented_as_whatsapp_services(self):
        result = self.clean_brand_text("Official ZapZap website to download it")
        self.assertNotIn("ZapZap", result)
        self.assertNotIn("WhatsApp website", result)
        self.assertIn("página do aplicativo", result)

    def test_direct_native_window_and_widget_labels_are_sanitized(self):
        window = self.fake_ui_element()
        window.setWindowTitle("ZapZap — Quick access")
        self.assertEqual(window.title, "WhatsApp — Quick access")

        label = self.fake_ui_element()
        label.setText("ZapZap Settings")
        self.assertEqual(label.text, "WhatsApp Settings")

        report_preview = self.fake_ui_element()
        report_preview.setPlainText("ZapZap encountered a problem")
        self.assertEqual(report_preview.text, "WhatsApp encountered a problem")

    def test_customization_snapshot_is_private_deduplicated_and_updated(self):
        root = Path(__file__).resolve().parents[1]
        source = (root / "bin" / "whatsapp").read_text(encoding="utf-8")
        start = source.index("def preserve_user_customizations():")
        end = source.index("\n\npreserve_user_customizations()", start)
        namespace = {
            "Path": Path,
            "hashlib": hashlib,
            "json": json,
            "zipfile": zipfile,
            "datetime": datetime,
            "timezone": timezone,
            "__file__": "",
        }
        exec(compile(source[start:end], "customization_backup", "exec"), namespace)

        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temporary:
            home = Path(temporary)
            wrapper = home / ".local/bin/zapzap"
            preferences = home / ".config/WhatsApp/WhatsApp.conf"
            wrapper.parent.mkdir(parents=True)
            preferences.parent.mkdir(parents=True)
            wrapper.write_text("launcher customization", encoding="utf-8")
            preferences.write_text("separator_color=#123456", encoding="utf-8")
            namespace["__file__"] = str(wrapper)
            with patch.object(Path, "home", return_value=home):
                namespace["preserve_user_customizations"]()
                backup_dir = home / ".local/state/whatsapp-customizations/backups"
                backups = list(backup_dir.glob("*.zip"))
                self.assertEqual(len(backups), 1)
                with zipfile.ZipFile(backups[0]) as archive:
                    self.assertEqual(
                        archive.read(".config/WhatsApp/WhatsApp.conf").decode(),
                        "separator_color=#123456",
                    )

                namespace["preserve_user_customizations"]()
                self.assertEqual(len(list(backup_dir.glob("*.zip"))), 1)
                preferences.write_text("separator_color=#abcdef", encoding="utf-8")
                namespace["preserve_user_customizations"]()
                self.assertEqual(len(list(backup_dir.glob("*.zip"))), 2)


if __name__ == "__main__":
    unittest.main()
