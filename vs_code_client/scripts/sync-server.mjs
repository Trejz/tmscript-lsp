import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const extensionRoot = process.cwd();
const sourceServerRoot = path.resolve(extensionRoot, "..", "server");
const sourceServerSrc = path.join(sourceServerRoot, "src");
const destinationServerRoot = path.join(extensionRoot, "server");
const destinationServerSrc = path.join(destinationServerRoot, "src");

if (!fs.existsSync(sourceServerSrc)) {
  throw new Error(`Server source not found at ${sourceServerSrc}`);
}

fs.rmSync(destinationServerRoot, { recursive: true, force: true });
fs.mkdirSync(destinationServerRoot, { recursive: true });
fs.cpSync(sourceServerSrc, destinationServerSrc, { recursive: true });

const requirementsPath = path.join(destinationServerRoot, "requirements.txt");
const requirements = [
  "pygls>=1.3.0",
  "lsprotocol>=2023.0.1",
].join("\n");

fs.writeFileSync(requirementsPath, `${requirements}\n`, "utf8");
console.log(`Bundled server copied to ${destinationServerRoot}`);
