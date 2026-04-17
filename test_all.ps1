# Smart Stadium OS — Unified Test Suite Runner
# ==========================================
# Run this from the root to verify full Elite-tier compliance.

Write-Host "🚀 Initializing Smart Stadium Test Suite..." -ForegroundColor Cyan

# 1. Backend Tests (Pytest)
Write-Host "`n🧪 Running Backend Integration & Unit Tests..." -ForegroundColor Yellow
cd smart-stadium-os/backend
pytest --cov=services --cov=routes --cov=models --cov-report=term-missing
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Backend tests failed!" -ForegroundColor Red
    exit 1
}
cd ../..

# 2. Frontend Tests (Vitest)
Write-Host "`n🎨 Running Frontend Component & Accessibility Tests..." -ForegroundColor Yellow
cd smart-stadium-os/frontend
npm test -- --run
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend tests failed!" -ForegroundColor Red
    exit 1
}
cd ../..

Write-Host "`n✅ ALL TESTS PASSED. SYSTEM STATUS: ELITE." -ForegroundColor Green
