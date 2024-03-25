import subprocess
import sys


def install_fitz():
    """Install all required dependencies for the program"""

    print("Checking for all required dependencies")

    def check_and_install_package(package_name, import_name=None):
        if import_name is None:
            import_name = package_name
        try:
            __import__(import_name)
            print(f"{import_name} module is already installed.")
        except ImportError:
            print(f"{import_name} module not found, installing {package_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

    check_and_install_package("pymupdf", "fitz")
    check_and_install_package("pypdf")

    print("All required dependencies have been installed")
