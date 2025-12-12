# Start Web Server
# Run this script to launch the pedestrian navigation web application

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  PEDESTRIAN NAVIGATION WEB SERVER - STARTUP" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
$currentDir = Get-Location
Write-Host "[1/4] Checking directory..." -ForegroundColor Yellow
Write-Host "      Current: $currentDir" -ForegroundColor Gray

# Navigate to project directory
$projectDir = "c:\Users\N\Desktop\FINAL_YEAR_PROJECT\pedestrian-navigation-esp32cam\web_app"
if (Test-Path $projectDir) {
    Set-Location $projectDir
    Write-Host "      Changed to: $projectDir" -ForegroundColor Green
} else {
    Write-Host "      ERROR: Project directory not found!" -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host ""
Write-Host "[2/4] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "      $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "      ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host ""
Write-Host "[3/4] Checking dependencies..." -ForegroundColor Yellow
$packages = @("Flask", "flask_socketio", "flask_cors")
$allInstalled = $true

foreach ($package in $packages) {
    $result = python -c "import $package; print('OK')" 2>&1
    if ($result -eq "OK") {
        Write-Host "      $package... OK" -ForegroundColor Green
    } else {
        Write-Host "      $package... MISSING" -ForegroundColor Red
        $allInstalled = $false
    }
}

if (-not $allInstalled) {
    Write-Host ""
    Write-Host "Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Start server
Write-Host ""
Write-Host "[4/4] Starting web server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SERVER STARTING" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Green
Write-Host "  Map Interface:  http://localhost:5000" -ForegroundColor White
Write-Host "  Dashboard:      http://localhost:5000/dashboard" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run server
python server.py
