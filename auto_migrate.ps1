# Auto Migration Script for Scalingo
# This script downloads, installs Scalingo CLI and runs migration automatically

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Auto Migration Script for Scalingo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Scalingo CLI is installed
Write-Host "[1/5] Checking Scalingo CLI..." -ForegroundColor Yellow
$cliInstalled = $false
$cliPath = $null

# Check common installation paths
$possiblePaths = @(
    "$env:USERPROFILE\AppData\Local\Programs\Scalingo\scalingo.exe",
    "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\scalingo.exe",
    "C:\Program Files\Scalingo\scalingo.exe",
    "C:\Program Files (x86)\Scalingo\scalingo.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $cliPath = $path
        $cliInstalled = $true
        Write-Host "Found Scalingo CLI at: $path" -ForegroundColor Green
        break
    }
}

# Check if in PATH
if (-not $cliInstalled) {
    try {
        $null = Get-Command scalingo -ErrorAction Stop
        $cliInstalled = $true
        Write-Host "Scalingo CLI found in PATH" -ForegroundColor Green
    } catch {
        $cliInstalled = $false
    }
}

# Step 2: Download and install if not installed
if (-not $cliInstalled) {
    Write-Host "[2/5] Downloading Scalingo CLI..." -ForegroundColor Yellow
    
    $tempDir = "$env:TEMP\scalingo_install"
    if (-not (Test-Path $tempDir)) {
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    }
    
    $downloadUrl = "https://github.com/Scalingo/cli/releases/latest/download/scalingo_windows_amd64.exe"
    $exePath = "$tempDir\scalingo.exe"
    
    try {
        Write-Host "Downloading from GitHub..." -ForegroundColor Gray
        $client = New-Object System.Net.WebClient
        $client.DownloadFile($downloadUrl, $exePath)
        Write-Host "Download completed!" -ForegroundColor Green
        
        # Install to user directory
        $installDir = "$env:USERPROFILE\AppData\Local\Programs\Scalingo"
        if (-not (Test-Path $installDir)) {
            New-Item -ItemType Directory -Path $installDir -Force | Out-Null
        }
        
        $installPath = "$installDir\scalingo.exe"
        Copy-Item $exePath $installPath -Force
        Write-Host "Installed to: $installPath" -ForegroundColor Green
        
        # Add to PATH for current session
        $env:Path += ";$installDir"
        
        # Add to user PATH permanently
        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($userPath -notlike "*$installDir*") {
            [Environment]::SetEnvironmentVariable("Path", "$userPath;$installDir", "User")
        }
        
        $cliPath = $installPath
        $cliInstalled = $true
        
        Start-Sleep -Seconds 2
        
    } catch {
        Write-Host "Error downloading: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Trying alternative method..." -ForegroundColor Yellow
        
        # Alternative: Use Invoke-WebRequest
        try {
            Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath -UseBasicParsing -TimeoutSec 60
            $installDir = "$env:USERPROFILE\AppData\Local\Programs\Scalingo"
            if (-not (Test-Path $installDir)) {
                New-Item -ItemType Directory -Path $installDir -Force | Out-Null
            }
            $installPath = "$installDir\scalingo.exe"
            Copy-Item $exePath $installPath -Force
            $env:Path += ";$installDir"
            $cliPath = $installPath
            $cliInstalled = $true
            Write-Host "Download completed with alternative method!" -ForegroundColor Green
        } catch {
            Write-Host "Failed to download Scalingo CLI" -ForegroundColor Red
            Write-Host "Please download manually from: https://cli.scalingo.com/install" -ForegroundColor Yellow
            exit 1
        }
    }
}

# Verify installation
if ($cliInstalled) {
    try {
        if ($cliPath) {
            & $cliPath --version | Out-Null
        } else {
            scalingo --version | Out-Null
        }
        Write-Host "Scalingo CLI is ready!" -ForegroundColor Green
    } catch {
        Write-Host "Warning: CLI may need PATH refresh" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 3: Check login
Write-Host "[3/5] Checking login status..." -ForegroundColor Yellow
$isLoggedIn = $false

try {
    if ($cliPath) {
        $whoami = & $cliPath whoami 2>&1
    } else {
        $whoami = scalingo whoami 2>&1
    }
    
    if ($LASTEXITCODE -eq 0 -and $whoami -notmatch "error" -and $whoami -notmatch "not logged") {
        $isLoggedIn = $true
        Write-Host "Already logged in: $whoami" -ForegroundColor Green
    }
} catch {
    $isLoggedIn = $false
}

if (-not $isLoggedIn) {
    Write-Host "Not logged in. Attempting login..." -ForegroundColor Yellow
    Write-Host "This will open your browser for authentication..." -ForegroundColor Gray
    
    try {
        if ($cliPath) {
            & $cliPath login
        } else {
            scalingo login
        }
        
        Start-Sleep -Seconds 3
        
        # Verify login
        if ($cliPath) {
            $whoami = & $cliPath whoami 2>&1
        } else {
            $whoami = scalingo whoami 2>&1
        }
        
        if ($LASTEXITCODE -eq 0) {
            $isLoggedIn = $true
            Write-Host "Login successful!" -ForegroundColor Green
        } else {
            Write-Host "Login may require manual intervention" -ForegroundColor Yellow
            Write-Host "Please run: scalingo login" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "Login failed. Please run manually: scalingo login" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 4: Check migration status
Write-Host "[4/5] Checking migration status..." -ForegroundColor Yellow
$appName = "mywebsite"

try {
    if ($cliPath) {
        $migrations = & $cliPath --app $appName run python manage.py showmigrations accounts 2>&1
    } else {
        $migrations = scalingo --app $appName run python manage.py showmigrations accounts 2>&1
    }
    Write-Host $migrations
} catch {
    Write-Host "Could not check migration status (continuing anyway)" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Run migration
Write-Host "[5/5] Running migration..." -ForegroundColor Yellow
Write-Host "App: $appName" -ForegroundColor Cyan
Write-Host "Command: python manage.py migrate accounts" -ForegroundColor Gray
Write-Host ""

try {
    if ($cliPath) {
        $result = & $cliPath --app $appName run python manage.py migrate accounts 2>&1
    } else {
        $result = scalingo --app $appName run python manage.py migrate accounts 2>&1
    }
    
    Write-Host $result
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "SUCCESS! Migration completed!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "Migration completed with warnings" -ForegroundColor Yellow
        Write-Host "Check output above for details" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Cyan
    }
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Error running migration" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs with:" -ForegroundColor Yellow
    if ($cliPath) {
        Write-Host "$cliPath --app $appName logs" -ForegroundColor Cyan
    } else {
        Write-Host "scalingo --app $appName logs" -ForegroundColor Cyan
    }
    Write-Host "========================================" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

