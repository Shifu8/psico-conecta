param([string]$Region = "us-east-2")

$secretos = @(
    @{name="psicoconecta/GOOGLE_CLIENT_ID"; val="339658076678-8b46grlhh639h3ujsp1fe05bkbqlvnqo.apps.googleusercontent.com"},
    @{name="psicoconecta/GOOGLE_CLIENT_SECRET"; val="GOCSPX-placeholder_google_secret"},
    @{name="psicoconecta/GOOGLE_REFRESH_TOKEN"; val="1//placeholder_refresh_token"},
    @{name="psicoconecta/GOOGLE_SENDER_EMAIL"; val="brandon.medina@unl.edu.ec"},
    @{name="psicoconecta/TURNSTILE_SECRET_KEY"; val="placeholder_turnstile_secret"},
    @{name="psicoconecta/TELECONSULTA_INTERNAL_TOKEN"; val="change_this_internal_service_token"},
    @{name="psicoconecta/PAGOS_INTERNAL_TOKEN"; val="change_this_payments_internal_token"},
    @{name="psicoconecta/ZOOM_ACCOUNT_ID"; val="placeholder_zoom_account_id"},
    @{name="psicoconecta/ZOOM_CLIENT_ID"; val="placeholder_zoom_client_id"},
    @{name="psicoconecta/ZOOM_CLIENT_SECRET"; val="placeholder_zoom_client_secret"},
    @{name="psicoconecta/ZOOM_HOST_USER_ID"; val="placeholder_zoom_host_user_id"},
    @{name="psicoconecta/ZOOM_WEBHOOK_SECRET_TOKEN"; val="placeholder_zoom_webhook_secret"},
    @{name="psicoconecta/STRIPE_SECRET_KEY"; val="sk_test_placeholder_stripe_key"},
    @{name="psicoconecta/STRIPE_WEBHOOK_SECRET"; val="whsec_placeholder_stripe_webhook"}
)

foreach ($s in $secretos) {
    $exists = aws secretsmanager describe-secret --secret-id $($s.name) --region $Region 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $exists) {
        Write-Host "Creando secreto $($s.name)..." -ForegroundColor Yellow
        aws secretsmanager create-secret --name $($s.name) --secret-string $($s.val) --region $Region | Out-Null
        Write-Host "  - $($s.name) creado." -ForegroundColor Green
    } else {
        Write-Host "  - $($s.name) ya existe." -ForegroundColor Gray
    }
}

Write-Host "`nTodos los secretos necesarios estan listos en Secrets Manager." -ForegroundColor Green
