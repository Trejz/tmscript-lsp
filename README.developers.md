# TMScript Developer Guide

This guide explains how to set up local development, run the extension, and publish it.

## Repository Layout

- [server](server): Python language server implementation.
- [vs_code_client](vs_code_client): VS Code extension client and packaging pipeline.

## Prerequisites

- Node.js 20 or newer
- npm 10 or newer
- Python 3.11 or newer
- VS Code

## 1) Python Environment Setup

Run these commands from the repository root:

Windows PowerShell:

python -m venv server/.venv

server/.venv/Scripts/Activate.ps1

pip install pygls lsprotocol

macOS or Linux:

python3 -m venv server/.venv

source server/.venv/bin/activate

pip install pygls lsprotocol

## 2) Node Environment Setup

Run these commands from [vs_code_client](vs_code_client):

npm install

npm run build

## 3) Run Extension Locally

1. Open the repository in VS Code.
2. Start the launch config named Run TMScript Client from [vs_code_client/.vscode/launch.json](vs_code_client/.vscode/launch.json).
3. In the Extension Development Host, open a .tmss file.
4. Verify autocomplete and diagnostics are active.

## 4) How Single-Extension Packaging Works

The extension bundles the Python server source into the extension at prepublish time.

- Source server path: [server/src](server/src)
- Bundled server path: [vs_code_client/server/src](vs_code_client/server/src)
- Sync script: [vs_code_client/scripts/sync-server.mjs](vs_code_client/scripts/sync-server.mjs)

The prepublish script runs:

- npm run sync:server
- npm run build

## 5) Build VSIX Package

From [vs_code_client](vs_code_client):

npm run vscode:prepublish

npx @vscode/vsce package

Result: a VSIX that contains both the VS Code client and bundled Python server source.

## 6) Publish to Marketplace

Before publishing, update metadata in [vs_code_client/package.json](vs_code_client/package.json):

- publisher
- displayName
- description
- version
- repository
- license
- icon

Then publish from [vs_code_client](vs_code_client):

npx @vscode/vsce publish

You will need a Visual Studio Marketplace publisher and Personal Access Token.

## Runtime Notes

- End users still need Python installed.
- If Python is not on PATH, they should set tmscriptLsp.pythonPath.
- If you want zero Python dependency, ship prebuilt platform binaries and launch those from the extension.

## Common Commands

From [vs_code_client](vs_code_client):

npm run build

npm run watch

npm run vscode:prepublish

From repository root with virtual environment active:

python -m server.src.main
