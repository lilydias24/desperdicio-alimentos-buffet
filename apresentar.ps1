# Sobe o dashboard do Grupo 03 para a apresentacao/demo.
# Uso: clique com o botao direito > Executar com PowerShell, ou rode:
#   powershell -ExecutionPolicy Bypass -File apresentar.ps1
#
# Tenta Docker Compose primeiro (caminho documentado no README). Se o Docker
# nao estiver disponivel na maquina da apresentacao, cai para execucao local
# com Python. Ao final, abre o navegador em http://localhost:8501.

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

Write-Host "================================================================" -ForegroundColor Green
Write-Host " Grupo 03 - Investigacao do Desperdicio de Alimentos em Buffets" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

function Wait-Dashboard {
    param([int]$TimeoutSeconds = 90)
    $elapsed = 0
    while ($elapsed -lt $TimeoutSeconds) {
        try {
            $resp = Invoke-WebRequest -Uri "http://localhost:8501/_stcore/health" -UseBasicParsing -TimeoutSec 2
            if ($resp.StatusCode -eq 200) { return $true }
        } catch {}
        Start-Sleep -Seconds 2
        $elapsed += 2
        Write-Host "." -NoNewline
    }
    return $false
}

$dockerOk = $false
try {
    docker --version *> $null
    if ($?) { $dockerOk = $true }
} catch {
    $dockerOk = $false
}

if ($dockerOk) {
    Write-Host "[1/2] Docker encontrado. Subindo o dashboard com 'docker compose up --build -d'..." -ForegroundColor Cyan
    docker compose up --build -d
    if (-not $?) {
        Write-Host ""
        Write-Host "Falha ao subir o container. Veja o erro acima ou rode 'docker compose logs'." -ForegroundColor Red
        exit 1
    }
    Write-Host "[2/2] Aguardando o dashboard ficar pronto" -NoNewline
} else {
    Write-Host "[1/2] Docker nao encontrado nesta maquina. Rodando localmente com Python..." -ForegroundColor Yellow
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host ""
        Write-Host "Python nao encontrado no PATH. Instale Python 3.10+ ou use uma maquina com Docker." -ForegroundColor Red
        exit 1
    }
    Write-Host "      Instalando dependencias (requirements.txt)..." -ForegroundColor Cyan
    pip install -r requirements.txt --quiet
    Start-Process -FilePath "python" -ArgumentList "-m", "streamlit", "run", "app/app.py" -WindowStyle Normal
    Write-Host "[2/2] Aguardando o dashboard ficar pronto" -NoNewline
}

if (Wait-Dashboard) {
    Write-Host ""
    Write-Host ""
    Write-Host "Dashboard pronto! Abrindo http://localhost:8501 no navegador..." -ForegroundColor Green
    Start-Process "http://localhost:8501"
} else {
    Write-Host ""
    Write-Host ""
    Write-Host "O dashboard nao respondeu em 90s." -ForegroundColor Yellow
    if ($dockerOk) {
        Write-Host "Verifique os logs com: docker compose logs -f" -ForegroundColor Yellow
    } else {
        Write-Host "Confira a janela do Streamlit que foi aberta separadamente." -ForegroundColor Yellow
    }
    Write-Host "Voce tambem pode abrir manualmente: http://localhost:8501" -ForegroundColor Yellow
}
