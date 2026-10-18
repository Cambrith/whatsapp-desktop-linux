"""Regressions for executable KDE launchers generated for the pinned badge."""
import ast
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


class LauncherPermissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.tree = ast.parse((cls.root / "bin" / "whatsapp").read_text())
        cls.functions = {
            node.name: node for node in ast.walk(cls.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def test_helper_marks_desktop_file_executable(self):
        helper = self.functions["ensure_desktop_launcher_executable"]
        module = ast.Module(body=[helper], type_ignores=[])
        namespace = {"os": os}
        exec(compile(module, "bin/whatsapp", "exec"), namespace)
        with tempfile.TemporaryDirectory() as directory:
            launcher = Path(directory) / "whatsapp.desktop"
            launcher.write_text("[Desktop Entry]\nType=Application\n")
            namespace["ensure_desktop_launcher_executable"](launcher)
            self.assertTrue(stat.S_IMODE(launcher.stat().st_mode) & stat.S_IXUSR)

    def test_badge_update_marks_both_badged_and_base_launchers_executable(self):
        update = self.functions["update_pinned_panel_badge"]
        calls_helper = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "ensure_desktop_launcher_executable"
            for node in ast.walk(update)
        )
        self.assertTrue(calls_helper)

    def test_installer_marks_desktop_entries_executable(self):
        installer = (self.root / "install.sh").read_text()
        self.assertIn('chmod +x "$APP_DIR/whatsapp.desktop" "$APP_DIR/zapzap.desktop"', installer)

    def test_permission_repair_catches_shortcut_created_by_an_old_running_instance(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            icons = home / ".local/share/plasma_icons"
            apps = home / ".local/share/applications"
            icons.mkdir(parents=True)
            apps.mkdir(parents=True)
            badge = icons / "com.rtosta.zapzap-badge-17.desktop"
            badge.write_text("[Desktop Entry]\nType=Application\n")
            badge.chmod(0o644)
            env = os.environ.copy()
            env["HOME"] = str(home)
            subprocess.run([self.root / "bin/fix-panel-launcher-permissions"], check=True, env=env)
            self.assertTrue(badge.stat().st_mode & stat.S_IXUSR)

    def test_systemd_monitor_is_installed_and_removed_with_the_app(self):
        path_unit = (self.root / "systemd/whatsapp-panel-launcher-permissions.path").read_text()
        installer = (self.root / "install.sh").read_text()
        uninstaller = (self.root / "uninstall.sh").read_text()
        self.assertIn("PathChanged=%h/.local/share/plasma_icons", path_unit)
        self.assertIn("enable --now whatsapp-panel-launcher-permissions.path", installer)
        self.assertIn("disable --now whatsapp-panel-launcher-permissions.path", uninstaller)


if __name__ == "__main__":
    unittest.main()
