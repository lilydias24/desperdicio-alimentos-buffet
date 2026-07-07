# Encerra o dashboard iniciado por apresentar.ps1.
# Uso: powershell -ExecutionPolicy Bypass -File parar.ps1

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$dockerOk = $false
try {
    docker --version *> $null
    if ($?) { $dockerOk = $true }
} catch {
    $dockerOk = $false
}

if ($dockerOk) {
    Write-Host "Encerrando o container Docker (docker compose down)..." -ForegroundColor Cyan
    docker compose down
}

Write-Host ""
Write-Host "Se o dashboard estiver rodando localmente (janela do Streamlit aberta" -ForegroundColor Yellow
Write-Host "fora do Docker), feche essa janela ou pressione Ctrl+C nela." -ForegroundColor Yellow
