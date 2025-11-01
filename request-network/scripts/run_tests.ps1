# اسکریپت اجرای تست‌ها
$ErrorActionPreference = "Stop"

Write-Host "شروع اجرای تست‌ها..." -ForegroundColor Green

# فعال‌سازی محیط مجازی
if (Test-Path ".venv") {
    Write-Host "فعال‌سازی محیط مجازی..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "محیط مجازی یافت نشد. لطفاً ابتدا آن را ایجاد کنید." -ForegroundColor Red
    exit 1
}

# اجرای تست‌ها با pytest
try {
    Write-Host "اجرای تست‌ها با pytest..." -ForegroundColor Yellow
    pytest tests/ -v --cov=api --cov-report=term-missing
} catch {
    Write-Host "خطا در اجرای تست‌ها:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

Write-Host "تست‌ها با موفقیت اجرا شدند." -ForegroundColor Green