# TMScript VS Code Client

This folder contains a minimal VS Code extension that starts your Python language server (pygls) over stdio.

## What it does

- Registers tmscript language for .tms files.
- Launches the server with:
  - Executable first: bundled server binary when available
  - Fallback: <python> -m src.main
- Connects via `vscode-languageclient`.

Server root auto-detection order:

- tmscriptLsp.serverRoot setting (if provided)
- bundled extension server folder (for published extension)
- sibling ../server (fallback for local dev)
- <workspace>/server when available (development fallback)

Python auto-detection order:

- tmscriptLsp.pythonPath setting (if provided)
- server/.venv or server/venv interpreter
- python on PATH

Executable auto-detection order:

- tmscriptLsp.serverExecutablePath setting (if provided)
- server/bin/win32/tmscript-lsp-server.exe on Windows
- server/bin/darwin/tmscript-lsp-server on macOS
- server/bin/linux/tmscript-lsp-server on Linux
- server/dist/main(.exe) fallback

## Run locally

1. Open this repository in VS Code.
2. In vs_code_client/, install dependencies:

```bash
npm install
```

3. Build the extension:

```bash
npm run build
```

4. Press F5 with the Run TMScript Client launch config.

## Marketplace packaging note

This project includes a prepublish sync step that copies ../server/src into vs_code_client/server/src before packaging.
If ../server/dist/main.exe exists, it is also copied to vs_code_client/server/bin/win32/tmscript-lsp-server.exe.

Use this flow:

1. npm install
2. npm run vscode:prepublish
3. npx @vscode/vsce package

The generated VSIX then contains both client and server in one extension.

Runtime requirement: users still need Python installed (unless you later replace python -m startup with a bundled executable).

## Settings

- tmscriptLsp.pythonPath: explicit Python executable path.
- tmscriptLsp.serverExecutablePath: explicit server executable path.
- tmscriptLsp.serverRoot: path to server root.
- tmscriptLsp.serverModule: Python module to run (defaults to src.main).
- tmscriptLsp.trace.server: LSP trace verbosity.
