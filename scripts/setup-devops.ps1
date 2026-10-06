param([Parameter(Mandatory)][string]$Organization,[Parameter(Mandatory)][string]$ServiceConnection,[Parameter(Mandatory)][string]$SubscriptionId,[Parameter(Mandatory)][string]$AppName,[Parameter(Mandatory)][string]$StateStorageAccount,[string]$Project='DailyCalculator',[string]$Location='centralindia')
$ErrorActionPreference='Stop'
if ($Organization -notmatch '^https://dev\.azure\.com/[^/]+/?$') { throw 'Use an exact https://dev.azure.com/ORGANIZATION URL' }
$remote=az repos list --organization $Organization --project $Project --query "[?name=='daily-calorie-calculator'].remoteUrl | [0]" -o tsv
if (-not $remote) { $remote=az repos create --organization $Organization --project $Project --name daily-calorie-calculator --query remoteUrl -o tsv }
if ($LASTEXITCODE -ne 0) { throw 'Could not find or create the repository' }
Write-Host "Repository: $remote"
Write-Host 'Push this project to main, create a federated service connection, then configure the pipeline variables:'
Write-Host "azureServiceConnection=$ServiceConnection; subscriptionId=$SubscriptionId; appName=$AppName; azureLocation=$Location; stateStorageAccount=$StateStorageAccount"
