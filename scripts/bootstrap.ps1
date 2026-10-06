param([Parameter(Mandatory)][string]$SubscriptionId,[Parameter(Mandatory)][string]$StorageName,[string]$Location='centralindia')
$ErrorActionPreference='Stop'
az account set --subscription $SubscriptionId
if ($LASTEXITCODE -ne 0) { throw 'Could not select subscription' }
terraform -chdir=infra/bootstrap init
if ($LASTEXITCODE -ne 0) { throw 'Terraform init failed' }
terraform -chdir=infra/bootstrap apply "-var=subscription_id=$SubscriptionId" "-var=storage_name=$StorageName" "-var=location=$Location" -auto-approve
if ($LASTEXITCODE -ne 0) { throw 'Backend bootstrap failed' }
az storage container create --account-name $StorageName --name tfstate --auth-mode login
if ($LASTEXITCODE -ne 0) { throw 'Could not create the state container' }
@"
resource_group_name = "daily-calculator-tfstate-rg"
storage_account_name = "$StorageName"
container_name = "tfstate"
key = "daily-calculator/app.tfstate"
use_azuread_auth = true
"@ | Set-Content infra/backend.hcl
terraform -chdir=infra init -backend-config=backend.hcl
if ($LASTEXITCODE -ne 0) { throw 'App backend init failed' }
