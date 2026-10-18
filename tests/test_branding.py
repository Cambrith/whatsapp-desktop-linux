"""O nome original não deve escapar pelas traduções da interface."""
import re
import textwrap
import unittest
from pathlib import Path

from PyQt6.QtCore import QTranslator


class BrandingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        source = (root / "bin" / "whatsapp").read_text(encoding="utf-8")
        start = source.index("    # Substitui o nome original")
        end = source.index("    # 2. Dicionário massivo")
        namespace = {"re": re, "QTranslator": QTranslator}
        exec(compile(textwrap.dedent(source[start:end]), "branding", "exec"), namespace)
        cls.clean_brand_text = staticmethod(namespace["clean_brand_text"])
        cls.translator = namespace["_brand_translator"]

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


if __name__ == "__main__":
    unittest.main()
