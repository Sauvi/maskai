import * as vscode from 'vscode';
import { execFile } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';

export function activate(context: vscode.ExtensionContext) {

    // ── MASK SELECTED CODE ───────────────────────────
    let maskCommand = vscode.commands.registerCommand(
        'maskai.maskCode',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor found');
                return;
            }

            const selection = editor.selection;
            const selectedCode = editor.document.getText(selection);

            if (!selectedCode) {
                vscode.window.showErrorMessage(
                    'Please select some code first'
                );
                return;
            }

            await maskCodeHelper(context, editor.document, selectedCode);
        }
    );

    // ── MASK ENTIRE FILE ─────────────────────────────
    let maskEntireFileCommand = vscode.commands.registerCommand(
        'maskai.maskEntireFile',
        async (uri?: vscode.Uri) => {
            let document: vscode.TextDocument;

            // Called from explorer context menu with URI
            if (uri) {
                document = await vscode.workspace.openTextDocument(uri);
            } else {
                // Called from editor context or command palette
                const editor = vscode.window.activeTextEditor;
                if (!editor) {
                    vscode.window.showErrorMessage('No active editor found');
                    return;
                }
                document = editor.document;
            }

            const fullCode = document.getText();

            if (!fullCode || fullCode.trim().length === 0) {
                vscode.window.showErrorMessage('File is empty');
                return;
            }

            await maskCodeHelper(context, document, fullCode);
        }
    );

    // ── UNMASK AND REPLACE ───────────────────────────
    let unmaskAndReplaceCommand = vscode.commands.registerCommand(
        'maskai.unmaskAndReplace',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor found');
                return;
            }

            const selection = editor.selection;
            const selectedText = editor.document.getText(selection);

            if (!selectedText) {
                vscode.window.showErrorMessage(
                    'Please select the masked text first'
                );
                return;
            }

            const mappingPath = path.join(
                context.extensionPath, 'mapping.json'
            );

            if (!fs.existsSync(mappingPath)) {
                vscode.window.showErrorMessage(
                    'No mapping found. Mask some code first.'
                );
                return;
            }

            const maskerPath = path.join(
                context.extensionPath, 'masker.py'
            );

            execFile('python', [
                maskerPath,
                'unmask',
                '--response', selectedText,
                '--mapping', mappingPath
            ],
            { env: { ...process.env, PYTHONIOENCODING: 'utf-8' } },
            (error, stdout, stderr) => {

                if (error) {
                    vscode.window.showErrorMessage(
                        `MaskAI Error: ${stderr}`
                    );
                    return;
                }

                const unmaskedText = stdout;

                // Replace selected text with unmasked version
                editor.edit(editBuilder => {
                    editBuilder.replace(selection, unmaskedText);
                }).then(success => {
                    if (success) {
                        vscode.window.showInformationMessage(
                            '✅ Text unmasked and replaced!'
                        );
                    } else {
                        vscode.window.showErrorMessage(
                            'Failed to replace text'
                        );
                    }
                });
            });
        }
    );

    context.subscriptions.push(
        maskCommand, 
        maskEntireFileCommand, 
        unmaskAndReplaceCommand
    );
}

// ── HELPER: MASK CODE ────────────────────────────────
async function maskCodeHelper(
    context: vscode.ExtensionContext,
    document: vscode.TextDocument,
    code: string
) {
    // Detect language from VS Code editor
    const languageId = document.languageId;
    let language = 'auto';
    let tempFileExt = '.txt';

    if (languageId === 'python') {
        language = 'python';
        tempFileExt = '.py';
    } else if (['javascript', 'typescript', 'javascriptreact', 'typescriptreact'].includes(languageId)) {
        language = 'javascript';
        tempFileExt = '.js';
    }

    // Read user settings
    const config = vscode.workspace.getConfiguration('maskai');
    const maskClasses = config.get<boolean>('maskClasses', true);
    const maskFunctions = config.get<boolean>('maskFunctions', true);
    const maskParameters = config.get<boolean>('maskParameters', true);
    const maskVariables = config.get<boolean>('maskVariables', true);

    const maskerPath = path.join(
        context.extensionPath, 'masker.py'
    );
    const mappingPath = path.join(
        context.extensionPath, 'mapping.json'
    );
    const tempFile = path.join(
        context.extensionPath, 'temp_input' + tempFileExt
    );

    fs.writeFileSync(tempFile, code);

    // Build arguments array
    const args = [
        maskerPath,
        'mask',
        '--file', tempFile,
        '--lang', language,
        '--mapping', mappingPath
    ];

    // Add skip flags based on settings
    if (!maskClasses) args.push('--skip-classes');
    if (!maskFunctions) args.push('--skip-functions');
    if (!maskParameters) args.push('--skip-parameters');
    if (!maskVariables) args.push('--skip-variables');

    execFile('python', args,
    { env: { ...process.env, PYTHONIOENCODING: 'utf-8' } },
    (error, stdout, stderr) => {

        if (fs.existsSync(tempFile)) {
            fs.unlinkSync(tempFile);
        }

        if (error) {
            vscode.window.showErrorMessage(
                `MaskAI Error: ${stderr}`
            );
            return;
        }

        const maskedCode = stdout;

        vscode.env.clipboard.writeText(maskedCode).then(() => {
            showMappingPanel(context, mappingPath, maskedCode);
            vscode.window.showInformationMessage(
                '✅ Masked code copied to clipboard! Safe to paste to AI.'
            );
        });
    });
}

// ── MAPPING PANEL ────────────────────────────────────
function showMappingPanel(
    context: vscode.ExtensionContext,
    mappingPath: string,
    maskedCode: string
) {
    const panel = vscode.window.createWebviewPanel(
        'maskaiMapping',
        'MaskAI — Mapping Table',
        vscode.ViewColumn.Beside,
        {}
    );

    let mappingHtml = '';
    if (fs.existsSync(mappingPath)) {
        const mapping = JSON.parse(
            fs.readFileSync(mappingPath, 'utf8')
        );
        const rows = Object.entries(mapping)
            .map(([real, masked]) => `
                <tr>
                    <td class="real">${real}</td>
                    <td class="arrow">→</td>
                    <td class="masked">${masked}</td>
                </tr>
            `).join('');
        mappingHtml = `<table>${rows}</table>`;
    }

    panel.webview.html = `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: monospace;
                    padding: 20px;
                    background: #1e1e1e;
                    color: #d4d4d4;
                }
                h2 { color: #569cd6; }
                h3 { color: #9cdcfe; margin-top: 30px; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }
                td {
                    padding: 6px 12px;
                    border-bottom: 1px solid #333;
                }
                .real   { color: #f44747; }
                .arrow  { color: #666; }
                .masked { color: #4ec9b0; }
                pre {
                    background: #252526;
                    padding: 15px;
                    border-radius: 4px;
                    overflow-x: auto;
                    color: #ce9178;
                    font-size: 13px;
                }
                .warning {
                    background: #3a2a00;
                    border-left: 3px solid #f9a825;
                    padding: 10px 15px;
                    margin: 15px 0;
                    border-radius: 2px;
                }
            </style>
        </head>
        <body>
            <h2>🔒 MaskAI — Mapping Table</h2>
            <div class="warning">
                ⚠️ Keep this mapping private.
                You need it to unmask the AI response.
            </div>
            <h3>Identifier Mapping</h3>
            ${mappingHtml}
            <h3>Masked Code (copied to clipboard)</h3>
            <pre>${maskedCode}</pre>
        </body>
        </html>
    `;
}

export function deactivate() {}
