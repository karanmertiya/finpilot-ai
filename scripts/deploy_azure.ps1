# ==============================================================================
# FinPilot AI — Automated Azure VM Deployment Script (Central India)
# ==============================================================================
param(
    [string]$ResourceGroupName = "rg-finpilot-prod",
    [string]$Location = "centralindia",
    [string]$VmName = "vm-finpilot-prod",
    [string]$VmSize = "Standard_B2s_v2", # 2 vCPUs, 4GB RAM (Supported in Central India)
    [string]$AdminUsername = "azureuser"
)

$ErrorActionPreference = "Stop"
$azCmd = "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

Write-Host "`n=== [1/5] Verifying Azure Subscription & Account ===" -ForegroundColor Cyan
& $azCmd account show --output table

Write-Host "`n=== [2/5] Creating Resource Group: $ResourceGroupName in $Location ===" -ForegroundColor Cyan
& $azCmd group create --name $ResourceGroupName --location $Location --output table

Write-Host "`n=== [3/5] Creating Virtual Machine: $VmName ($VmSize in $Location) ===" -ForegroundColor Cyan
Write-Host "Image: Ubuntu 24.04 LTS | Generating SSH keys automatically..." -ForegroundColor Yellow

& $azCmd vm create `
    --resource-group $ResourceGroupName `
    --name $VmName `
    --location $Location `
    --image "Canonical:ubuntu-24_04-lts:server:latest" `
    --size $VmSize `
    --zone 1 `
    --admin-username $AdminUsername `
    --generate-ssh-keys `
    --public-ip-sku Standard `
    --output table

Write-Host "`n=== [4/5] Opening Firewall Ports (80 HTTP, 443 HTTPS, 22 SSH) ===" -ForegroundColor Cyan
& $azCmd vm open-port --resource-group $ResourceGroupName --name $VmName --port 80 --priority 1010 --output table
& $azCmd vm open-port --resource-group $ResourceGroupName --name $VmName --port 443 --priority 1020 --output table

Write-Host "`n=== [5/5] Retrieving Public IP Address ===" -ForegroundColor Cyan
$publicIp = & $azCmd vm list-ip-addresses --resource-group $ResourceGroupName --name $VmName --query "[0].virtualMachine.network.publicIpAddresses[0].ipAddress" -o tsv

Write-Host "`n==============================================================================" -ForegroundColor Green
Write-Host " FINPILOT AI AZURE VM DEPLOYED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host " VM Name:        $VmName"
Write-Host " Region:         $Location (Pune, India)"
Write-Host " Public IP:      $publicIp"
Write-Host " SSH Command:    ssh $AdminUsername@$publicIp"
Write-Host ""
Write-Host " DNS RECORDS TO ADD FOR karanmertiya.me:" -ForegroundColor Yellow
Write-Host "   Type: A  |  Host: finpilot      |  Points to: $publicIp" -ForegroundColor White
Write-Host "   Type: A  |  Host: api.finpilot  |  Points to: $publicIp" -ForegroundColor White
Write-Host "==============================================================================`n"
