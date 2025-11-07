# Complete script to install Scalingo CLI and run migration
# Run this script as Administrator for best results

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installing Scalingo CLI and Running Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Warning: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some operations may require admin rights" -ForegroundColor Yellow
    Write-Host ""
}

# Step 1: Check if Scalingo CLI is already installed
Write-Host "Step 1: Checking if Scalingo CLI is installed..." -ForegroundColor Yellow
$cliInstalled = $false
try {
    $version = scalingo --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Scalingo CLI is already installed!" -ForegroundColor Green
        Write-Host "Version: $version" -ForegroundColor Gray
        $cliInstalled = $true
    }
} catch {
    $cliInstalled = $false
}

# Step 2: Download and install if not installed
if (-not $cliInstalled) {
    Write-Host ""
    Write-Host "Step 2: Downloading Scalingo CLI..." -ForegroundColor Yellow
    
    # Create temp directory
    $tempDir = "$env:TEMP\scalingo_install"
    if (-not (Test-Path $tempDir)) {
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    }
    
    $downloadUrl = "https://github.com/Scalingo/cli/releases/latest/download/scalingo_windows_amd64.exe"
    $exePath = "$tempDir\scalingo.exe"
    
    try {
        Write-Host "Downloading from: $downloadUrl" -ForegroundColor Gray
        Invoke-WebRequest -Uri $downloadUrl -OutFile $exePath -UseBasicParsing -ErrorAction Stop
        
        Write-Host "Download completed!" -ForegroundColor Green
        Write-Host ""
        
        # Install to a location in PATH
        $installDir = "$env:USERPROFILE\AppData\Local\Programs\Scalingo"
        if (-not (Test-Path $installDir)) {
            New-Item -ItemType Directory -Path $installDir -Force | Out-Null
        }
        
        $installPath = "$installDir\scalingo.exe"
        Copy-Item $exePath $installPath -Force
        
        Write-Host "Installing to: $installPath" -ForegroundColor Gray
        
        # Add to PATH for current user
        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($userPath -notlike "*$installDir*") {
            [Environment]::SetEnvironmentVariable("Path", "$userPath;$installDir", "User")
            Write-Host "Added to PATH" -ForegroundColor Green
        }
        
        # Add to current session PATH
        $env:Path += ";$installDir"
        
        Write-Host "Installation completed!" -ForegroundColor Green
        Write-Host ""
        
        # Verify installation
        Start-Sleep -Seconds 2
        try {
            $version = scalingo --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "Verification: Scalingo CLI is working!" -ForegroundColor Green
                Write-Host "Version: $version" -ForegroundColor Gray
            } else {
                Write-Host "Warning: Installation may need PowerShell restart" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Warning: Please restart PowerShell and run the script again" -ForegroundColor Yellow
            Write-Host "Or manually add to PATH: $installDir" -ForegroundColor Cyan
        }
        
    } catch {
        Write-Host "Error downloading/installing Scalingo CLI" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install manually:" -ForegroundColor Yellow
        Write-Host "1. Go to: https://cli.scalingo.com/install" -ForegroundColor Cyan
        Write-Host "2. Download and run the installer" -ForegroundColor Cyan
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 3: Checking login status..." -ForegroundColor Yellow

# Step 3: Check login
try {
    $whoami = scalingo whoami 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "You are logged in!" -ForegroundColor Green
        Write-Host "User: $whoami" -ForegroundColor Gray
    } else {
        Write-Host "You are not logged in" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Please login to Scalingo..." -ForegroundColor Cyan
        Write-Host "This will open your browser for authentication" -ForegroundColor Gray
        Write-Host ""
        
        scalingo login
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Login failed. Please try manually: scalingo login" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "Error checking login. Please run: scalingo login" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 4: Running migration..." -ForegroundColor Yellow

# Step 4: Run migration
$appName = "mywebsite"
Write-Host "App name: $appName" -ForegroundColor Cyan
Write-Host ""

# Check migration status first
Write-Host "Checking migration status..." -ForegroundColor Gray
try {
    scalingo --app $appName run python manage.py showmigrations accounts 2>&1 | Out-Null
} catch {
    Write-Host "Could not check migration status (continuing anyway)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Running migration: python manage.py migrate accounts" -ForegroundColor Yellow
Write-Host "This may take a few moments..." -ForegroundColor Gray
Write-Host ""

try {
    $result = scalingo --app $appName run python manage.py migrate accounts 2>&1
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
        Write-Host "Check the output above for details" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Cyan
    }
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Error running migration" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Check logs with:" -ForegroundColor Yellow
    Write-Host "scalingo --app $appName logs" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    exit 1
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green

