# TMScript LSP

TMScript LSP is language support for the Techman Robot scripting language in Visual Studio Code.

It consists of:
- A Python Language Server Protocol (LSP) server.
- A VS Code extension client that starts and connects to that server.

The extension targets `.tms` files and provides core editing intelligence for TMScript.

## What It Does

Current capabilities include:

- Auto-completion for:
	- TMScript keywords
	- Built-in script functions
	- Built-in script types
	- User-defined variables from the current document
- Type-aware completion while assigning values:
	- Suggests functions that return a compatible type
	- Suggests user variables with matching declared type
- Diagnostics for variable declarations and assignments:
	- Invalid type keywords
	- Undefined variable assignments
	- Type mismatch in assignments (for example int/byte/float/double/string/bool)
	- Invalid function return type usage in assignments
	- String formatting and quoting issues
	- Byte-specific constraints (for example negative values)

## Architecture

### LSP Server (Python)

The server is implemented with `pygls` and `lsprotocol` and currently handles:

- `textDocument/completion`
- `textDocument/didOpen`
- `textDocument/didChange`

Completion and diagnostic logic is driven by rule handlers and asset files containing TMScript metadata (keywords, functions, methods, and types).

### VS Code Extension (TypeScript)

The VS Code client uses `vscode-languageclient` to launch and communicate with the server.

It can run the server in either mode:
- As a packaged executable (preferred when available)
- As a Python module fallback (`src.main` by default)

It also contributes:
- TMScript language registration (`tmscript`)
- `.tms` file association
- Extension settings for server path, Python path, module entrypoint, and trace level

---

Note: This extension is not officially affiliated with Techman Robot Inc. TMscript documentation is based on TMscript 2.24.
