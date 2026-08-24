$taskName = 'Sumo forgetting 3200x2000 20260822'
$start = [datetime]::Today.AddHours(23)

if ($start -le (Get-Date)) {
    throw '23:00 today has already passed.'
}

$python = (Get-Command python).Source

$action = New-ScheduledTaskAction `
    -Execute $python `
    -Argument '-m src.analysis.forgetting.toy.true_start_ensemble --runs 3200 --events 2000 --seed 1' `
    -WorkingDirectory 'X:\Sumo-Tools'

$trigger = New-ScheduledTaskTrigger -Once -At $start

$settings = New-ScheduledTaskSettingsSet `
    -WakeToRun `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 12)

$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal
