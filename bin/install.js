#!/usr/bin/env node
const fs = require("fs");
const os = require("os");
const path = require("path");

const root = path.resolve(__dirname, "..");
const codexHome = process.env.CODEX_HOME
  ? path.resolve(process.env.CODEX_HOME)
  : path.join(os.homedir(), ".codex");
const skillsDir = path.join(codexHome, "skills");
const skillNames = [
  "constitution-init",
  "constitutional-amendment",
  "constitutional-review",
];

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const from = path.join(src, entry.name);
    const to = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(from, to);
    } else if (entry.isFile()) {
      fs.copyFileSync(from, to);
      fs.chmodSync(to, fs.statSync(from).mode);
    }
  }
}

fs.mkdirSync(skillsDir, { recursive: true });

for (const skillName of skillNames) {
  const src = path.join(root, skillName);
  const dest = path.join(skillsDir, skillName);
  if (!fs.existsSync(src)) {
    throw new Error(`Missing skill directory: ${src}`);
  }
  fs.rmSync(dest, { recursive: true, force: true });
  copyDir(src, dest);
  console.log(`installed: ${dest}`);
}

console.log(`Codex skills installed to: ${skillsDir}`);
