param(
	[string] $BaseUrl = "http://localhost:8000",
	[Parameter(Mandatory = $false)] [string] $ApiKey,
	[Parameter(Mandatory = $false)] [string] $Secret,
	[string] $OrderId = ("ORD-" + (Get-Random -Minimum 10000 -Maximum 99999)),
	[string] $Amount = "49.00",
	[string] $Currency = "USD",
	[string] $CustomerEmail = "buyer@example.com",
	[string] $SuccessUrl = "https://merchant.example/success",
	[string] $CancelUrl = "https://merchant.example/cancel",
	[string] $WebhookUrl = "https://merchant.example/api/paycrypt/webhook",
	[switch] $OpenCheckout
)

# Purpose: Smoke test the /api/v1/payment_sessions flow with HMAC headers
# - Creates a payment session and prints id + checkout_url
# - Fetches the session details
# - Optionally opens the checkout page in your default browser

function Ensure-Value {
	param([string]$Name, [string]$Value)
	if (-not $Value -or $Value.Trim() -eq "") {
		return Read-Host "Enter $Name"
	}
	return $Value
}

$ApiKey  = Ensure-Value -Name "API Key (X-Paycrypt-Key)" -Value $ApiKey
$Secret  = Ensure-Value -Name "Secret (used to compute X-Paycrypt-Signature)" -Value $Secret

Write-Host "BaseUrl:" $BaseUrl -ForegroundColor Cyan
Write-Host "OrderId:" $OrderId -ForegroundColor Cyan

# Build JSON body
$bodyObj = [ordered]@{
	order_id     = $OrderId
	amount       = $Amount
	currency     = $Currency.ToUpper()
	customer     = @{ email = $CustomerEmail }
	metadata     = @{ source = "ps1-smoketest" }
	success_url  = $SuccessUrl
	cancel_url   = $CancelUrl
	webhook_url  = $WebhookUrl
}
$body = ($bodyObj | ConvertTo-Json -Depth 6 -Compress)

# Compute HMAC-SHA256 over "<ts>.<body>" using UTF-8 bytes of Secret
$ts = [int][DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$message = "$ts.$body"

$secretBytes = [Text.Encoding]::UTF8.GetBytes($Secret)
$hmac = New-Object System.Security.Cryptography.HMACSHA256($secretBytes)
$msgBytes = [Text.Encoding]::UTF8.GetBytes($message)
$sigBytes = $hmac.ComputeHash($msgBytes)
$sig = -join ($sigBytes | ForEach-Object { $_.ToString("x2") })

$headers = @{
	"X-Paycrypt-Key"       = $ApiKey
	"X-Paycrypt-Timestamp" = $ts
	"X-Paycrypt-Signature" = $sig
	"Content-Type"         = "application/json"
}

$createUrl = "$BaseUrl/api/v1/payment_sessions"
Write-Host "POST $createUrl" -ForegroundColor Yellow
try {
	$resp = Invoke-RestMethod -Method POST -Uri $createUrl -Headers $headers -Body $body -TimeoutSec 30
} catch {
	Write-Error "Create session failed: $($_.Exception.Message)"
	if ($_.Exception.Response -and $_.Exception.Response.GetResponseStream) {
		$sr = New-Object System.IO.StreamReader ($_.Exception.Response.GetResponseStream())
		$errBody = $sr.ReadToEnd()
		Write-Host $errBody -ForegroundColor Red
	}
	exit 1
}

Write-Host "Created session:" (ConvertTo-Json $resp -Depth 6) -ForegroundColor Green
if (-not $resp.id -or -not $resp.checkout_url) {
	Write-Error "Unexpected response. Missing id/checkout_url."
	exit 1
}

$getUrl = "$BaseUrl/api/v1/payment_sessions/$($resp.id)"
Write-Host "GET $getUrl" -ForegroundColor Yellow
try {
	$detail = Invoke-RestMethod -Method GET -Uri $getUrl -TimeoutSec 30
	Write-Host "Session details:" (ConvertTo-Json $detail -Depth 6) -ForegroundColor Green
} catch {
	Write-Warning "Fetch session failed: $($_.Exception.Message)"
}

if ($OpenCheckout) {
	Write-Host "Opening checkout: $($resp.checkout_url)" -ForegroundColor Cyan
	Start-Process $resp.checkout_url | Out-Null
}

Write-Host "Done." -ForegroundColor Green
