# AI-Socratic-Clarifier VS Code Extension

This directory contains a prototype VS Code extension that integrates the AI-Socratic-Clarifier into the popular code editor. This allows writers to get inline feedback and Socratic questions as they write.

## Features

- **Inline Feedback**: Highlights potential issues in your text directly within the editor
- **Socratic Questioning**: Provides questions to help improve clarity and reduce bias
- **SoT Reasoning**: Shows structured reasoning for each issue
- **Multiple Modes**: Switch between academic, casual, legal, and other modes

## Installation (Development)

1. Install VS Code Extension Manager
   ```bash
   npm install -g @vscode/vsce
   ```

2. Install dependencies
   ```bash
   cd extensions/vscode
   npm install
   ```

3. Package the extension
   ```bash
   vsce package
   ```

4. Install the generated .vsix file in VS Code:
   - Open VS Code
   - Go to Extensions view (Ctrl+Shift+X)
   - Click "..." in the top-right of the extensions view
   - Choose "Install from VSIX..."
   - Select the .vsix file you generated

## Usage

1. Open a text or markdown file
2. Click the "Socratic Clarifier" icon in the status bar to activate
3. Issues will be highlighted in the text
4. Hover over a highlight to see questions and reasoning
5. Use the command palette (Ctrl+Shift+P) to change modes

## Configuration

You can configure the extension in your VS Code settings:
- `socraticClarifier.mode`: Default mode (academic, casual, legal, etc.)
- `socraticClarifier.autoAnalyze`: Whether to analyze text automatically as you type
- `socraticClarifier.highlightColor`: Color for highlighted issues
