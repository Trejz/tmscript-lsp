import os
from pathlib import Path
import subprocess
import shutil
import json

os.chdir(Path(__file__).parent)
main_dir = Path(__file__).parent.parent

with open(f"{main_dir}/vs_code_client/package.json") as f:
    data = json.load(f)
    version = data.get("version", "")
    name = data.get("name", "")

vsix_file = f"{name}-{version}.vsix"

def clean_output_directory(directory: str):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)


def create_exe():
    subprocess.run("""pyinstaller --onefile src/main.py --add-data "src/server/assets;assets" """)


def copy_exe():
    # Copy exe to vs_code_extensions
    src: str = os.path.join("dist", "main.exe")
    dst: str = os.path.join(main_dir, "vs_code_client", "server", "tmscript-lsp-server.exe")
    shutil.copy(src, dst)


def create_vscode_extension():
    extension_dir = os.path.join(main_dir, "vs_code_client")
    os.chdir(extension_dir)

    # Build TypeScript extension output.
    subprocess.run("""npm run build""", cwd=extension_dir, check=True, shell=True)

    extension_dir = os.path.join(main_dir, "vs_code_client")
    os.chdir(extension_dir)

    subprocess.run("""npx @vscode/vsce package --allow-missing-repository""", cwd=extension_dir, check=True, shell=True)

    src: str = os.path.join(extension_dir, vsix_file)
    dst: str = os.path.join(extension_dir, "release", vsix_file)

    shutil.move(src, dst)


def readme_changelog_copy():
    src: str = os.path.join(main_dir, "README.md")
    dst: str = os.path.join(main_dir, "vs_code_client", "README.md")
    shutil.copy(src, dst)

    src: str = os.path.join(main_dir, "CHANGELOG.md")
    dst: str = os.path.join(main_dir, "vs_code_client", "CHANGELOG.md")
    shutil.copy(src, dst)

    src: str = os.path.join(main_dir, "LICENSE.md")
    dst: str = os.path.join(main_dir, "vs_code_client", "LICENSE.md")
    shutil.copy(src, dst)

if __name__ == "__main__":
    # Create exe
    clean_output_directory("dist")
    create_exe()

    clean_output_directory(os.path.join(main_dir, "vs_code_client", "server"))
    copy_exe()

    # Build VS Code extension
    clean_output_directory(os.path.join(main_dir, "vs_code_client", "out"))
    clean_output_directory(os.path.join(main_dir, "vs_code_client", "release"))
    readme_changelog_copy()
    create_vscode_extension()
