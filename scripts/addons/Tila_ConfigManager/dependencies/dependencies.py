import subprocess
import sys
import os
import importlib.util
from importlib import resources
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError
from packaging.requirements import Requirement

# from https://github.com/CGCookie/install_deps_example/blob/main/dependencies.py

module_path = Path(__file__).parent.parent
requirements_txt = module_path / "requirements.txt"
site_package_path = module_path / "site_package"

sys.path.append(os.fspath(site_package_path))


class Dependencies:
    _checked = None
    _requirements = None

    @staticmethod
    def is_package_installed(package_name: str) -> bool:
        """Check if a package in installed in the current environment"""

        req = Requirement(package_name)

        try:
            installed_version = version(req.name)
        except PackageNotFoundError:
            return False

        if req.specifier:
            return installed_version in req.specifier

        return True

    @staticmethod
    def is_module_exists(module_name: str) -> bool:
        """Check if a module exists in the current environment"""
        spam_spec = importlib.util.find_spec(module_name)
        return spam_spec is not None

    @staticmethod
    def run_powershell(cmd: str):
        """Run powershell command with the proper execution policy"""
        completed = subprocess.run(["powershell", "-ExecutionPolicy", "ByPass", "-Command", cmd], capture_output=True)
        return completed

    @staticmethod
    def ensure_uv_installed(module_path: Path) -> Path:
        """Install uv on a subfolder of module_path if it does not exists"""
        install_path = module_path / "uv"
        uv_path = install_path / "uv.exe"
        if not uv_path.exists():
            if not install_path.exists():
                os.makedirs(str(install_path), exist_ok=True)

            command = r"$env:UV_INSTALL_DIR = '{}'; irm https://astral.sh/uv/install.ps1 | iex".format(
                str(install_path)
            )

            print(f"installing UV in {str(install_path)}")
            Dependencies.run_powershell(command)

        return uv_path

    @staticmethod
    def install():
        if Dependencies.check():
            return True

        # Create folder into which pip will install dependencies
        try:
            site_package_path.mkdir(exist_ok=True)
        except Exception as e:
            print(f"Caught Exception while trying to create dependencies folder")
            print(f"  Exception: {e}")
            print(f"  Folder: {site_package_path}")
            return False

        # Ensure pip is installed
        try:
            subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
        except subprocess.CalledProcessError as e:
            print(f"Caught CalledProcessError while trying to ensure pip is installed")
            print(f"  Exception: {e}")
            print(f"  {sys.executable=}")
            return False

        # Install dependencies from requirements.txt
        try:
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                os.fspath(requirements_txt),
                "--target",
                os.fspath(site_package_path),
            ]
            print(f"Installing: {cmd}")
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            print(f"Caught CalledProcessError while trying to install dependencies")
            print(f"  Exception: {e}")
            print(f"  Requirements: {requirements_txt}")
            print(f"  Folder: {site_package_path}")
            return False

        return Dependencies.check(force=True)

    @staticmethod
    def check(*, force=False):
        if force:
            Dependencies._checked = None
        elif Dependencies._checked is not None:
            # Assume everything is installed
            return Dependencies._checked

        Dependencies._checked = False

        if site_package_path.exists():
            try:
                # Ensure all required dependencies are installed in dependencies folder
                if len(Dependencies.requirements(force=force)):
                    return False

                # If we get here, we found all required dependencies
                Dependencies._checked = True

            except Exception as e:
                print(f"Caught Exception while trying to check dependencies")
                print(f"  Exception: {e}")

        return Dependencies._checked

    @staticmethod
    def requirements(*, force=False):
        if force:
            Dependencies._requirements = None
        elif Dependencies._requirements is not None:
            return Dependencies._requirements

        missing = []
        # load and cache requirements
        with requirements_txt.open() as requirements:
            for line in requirements:
                if not line or line.startswith("#"):
                    continue

                if not Dependencies.is_package_installed(line):
                    missing.append(line)
            Dependencies._requirements = missing
        return Dependencies._requirements

