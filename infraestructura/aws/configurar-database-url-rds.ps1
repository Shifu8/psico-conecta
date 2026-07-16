param(
    [string]$Region = "us-east-2",
    [string]$SecretName = "psicoconecta/DATABASE_URL"
)

$ErrorActionPreference = "Stop"

Write-Host "Configurar DATABASE_URL para PsicoConecta" -ForegroundColor Green
Write-Host "Usa la RDS PostgreSQL existente. No se creara una base nueva." -ForegroundColor Yellow
Write-Host "Formato: postgresql+psycopg://USUARIO:CONTRASENA@ENDPOINT_RDS:5432/psicoconecta" -ForegroundColor Cyan

$secureValue = Read-Host "Pega DATABASE_URL" -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureValue)
try {
    $databaseUrl = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr).Trim()
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

if (-not $databaseUrl.StartsWith("postgresql+psycopg://")) {
    throw "DATABASE_URL debe iniciar con postgresql+psycopg://"
}
if ($databaseUrl -match "localhost|127\.0\.0\.1|sqlite") {
    throw "DATABASE_URL apunta a local/SQLite. Debe ser el endpoint RDS existente."
}

$tempFile = [System.IO.Path]::GetTempFileName()
try {
    Set-Content -LiteralPath $tempFile -Value $databaseUrl -NoNewline -Encoding ascii
    $exists = aws secretsmanager describe-secret --secret-id $SecretName --region $Region 2>$null
    if ($LASTEXITCODE -eq 0 -and $exists) {
        aws secretsmanager put-secret-value --secret-id $SecretName --secret-string "file://$tempFile" --region $Region | Out-Null
        Write-Host "Se actualizo el secreto $SecretName." -ForegroundColor Green
    } else {
        aws secretsmanager create-secret --name $SecretName --secret-string "file://$tempFile" --region $Region | Out-Null
        Write-Host "Se creo el secreto $SecretName." -ForegroundColor Green
    }
} finally {
    Remove-Item -LiteralPath $tempFile -Force -ErrorAction SilentlyContinue
}

Write-Host "DATABASE_URL quedo guardado en Secrets Manager sin imprimir el valor." -ForegroundColor Green
