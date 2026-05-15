# TMScript for VS Code

TMScript for VS Code adds language support for TMS files.

## What You Get

- Language server powered editing for .tms files
- Autocomplete for keywords, script functions, types, and user-defined variables
- Diagnostics while you type

## Quick Start

1. Install TMScript for VS Code from the Extensions view.
2. Open a folder that contains TMS files.
3. Open any file ending in .tms.
4. Start typing to see completions and diagnostics.

## Requirements

- Python must be installed and available on your machine.
- The extension will try to find Python automatically.

## Extension Settings

You can configure these settings from VS Code Settings:

- tmscriptLsp.pythonPath: Path to a specific Python executable.
- tmscriptLsp.serverRoot: Optional override for the server folder.
- tmscriptLsp.serverModule: Python module to run. Default is src.main.
- tmscriptLsp.trace.server: LSP trace level (off, messages, verbose).

## Troubleshooting

- If language features do not appear, reload the VS Code window.
- If server startup fails, set tmscriptLsp.pythonPath explicitly.
- Open the Output panel and choose TMScript LSP to inspect logs.

## Feedback

For issues and feature requests, use the project issue tracker.
For contributor setup and publishing steps, see [README.developers.md](README.developers.md).
