# INSTALAR E RODAR - Dashboard Parceiro Isopor
# Execute como Administrador no PowerShell

$ErrorActionPreference = "Stop"
$repo = "https://github.com/med4to-badass/AI-Master-Plan.git"
$pasta = "$env:USERPROFILE\Desktop\AuraDashboard"
$branch = "main"

Write-Host ""
Write-Host "=== Dashboard Parceiro Isopor ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "Verificando Python..." -ForegroundColor Yellow
$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -ge 9) {
                $python = $cmd
                Write-Host "  OK: $ver" -ForegroundColor Green
                break
            }
        }
    } catch {}
}

if (-not $python) {
    Write-Host ""
    Write-Host "Python 3.9+ nao encontrado." -ForegroundColor Red
    Write-Host "Baixando instalador do Python 3.12..." -ForegroundColor Yellow
    $pyInstaller = "$env:TEMP\python-installer.exe"
    Invoke-WebRequest "https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe" -OutFile $pyInstaller
    Start-Process $pyInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    $python = "python"
    Write-Host "  Python instalado." -ForegroundColor Green
}

# 2. Verificar Git
Write-Host "Verificando Git..." -ForegroundColor Yellow
$temGit = $false
try {
    git --version | Out-Null
    $temGit = $true
    Write-Host "  OK: Git disponivel" -ForegroundColor Green
} catch {
    Write-Host "  Git nao encontrado. Usando download ZIP..." -ForegroundColor Yellow
}

# 3. Baixar ou atualizar o projeto
if (Test-Path $pasta) {
    Write-Host "Atualizando projeto em $pasta..." -ForegroundColor Yellow
    if ($temGit -and (Test-Path "$pasta\.git")) {
        Set-Location $pasta
        git pull origin $branch 2>&1 | Out-Null
        Write-Host "  Atualizado." -ForegroundColor Green
    } else {
        Write-Host "  Pasta ja existe, pulando download." -ForegroundColor Green
        Set-Location $pasta
    }
} else {
    New-Item -ItemType Directory -Path $pasta -Force | Out-Null
    if ($temGit) {
        Write-Host "Clonando repositorio..." -ForegroundColor Yellow
        git clone --branch $branch $repo $pasta 2>&1
        Set-Location $pasta
        Write-Host "  Clonado." -ForegroundColor Green
    } else {
        Write-Host "Baixando projeto como ZIP..." -ForegroundColor Yellow
        $zip = "$env:TEMP\dashboard.zip"
        Invoke-WebRequest "https://github.com/med4to-badass/AI-Master-Plan/archive/refs/heads/main.zip" -OutFile $zip
        Expand-Archive $zip -DestinationPath $env:TEMP -Force
        Copy-Item "$env:TEMP\AI-Master-Plan-main\*" $pasta -Recurse -Force
        Set-Location $pasta
        Write-Host "  Baixado e extraido." -ForegroundColor Green
    }
}

# 4. Criar ambiente virtual
Write-Host "Configurando ambiente virtual..." -ForegroundColor Yellow
if (-not (Test-Path "$pasta\venv_win")) {
    & $python -m venv "$pasta\venv_win"
}
$pip = "$pasta\venv_win\Scripts\pip.exe"
$streamlit = "$pasta\venv_win\Scripts\streamlit.exe"

Write-Host "Instalando dependencias..." -ForegroundColor Yellow
& $pip install -r "$pasta\requirements.txt" -q
Write-Host "  Instalado." -ForegroundColor Green

# 5. Abrir no navegador automaticamente
Write-Host ""
Write-Host "Iniciando dashboard..." -ForegroundColor Cyan
Start-Sleep 1
Start-Process "http://localhost:8501"

# 6. Rodar Streamlit
Write-Host ""
Write-Host "Dashboard rodando em: http://localhost:8501" -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar." -ForegroundColor Gray
Write-Host ""
& $streamlit run "$pasta\app.py" --server.port 8501
