# TMScript LSP Developer Guide

This is a short guide for local development of the Python LSP server and VS Code extension.

## Requirements

- Python 3.11+ (recommended)
- Node.js 18+ (recommended)
- npm
- VS Code

Optional but used in release flow:

- PyInstaller (for building Windows executable server)
- `@vscode/vsce` (for packaging the extension)

## Development Setup

### 1) Set up Python server environment

From repository root:

```powershell
cd server
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

### 2) Set up VS Code extension environment

From repository root:

```powershell
cd vs_code_client
npm install
npm run build
```

### 3) Run in development

- Build extension TypeScript: `npm run build` in `vs_code_client`
- Launch Extension Development Host from VS Code
- Open a `.tms` file to activate the extension

## Testing

Unit tests are under `server/tests/unit/`.

Run tests:

```powershell
cd server
.\.venv\Scripts\Activate.ps1
python -m pytest tests\unit
```

Debug scripts (optional):

- `server/tests/debug/diagnostic_test.py`
- `server/tests/debug/user_variables.py`

## Deployment

The project deploy flow is script-based and centered around `server/deploy.py`.

From repository root:

```powershell
cd server
.\.venv\Scripts\Activate.ps1
python deploy.py
```

What this does:


1. Builds server executable with PyInstaller.
2. Copies server artifact into the extension server bundle area.
3. Builds the VS Code extension.
4. Packages a `.vsix` into `vs_code_client/release/`.

Related files:

- `server/deploy.py`
- `vs_code_client/scripts/sync-server.mjs`

## Quick Troubleshooting

- If tests fail with import errors, run them from `server/` and ensure the virtual environment is activated.
- If extension changes are not visible, rebuild with `npm run build` in `vs_code_client`.
- If server launch fails in VS Code, check extension settings for `tmscriptLsp.serverRoot` and `tmscriptLsp.pythonPath`.

