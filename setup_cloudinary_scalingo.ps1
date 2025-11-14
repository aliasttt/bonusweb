# PowerShell script to set Cloudinary environment variables in Scalingo
# Usage: .\setup_cloudinary_scalingo.ps1 -ApiSecret "YOUR_API_SECRET" -AppName "your-app-name"
# Or: .\setup_cloudinary_scalingo.ps1 -ApiSecret "YOUR_API_SECRET" (will try to detect from git remote)

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiSecret,
    [Parameter(Mandatory=$false)]
    [string]$AppName = ""
)

# Try to detect app name from git remote if not provided
if ([string]::IsNullOrEmpty($AppName)) {
    Write-Host "Trying to detect app name from git remote..." -ForegroundColor Yellow
    try {
        $gitRemote = git remote get-url scalingo 2>$null
        if ($gitRemote) {
            # Extract app name from scalingo remote URL
            if ($gitRemote -match "scalingo\.com[:/]([^/]+)\.git") {
                $AppName = $matches[1]
                Write-Host "Detected app name: $AppName" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "Could not detect app name from git remote" -ForegroundColor Yellow
    }
}

if ([string]::IsNullOrEmpty($AppName)) {
    Write-Host "Error: App name is required!" -ForegroundColor Red
    Write-Host "Usage: .\setup_cloudinary_scalingo.ps1 -ApiSecret 'YOUR_SECRET' -AppName 'your-app-name'" -ForegroundColor Yellow
    Write-Host "Or set SCALINGO_APP environment variable" -ForegroundColor Yellow
    exit 1
}

Write-Host "Setting Cloudinary environment variables in Scalingo for app: $AppName" -ForegroundColor Cyan
Write-Host ""

scalingo --app $AppName env-set USE_CLOUDINARY=1
scalingo --app $AppName env-set CLOUDINARY_CLOUD_NAME=993373522259225
scalingo --app $AppName env-set CLOUDINARY_API_KEY=G0UxjA_EEAJ9T_BMd9LS6WOdnZo
scalingo --app $AppName env-set CLOUDINARY_API_SECRET=$ApiSecret

Write-Host ""
Write-Host "✅ Cloudinary environment variables set successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Verifying settings..." -ForegroundColor Cyan
scalingo --app $AppName env | Select-String "CLOUDINARY"
Write-Host ""
Write-Host "⚠️  Don't forget to restart your app:" -ForegroundColor Yellow
Write-Host "   scalingo --app $AppName restart" -ForegroundColor White
