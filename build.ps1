#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build the admin UI and packaged VS Code extension. Install only with -Install.
#>
param([switch]$Install)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSCommandPath
function Invoke-Checked([string]$Program, [string[]]$Arguments) {
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Program failed with exit code $LASTEXITCODE" }
}
Push-Location -LiteralPath $ProjectRoot
try {
    Push-Location -LiteralPath (Join-Path $ProjectRoot 'admin-ui')
    try {
        Invoke-Checked 'npm' @('ci', '--ignore-scripts', '--no-audit', '--no-fund')
        Invoke-Checked 'npm' @('run', 'build')
    } finally { Pop-Location }
    Push-Location -LiteralPath (Join-Path $ProjectRoot 'vscode-ego')
    try {
        Invoke-Checked 'npm' @('ci', '--ignore-scripts', '--no-audit', '--no-fund')
        Invoke-Checked 'npm' @('run', 'compile')
        Invoke-Checked 'npm' @('run', 'package')
        if ($Install) {
            $Package = Get-ChildItem -LiteralPath . -Filter '*.vsix' |
                Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if (-not $Package) { throw 'No VSIX produced by packaging' }
            Invoke-Checked 'code' @('--install-extension', $Package.FullName, '--force')
        }
    } finally { Pop-Location }
} finally { Pop-Location }
