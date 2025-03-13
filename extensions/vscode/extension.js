// The module 'vscode' contains the VS Code extensibility API
const vscode = require('vscode');
const axios = require('axios');

// API base URL - would point to a running instance of the API server
const API_URL = 'http://localhost:5000';

// This method is called when your extension is activated
function activate(context) {
    // Create status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "AI Socratic Clarifier";
    statusBarItem.command = 'socraticClarifier.analyze';
    statusBarItem.show();
    
    // Keep track of decorations
    let decorations = [];
    let decorationType = vscode.window.createTextEditorDecorationType({
        backgroundColor: vscode.workspace.getConfiguration('socraticClarifier').get('highlightColor'),
        isWholeLine: false,
        overviewRulerColor: 'rgba(255, 100, 100, 0.7)',
        overviewRulerLane: vscode.OverviewRulerLane.Right,
        light: {
            borderColor: 'darkred'
        },
        dark: {
            borderColor: 'lightred'
        }
    });
    
    // Register analyze command
    let analyzeCommand = vscode.commands.registerCommand('socraticClarifier.analyze', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showInformationMessage('No active editor to analyze');
            return;
        }
        
        const document = editor.document;
        const text = document.getText();
        
        // Show progress notification
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing text with AI Socratic Clarifier",
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            
            try {
                // Call the API
                const mode = vscode.workspace.getConfiguration('socraticClarifier').get('mode');
                const response = await axios.post(`${API_URL}/analyze`, {
                    text: text,
                    mode: mode
                });
                
                progress.report({ increment: 50 });
                
                const result = response.data;
                
                // Clear previous decorations
                editor.setDecorations(decorationType, []);
                decorations = [];
                
                // Create decorations for each issue
                if (result.issues && result.issues.length > 0) {
                    result.issues.forEach(issue => {
                        // Find the position in the document for the term
                        const startPos = document.positionAt(text.indexOf(issue.term));
                        const endPos = document.positionAt(text.indexOf(issue.term) + issue.term.length);
                        
                        // Create hover message with issue details and questions
                        let hoverMessage = new vscode.MarkdownString();
                        hoverMessage.appendMarkdown(`### ${issue.issue.replace('_', ' ').toUpperCase()}\n\n`);
                        hoverMessage.appendMarkdown(`**Issue**: ${issue.description}\n\n`);
                        
                        // Add reasoning if available
                        if (result.reasoning) {
                            hoverMessage.appendMarkdown(`**Reasoning**:\n\`\`\`\n${result.reasoning}\n\`\`\`\n\n`);
                        }
                        
                        // Add questions related to this issue
                        hoverMessage.appendMarkdown(`**Clarifying Questions**:\n`);
                        result.questions.forEach(question => {
                            hoverMessage.appendMarkdown(`- ${question}\n`);
                        });
                        
                        // Create decoration
                        const decoration = {
                            range: new vscode.Range(startPos, endPos),
                            hoverMessage: hoverMessage
                        };
                        
                        decorations.push(decoration);
                    });
                    
                    // Apply decorations
                    editor.setDecorations(decorationType, decorations);
                    
                    vscode.window.showInformationMessage(`Found ${result.issues.length} issue(s) to clarify.`);
                } else {
                    vscode.window.showInformationMessage('No issues found in the text.');
                }
                
                progress.report({ increment: 100 });
            } catch (error) {
                vscode.window.showErrorMessage(`Error: ${error.message}`);
            }
        });
    });
    
    // Register mode change command
    let changeModeCommand = vscode.commands.registerCommand('socraticClarifier.changeMode', async () => {
        try {
            // Get available modes
            const response = await axios.get(`${API_URL}/modes`);
            const modes = response.data.modes;
            
            // Show quick pick for modes
            const selectedMode = await vscode.window.showQuickPick(modes, {
                placeHolder: 'Select operating mode'
            });
            
            if (selectedMode) {
                // Update configuration
                await vscode.workspace.getConfiguration('socraticClarifier').update('mode', selectedMode, true);
                vscode.window.showInformationMessage(`Socratic Clarifier mode changed to: ${selectedMode}`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Error: ${error.message}`);
        }
    });
    
    // Register auto-analyze if enabled
    let changeTextSubscription;
    const setupAutoAnalyze = () => {
        const autoAnalyze = vscode.workspace.getConfiguration('socraticClarifier').get('autoAnalyze');
        
        if (autoAnalyze && !changeTextSubscription) {
            // Debounce function to prevent excessive API calls
            let analyzeTimeout;
            changeTextSubscription = vscode.workspace.onDidChangeTextDocument(event => {
                clearTimeout(analyzeTimeout);
                analyzeTimeout = setTimeout(() => {
                    if (event.document === vscode.window.activeTextEditor?.document) {
                        vscode.commands.executeCommand('socraticClarifier.analyze');
                    }
                }, 2000);  // Delay in ms
            });
            context.subscriptions.push(changeTextSubscription);
        } else if (!autoAnalyze && changeTextSubscription) {
            changeTextSubscription.dispose();
            changeTextSubscription = undefined;
        }
    };
    
    // Watch for configuration changes
    context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('socraticClarifier.autoAnalyze')) {
            setupAutoAnalyze();
        }
        
        if (e.affectsConfiguration('socraticClarifier.highlightColor')) {
            decorationType = vscode.window.createTextEditorDecorationType({
                backgroundColor: vscode.workspace.getConfiguration('socraticClarifier').get('highlightColor'),
                isWholeLine: false,
                overviewRulerColor: 'rgba(255, 100, 100, 0.7)',
                overviewRulerLane: vscode.OverviewRulerLane.Right
            });
            
            // Reapply decorations if any exist
            const editor = vscode.window.activeTextEditor;
            if (editor && decorations.length > 0) {
                editor.setDecorations(decorationType, decorations);
            }
        }
    }));
    
    // Initial setup
    setupAutoAnalyze();
    
    // Register all disposables
    context.subscriptions.push(statusBarItem);
    context.subscriptions.push(analyzeCommand);
    context.subscriptions.push(changeModeCommand);
}

// This method is called when your extension is deactivated
function deactivate() {
    // Clean up resources if needed
}

module.exports = {
    activate,
    deactivate
};
