import * as fs from "fs";
import * as path from "path";
import * as vscode from "vscode";
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  Trace,
} from "vscode-languageclient/node";

let client: LanguageClient | undefined;

function resolvePath(inputPath: string, workspaceRoot: string): string {
  if (path.isAbsolute(inputPath)) {
    return inputPath;
  }

  return path.join(workspaceRoot, inputPath);
}

function resolveServerRoot(
  configuredServerRoot: string,
  workspaceRoot: string | undefined,
  extensionPath: string,
): string {
  const normalizedConfigured = configuredServerRoot.trim();

  if (normalizedConfigured.length > 0) {
    if (path.isAbsolute(normalizedConfigured)) {
      return normalizedConfigured;
    }

    if (workspaceRoot) {
      const workspaceCandidate = resolvePath(normalizedConfigured, workspaceRoot);
      if (fs.existsSync(workspaceCandidate)) {
        return workspaceCandidate;
      }
    }

    return path.join(extensionPath, normalizedConfigured);
  }

  const bundledServer = path.join(extensionPath, "server");
  if (fs.existsSync(path.join(bundledServer, "src", "main.py"))) {
    return bundledServer;
  }

  const siblingServer = path.join(extensionPath, "..", "server");
  if (fs.existsSync(path.join(siblingServer, "src", "main.py"))) {
    return siblingServer;
  }

  if (workspaceRoot) {
    const workspaceServer = path.join(workspaceRoot, "server");
    if (fs.existsSync(path.join(workspaceServer, "src", "main.py"))) {
      return workspaceServer;
    }
  }

  return bundledServer;
}

function resolveExecutablePath(
  configuredExecutablePath: string,
  serverRoot: string,
  workspaceRoot: string | undefined,
  extensionPath: string,
): string | undefined {
  const normalizedConfigured = configuredExecutablePath.trim();

  if (normalizedConfigured.length > 0) {
    if (path.isAbsolute(normalizedConfigured)) {
      return fs.existsSync(normalizedConfigured) ? normalizedConfigured : undefined;
    }

    if (workspaceRoot) {
      const workspaceCandidate = resolvePath(normalizedConfigured, workspaceRoot);
      if (fs.existsSync(workspaceCandidate)) {
        return workspaceCandidate;
      }
    }

    const extensionCandidate = path.join(extensionPath, normalizedConfigured);
    return fs.existsSync(extensionCandidate) ? extensionCandidate : undefined;
  }

  const platformCandidates = process.platform === "win32"
    ? [
      path.join(serverRoot, "bin", "win32", "tmscript-lsp-server.exe"),
      path.join(serverRoot, "dist", "main.exe"),
      path.join(serverRoot, "dist", "tmscript-lsp-server.exe"),
    ]
    : process.platform === "darwin"
      ? [
        path.join(serverRoot, "bin", "darwin", "tmscript-lsp-server"),
        path.join(serverRoot, "dist", "main"),
        path.join(serverRoot, "dist", "tmscript-lsp-server"),
      ]
      : [
        path.join(serverRoot, "bin", "linux", "tmscript-lsp-server"),
        path.join(serverRoot, "dist", "main"),
        path.join(serverRoot, "dist", "tmscript-lsp-server"),
      ];

  for (const candidate of platformCandidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  return undefined;
}

function detectPython(serverRoot: string, configuredPath: string): string {
  if (configuredPath.trim().length > 0) {
    return configuredPath;
  }

  const venvCandidates = process.platform === "win32"
    ? [
      path.join(serverRoot, ".venv", "Scripts", "python.exe"),
      path.join(serverRoot, "venv", "Scripts", "python.exe"),
    ]
    : [
      path.join(serverRoot, ".venv", "bin", "python"),
      path.join(serverRoot, "venv", "bin", "python"),
    ];

  for (const candidate of venvCandidates) {
    if (fs.existsSync(candidate)) {
      return candidate;
    }
  }

  return "python";
}

function toTraceMode(value: string): Trace {
  if (value === "messages") {
    return Trace.Messages;
  }

  if (value === "verbose") {
    return Trace.Verbose;
  }

  return Trace.Off;
}

export async function activate(context: vscode.ExtensionContext): Promise<void> {
  const workspaceRoot = vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;

  const config = vscode.workspace.getConfiguration("tmscriptLsp");
  const configuredServerRoot = config.get<string>("serverRoot", "");
  const serverRoot = resolveServerRoot(configuredServerRoot, workspaceRoot, context.extensionPath);

  const executablePath = resolveExecutablePath(
    config.get<string>("serverExecutablePath", ""),
    serverRoot,
    workspaceRoot,
    context.extensionPath,
  );

  const pythonPath = detectPython(serverRoot, config.get<string>("pythonPath", ""));
  const serverModule = config.get<string>("serverModule", "src.main");

  let serverOptions: ServerOptions | undefined;

  if (executablePath) {
    serverOptions = {
      command: executablePath,
      args: [],
      options: {
        cwd: path.dirname(executablePath),
        env: {
          ...process.env,
        },
      },
    };
  } else if (fs.existsSync(path.join(serverRoot, "src", "main.py"))) {
    serverOptions = {
      command: pythonPath,
      args: ["-m", serverModule],
      options: {
        cwd: serverRoot,
        env: {
          ...process.env,
          PYTHONPATH: process.env.PYTHONPATH
            ? `${serverRoot}${path.delimiter}${process.env.PYTHONPATH}`
            : serverRoot,
        },
      },
    };
  } else {
    vscode.window.showErrorMessage(
      "TMScript LSP server executable was not found and Python server source is missing. Bundle server/bin for your platform or set tmscriptLsp.serverExecutablePath.",
    );
    return;
  }

  const clientOptions: LanguageClientOptions = {
    documentSelector: [
      { scheme: "file", language: "tmscript" },
      { scheme: "untitled", language: "tmscript" },
    ],
    synchronize: {
      fileEvents: vscode.workspace.createFileSystemWatcher("**/*.tms"),
    },
    outputChannelName: "TMScript LSP",
  };

  client = new LanguageClient(
    "tmscript-lsp",
    "TMScript Language Server",
    serverOptions,
    clientOptions,
  );

  client.setTrace(toTraceMode(config.get<string>("trace.server", "off")));
  context.subscriptions.push(client);
  await client.start();
}

export async function deactivate(): Promise<void> {
  if (!client) {
    return;
  }

  await client.stop();
}
