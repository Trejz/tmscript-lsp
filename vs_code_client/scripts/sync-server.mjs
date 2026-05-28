import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const extensionRoot = process.cwd();
const sourceServerRoot = path.resolve(extensionRoot, "..", "server");
const sourceServerSrc = path.join(sourceServerRoot, "src");
const sourceServerDist = path.join(sourceServerRoot, "dist");
const destinationServerRoot = path.join(extensionRoot, "server");
const destinationServerSrc = path.join(destinationServerRoot, "src");
const destinationServerDist = path.join(destinationServerRoot, "dist");
const destinationServerBin = path.join(destinationServerRoot, "bin");
const destinationServerBinWin = path.join(destinationServerRoot, "bin", "win32");
const destinationServerExe = path.join(destinationServerRoot, "tmscript-lsp-server.exe");

if (!fs.existsSync(sourceServerSrc)) {
  throw new Error(`Server source not found at ${sourceServerSrc}`);
}

fs.rmSync(destinationServerRoot, { recursive: true, force: true });
fs.mkdirSync(destinationServerRoot, { recursive: true });
fs.cpSync(sourceServerSrc, destinationServerSrc, { recursive: true });

if (fs.existsSync(sourceServerDist)) {
  fs.cpSync(sourceServerDist, destinationServerDist, { recursive: true });

  const winExe = path.join(sourceServerDist, "main.exe");
  if (fs.existsSync(winExe)) {
    fs.mkdirSync(destinationServerBin, { recursive: true });
    fs.mkdirSync(destinationServerBinWin, { recursive: true });
    fs.copyFileSync(winExe, destinationServerExe);
    fs.copyFileSync(winExe, path.join(destinationServerBin, "main.exe"));
    fs.copyFileSync(winExe, path.join(destinationServerBinWin, "tmscript-lsp-server.exe"));
  }
}

const requirementsPath = path.join(destinationServerRoot, "requirements.txt");
const requirements = [
  "pygls>=1.3.0",
  "lsprotocol>=2023.0.1",
].join("\n");

fs.writeFileSync(requirementsPath, `${requirements}\n`, "utf8");
console.log(`Bundled server copied to ${destinationServerRoot}`);
