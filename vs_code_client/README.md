# TMScript VS Code Client

This folder contains a minimal VS Code extension that starts your Python language server (pygls) over stdio.

## What it does

- Registers tmscript language for .tmss files.
- Launches the server with:
  - Working directory: auto-detected server root
  - Command: <python> -m src.main
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

Use this flow:

1. npm install
2. npm run vscode:prepublish
3. npx @vscode/vsce package

The generated VSIX then contains both client and server in one extension.

Runtime requirement: users still need Python installed (unless you later replace python -m startup with a bundled executable).

## Settings

- tmscriptLsp.pythonPath: explicit Python executable path.
- tmscriptLsp.serverRoot: path to server root.
- tmscriptLsp.serverModule: Python module to run (defaults to src.main).
- tmscriptLsp.trace.server: LSP trace verbosity.
