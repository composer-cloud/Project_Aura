#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Setup completo — AuraOS / Dashboard Parceiro Isopor
    Instala ferramentas, dependências e drivers ASUS oficiais.
.NOTES
    Execute como Administrador no PowerShell:
    Set-ExecutionPolicy Bypass -Scope Process -Force; .\SETUP_COMPLETO.ps1
#>

$ErrorActionPreference = "Stop"
$ProgressPreference    = "SilentlyContinue"

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
function Write-Step { param($m); Write-Host "`n[►] $m" -ForegroundColor Cyan }
function Write-OK   { param($m); Write-Host "  [OK] $m" -ForegroundColor Green }
function Write-Warn { param($m); Write-Host "  [!]  $m" -ForegroundColor Yellow }
function Write-Fail { param($m); Write-Host "  [X]  $m" -ForegroundColor Red }

function Install-WingetApp {
    param([string]$Id, [string]$Nome)
    Write-Host "  -> $Nome..." -NoNewline
    $out = winget install --id $Id --silent --accept-package-agreements --accept-source-agreements 2>&1
    if ($LASTEXITCODE -eq 0 -or ($out -join '') -match 'already installed|já instalado') {
        Write-OK $Nome
    } else {
        Write-Warn "$Nome não instalado via winget (cód $LASTEXITCODE) — instale manualmente se necessário"
    }
}

# ─────────────────────────────────────────────
#  Banner
# ─────────────────────────────────────────────
Clear-Host
Write-Host @"
╔══════════════════════════════════════════════════════════╗
║   SETUP COMPLETO — AuraOS / Dashboard Isopor          ║
║   Drivers • Dev Tools • Python • Node.js • ASUS 2x     ║
╚══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Magenta

# ─────────────────────────────────────────────
#  1. Verificações iniciais
# ─────────────────────────────────────────────
Write-Step "Verificações iniciais"

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]"Administrator")
if (-not $isAdmin) { Write-Fail "Execute como Administrador! Saindo..."; Read-Host; exit 1 }
Write-OK "Rodando como Administrador"

try { [void][System.Net.Dns]::GetHostEntry("one.one.one.one"); Write-OK "Internet OK" }
catch { Write-Fail "Sem conexão com a internet. Verifique e tente novamente."; Read-Host; exit 1 }

# ─────────────────────────────────────────────
#  2. winget
# ─────────────────────────────────────────────
Write-Step "Verificando / atualizando winget"

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Warn "winget não encontrado. Instalando App Installer..."
    $uri = "https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
    $tmp = "$env:TEMP\AppInstaller.msixbundle"
    Invoke-WebRequest $uri -OutFile $tmp -UseBasicParsing
    Add-AppxPackage $tmp
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}
winget source update --disable-interactivity 2>&1 | Out-Null
Write-OK "winget pronto"

# ─────────────────────────────────────────────
#  3. Ferramentas de desenvolvimento
# ─────────────────────────────────────────────
Write-Step "Ferramentas de desenvolvimento"

Install-WingetApp "Git.Git"                      "Git"
Install-WingetApp "Python.Python.3.11"           "Python 3.11"
Install-WingetApp "OpenJS.NodeJS.LTS"            "Node.js LTS"
Install-WingetApp "Microsoft.VisualStudioCode"   "VS Code"
Install-WingetApp "GitHub.cli"                   "GitHub CLI (gh)"
Install-WingetApp "Microsoft.WindowsTerminal"    "Windows Terminal"
Install-WingetApp "7zip.7zip"                    "7-Zip"
Install-WingetApp "Cloudflare.cloudflared"       "Cloudflared (para tunnel / serve.sh)"

# Recarrega PATH para usar ferramentas recém-instaladas nesta sessão
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
            [System.Environment]::GetEnvironmentVariable("Path","User")

# ─────────────────────────────────────────────
#  4. Pacotes Python (requirements.txt)
# ─────────────────────────────────────────────
Write-Step "Pacotes Python (streamlit, plotly, pandas, Pillow, reportlab...)"

$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(\d+)" -and [int]$Matches[1] -ge 9) {
            $python = $cmd; break
        }
    } catch {}
}

if ($python) {
    $pkgs = @(
        "streamlit>=1.32",
        "plotly>=5.18",
        "pandas>=2.0",
        "openpyxl>=3.1",
        "requests>=2.31",
        "Pillow>=10.0",
        "reportlab>=4.0"
    )
    Write-Host "  Usando: $(& $python --version)" -ForegroundColor Gray
    foreach ($pkg in $pkgs) {
        $name = ($pkg -split ">=")[0]
        Write-Host "  -> $name..." -NoNewline
        & $python -m pip install $pkg --quiet --upgrade 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { Write-OK $name } else { Write-Warn "$name (verifique manualmente)" }
    }
} else {
    Write-Warn "Python não encontrado no PATH ainda. Reinicie o terminal e rode:`n  pip install -r requirements.txt"
}

# ─────────────────────────────────────────────
#  5. Node.js — IsoSolues-MKT
# ─────────────────────────────────────────────
Write-Step "Node.js — http-server para IsoSolues-MKT"

if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "  -> http-server (global)..." -NoNewline
    npm install -g http-server --silent 2>&1 | Out-Null
    Write-OK "http-server"
} else {
    Write-Warn "npm não está no PATH ainda. Reinicie o terminal e rode: npm install -g http-server"
}

# ─────────────────────────────────────────────
#  6. ASUS Dispositivo 1 — Placa-mãe (ROG / TUF / Prime)
# ─────────────────────────────────────────────
Write-Step "ASUS Dispositivo 1 — Placa-mãe (ROG / TUF / Prime)"

# DriverHub: detecta e instala TODOS os drivers da placa-mãe automaticamente
Install-WingetApp "ASUS.DriverHub"   "ASUS DriverHub (gerenciador oficial de drivers da placa-mãe)"

# Armoury Crate: Aura Sync, fan curves, overlays
Write-Host "  -> ASUS Armoury Crate..." -NoNewline
$acOut = winget install --id "9PM9DSXH6Z5K" --source msstore --accept-package-agreements --accept-source-agreements 2>&1
if ($LASTEXITCODE -eq 0 -or ($acOut -join '') -match 'already installed|já instalado') {
    Write-OK "ASUS Armoury Crate"
} else {
    $acOut2 = winget install --id "ASUS.ArmouryCrate" --silent --accept-package-agreements --accept-source-agreements 2>&1
    if ($LASTEXITCODE -eq 0 -or ($acOut2 -join '') -match 'already installed|já instalado') {
        Write-OK "ASUS Armoury Crate"
    } else {
        Write-Warn "Instale o Armoury Crate manualmente: https://rog.asus.com/br/armoury-crate/"
    }
}

# Chipset — detecta Intel vs AMD
Write-Host ""
Write-Host "  Detectando CPU para drivers de chipset..." -ForegroundColor Yellow
$cpu = (Get-CimInstance Win32_Processor).Name
Write-Host "  CPU: $cpu" -ForegroundColor Gray

if ($cpu -match "Intel") {
    Write-Host "  -> Intel Driver & Support Assistant..." -NoNewline
    $r = winget install --id "Intel.IntelDriverAndSupportAssistant" --silent --accept-package-agreements --accept-source-agreements 2>&1
    if ($LASTEXITCODE -eq 0 -or ($r -join '') -match 'already installed') {
        Write-OK "Intel DSA (detecta e instala chipset, LAN, USB, Wi-Fi automaticamente)"
    } else {
        Write-Warn "Baixe o Intel DSA em: https://www.intel.com/content/www/us/en/support/detect.html"
    }
} elseif ($cpu -match "AMD|Ryzen") {
    Write-Host "  -> AMD Chipset Software..." -NoNewline
    $r = winget install --id "AMD.AMDChipsetSoftware" --silent --accept-package-agreements --accept-source-agreements 2>&1
    if ($LASTEXITCODE -eq 0 -or ($r -join '') -match 'already installed') {
        Write-OK "AMD Chipset Software"
    } else {
        Write-Warn "Baixe o chipset AMD em: https://www.amd.com/pt/support"
    }
}

# Áudio Realtek (pré-instalado na maioria das placas ASUS)
Write-Host "  -> Realtek Audio Control (Microsoft Store)..." -NoNewline
$rtOut = winget install --id "RealtekSemiconductorCorp.RealtekAudioControl" --accept-package-agreements --accept-source-agreements 2>&1
if ($LASTEXITCODE -eq 0 -or ($rtOut -join '') -match 'already installed') {
    Write-OK "Realtek Audio Control"
} else {
    Write-Warn "Áudio: use o ASUS DriverHub para instalar o Realtek automaticamente"
}

# ─────────────────────────────────────────────
#  7. ASUS Dispositivo 2 — GPU (ROG Strix / TUF Gaming)
# ─────────────────────────────────────────────
Write-Step "ASUS Dispositivo 2 — GPU ASUS (ROG Strix / TUF Gaming)"

Install-WingetApp "ASUS.GPUTweakIII"   "ASUS GPU Tweak III (OC, monitoramento, Aura Sync GPU)"

Write-Host ""
Write-Host "  Detectando GPU..." -ForegroundColor Yellow
$gpus = Get-CimInstance Win32_VideoController | Where-Object { $_.Name -notmatch "Microsoft Basic" }
$gpu  = ($gpus | Select-Object -First 1).Name
Write-Host "  GPU: $gpu" -ForegroundColor Gray

if ($gpu -match "NVIDIA|GeForce|RTX|GTX") {
    Write-Host "  -> NVIDIA GeForce Experience (drivers oficiais)..." -NoNewline
    $r = winget install --id "Nvidia.GeForceExperience" --silent --accept-package-agreements --accept-source-agreements 2>&1
    if ($LASTEXITCODE -eq 0 -or ($r -join '') -match 'already installed') {
        Write-OK "NVIDIA GeForce Experience"
    } else {
        Write-Warn "Baixe drivers NVIDIA em: https://www.nvidia.com/pt-br/drivers/"
    }
} elseif ($gpu -match "AMD|Radeon|RX ") {
    Write-Host "  -> AMD Radeon Software Adrenalin..." -NoNewline
    $r = winget install --id "AMD.AdrenalinEdition" --silent --accept-package-agreements --accept-source-agreements 2>&1
    if ($LASTEXITCODE -eq 0 -or ($r -join '') -match 'already installed') {
        Write-OK "AMD Radeon Software Adrenalin"
    } else {
        Write-Warn "Baixe drivers AMD em: https://www.amd.com/pt/support"
    }
} else {
    Write-Warn "GPU '$gpu' não reconhecida automaticamente — use o ASUS DriverHub"
}

# ─────────────────────────────────────────────
#  8. Clonar repositórios
# ─────────────────────────────────────────────
Write-Step "Clonando / atualizando repositórios"

$desktop = [Environment]::GetFolderPath("Desktop")

function Sync-Repo {
    param([string]$Url, [string]$Dest, [string]$Nome)
    Write-Host "  -> $Nome..." -NoNewline
    if (Test-Path "$Dest\.git") {
        git -C $Dest pull origin main --quiet 2>&1 | Out-Null
        Write-OK "$Nome (atualizado)"
    } elseif (Test-Path $Dest) {
        Write-OK "$Nome (pasta já existe)"
    } else {
        git clone $Url $Dest --quiet 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { Write-OK "$Nome (clonado)" }
        else { Write-Warn "$Nome: falha no clone — verifique sua conexão" }
    }
}

if (Get-Command git -ErrorAction SilentlyContinue) {
    Sync-Repo "https://github.com/med4to-badass/AI-Master-Plan.git"  "$desktop\AuraDashboard"  "AI-Master-Plan (AuraDashboard)"
    Sync-Repo "https://github.com/med4to-badass/IsoSolues-MKT.git"  "$desktop\IsoSoluesMKT"  "IsoSolues-MKT"
} else {
    Write-Warn "Git não está no PATH ainda. Reinicie o terminal e execute novamente para clonar."
}

# ─────────────────────────────────────────────
#  9. Atalhos no Desktop
# ─────────────────────────────────────────────
Write-Step "Criando atalhos no Desktop"

$wsh = New-Object -ComObject WScript.Shell

function New-Lnk {
    param([string]$Nome, [string]$Target, [string]$Args, [string]$Desc)
    $lnk = $wsh.CreateShortcut("$desktop\$Nome.lnk")
    $lnk.TargetPath  = $Target
    $lnk.Arguments   = $Args
    $lnk.Description = $Desc
    $lnk.Save()
    Write-OK "Atalho: $Nome"
}

$pyExe = (Get-Command python -ErrorAction SilentlyContinue)?.Source
if ($pyExe -and (Test-Path "$desktop\AuraDashboard\app.py")) {
    New-Lnk -Nome   "AuraDashboard" `
             -Target $pyExe `
             -Args   "-m streamlit run `"$desktop\AuraDashboard\app.py`" --server.port 8501" `
             -Desc   "Inicia o Dashboard Parceiro Isopor"
}

if (Get-Command cmd -ErrorAction SilentlyContinue) {
    if (Test-Path "$desktop\IsoSoluesMKT\index.html") {
        New-Lnk -Nome   "IsoSolues-MKT" `
                 -Target "cmd.exe" `
                 -Args   "/k npx http-server `"$desktop\IsoSoluesMKT`" -p 3000 -o" `
                 -Desc   "Inicia o site IsoSolues MKT localmente"
    }
}

if (Test-Path "$desktop\AuraDashboard\serve.sh") {
    $wt = (Get-Command wt -ErrorAction SilentlyContinue)?.Source
    if ($wt) {
        New-Lnk -Nome   "AuraDashboard Tunel" `
                 -Target $wt `
                 -Args   "-d `"$desktop\AuraDashboard`" bash serve.sh" `
                 -Desc   "Inicia o dashboard + tunel Cloudflare publico"
    }
}

# ─────────────────────────────────────────────
#  10. Resumo final
# ─────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║                  SETUP CONCLUIDO!                     ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""
Write-Host " Dev Tools  :  Git, Python 3.11, Node.js LTS, VS Code, gh" -ForegroundColor White
Write-Host " Tunnel     :  cloudflared (serve.sh pronto)" -ForegroundColor White
Write-Host " Python     :  streamlit, plotly, pandas, Pillow, reportlab" -ForegroundColor White
Write-Host " ASUS [1]   :  DriverHub + Armoury Crate + Chipset + Realtek Audio" -ForegroundColor White
Write-Host " ASUS [2]   :  GPU Tweak III + driver NVIDIA/AMD detectado automaticamente" -ForegroundColor White
Write-Host " Repos      :  Desktop\AuraDashboard  e  Desktop\IsoSoluesMKT" -ForegroundColor White
Write-Host ""
Write-Host " PROXIMOS PASSOS:" -ForegroundColor Yellow
Write-Host "  1. Abra o ASUS DriverHub e clique 'Instalar Todos'" -ForegroundColor Gray
Write-Host "  2. Reinicie o PC para aplicar todos os drivers" -ForegroundColor Gray
Write-Host "  3. Atalho 'AuraDashboard' no Desktop para iniciar o sistema" -ForegroundColor Gray
Write-Host "  4. Para o portal publico: clique 'AuraDashboard Tunel' no Desktop" -ForegroundColor Gray
Write-Host ""
Write-Host " Pressione qualquer tecla para fechar..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
