# Add Scalingo CLI to PATH for current session
$installDir = "$env:USERPROFILE\AppData\Local\Programs\Scalingo"
$env:Path += ";$installDir"
Write-Host "Scalingo CLI added to PATH for this session" -ForegroundColor Green
Write-Host "Path: $installDir" -ForegroundColor Gray
Write-Host ""
Write-Host "Now you can use 'scalingo' command" -ForegroundColor Green
Write-Host ""
Write-Host "Test with: scalingo --version" -ForegroundColor Cyan

