# TRS Engine Core - Extension Installer
# Run this script to install recommended VS Code/Cursor extensions

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "TRS ENGINE CORE - EXTENSION INSTALLER" -ForegroundColor Cyan
Write-Host "================================================================================`n" -ForegroundColor Cyan

# Check if code command is available
$codeCmd = Get-Command code -ErrorAction SilentlyContinue

if (-not $codeCmd) {
    Write-Host "[ERROR] 'code' command not found. Please add VS Code/Cursor to PATH." -ForegroundColor Red
    Write-Host "[INFO] Or install extensions manually from the Extensions panel.`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Installing essential extensions...`n" -ForegroundColor Green

# Essential Extensions
$extensions = @(
    "ms-python.python",                    # Python
    "ms-python.vscode-pylance",            # Pylance
    "ms-toolsai.jupyter",                  # Jupyter
    "ms-toolsai.datawrangler",             # Data Wrangler
    "mechatroner.rainbow-csv",             # Rainbow CSV
    "eamodio.gitlens",                     # GitLens
    "mhutchie.git-graph",                  # Git Graph
    "usernamehw.errorlens",                # Error Lens
    "yzhang.markdown-all-in-one",          # Markdown All in One
    "christian-kohler.path-intellisense",  # Path Intellisense
    "naumovs.color-highlight",             # Color Highlight
    "njpwerner.autodocstring",             # autoDocstring
    "gruntfuggly.todo-tree",               # Todo Tree
    "aaron-bond.better-comments"           # Better Comments
)

$success = 0
$failed = 0

foreach ($ext in $extensions) {
    Write-Host "[INSTALLING] $ext" -ForegroundColor Yellow
    
    try {
        code --install-extension $ext --force 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] $ext installed successfully" -ForegroundColor Green
            $success++
        }
        else {
            Write-Host "  [FAILED] Could not install $ext" -ForegroundColor Red
            $failed++
        }
    }
    catch {
        Write-Host "  [FAILED] Error installing $ext" -ForegroundColor Red
        $failed++
    }
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "[SUMMARY] Installed: $success | Failed: $failed" -ForegroundColor Cyan
Write-Host "================================================================================`n" -ForegroundColor Cyan

if ($failed -gt 0) {
    Write-Host "[INFO] Some extensions failed to install. Try installing them manually." -ForegroundColor Yellow
    Write-Host "[INFO] Open Extensions panel (Ctrl+Shift+X) and search for the extension name.`n" -ForegroundColor Yellow
}

Write-Host "[INFO] Please restart VS Code/Cursor for changes to take effect.`n" -ForegroundColor Green

