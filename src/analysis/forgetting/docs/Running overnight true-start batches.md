# Running overnight true-start batches

This note records how to size and schedule large runs of the fixed-skill
true-start ensemble on Windows. Run all commands from PowerShell.

## Command

From the repository root, the canonical 3,200-replicate, 2,000-event batch is:

```powershell
python -m src.analysis.forgetting.toy.true_start_ensemble --runs 3200 --events 2000 --seed 1
```

The master seed defaults to `1`, but it is stated explicitly for the audit
record. Each replicate receives a different seed derived deterministically
from this master seed.

Outputs are written beneath:

```text
files/output/analysis/forgetting/toy/true_start_ensemble/
```

Each run creates its own timestamped directory. The report and `manifest.json`
persist the elapsed wall-clock time, run parameters, start time, and finish
time.

## Current runtime estimate

Measurements made on 22 August 2026 fit the following current-code estimate:

```text
seconds = 35 × (replicates / 100) × (events / 500)^2
```

For 3,200 replicates and 2,000 events this gives approximately 17,920 seconds,
or five hours. A 23:00 start should therefore finish at about 04:00.

The linear replicate scaling and quadratic event scaling have both been
observed directly. The quadratic event cost is an implementation artefact in
history validation, rather than a necessary property of the simulation. This
formula must be re-estimated if that validation is optimized.

## Current storage and memory estimates

The output contains approximately:

```text
replicate-event records = replicates × (events + 1)
```

The on-disk requirement is approximately:

```text
output bytes = 80 × replicates × (events + 1)
```

The 3,200 × 2,000 run therefore produces about 6.4 million records and roughly
0.48 GiB of output. A conservative peak-memory allowance is 0.75--1 KiB per
record, or approximately 5--6 GiB for this batch.

At the time of measurement the computer had 63.27 GiB of physical RAM, of
which 33.25 GiB was available while no experiment was running. Drive `X:` had
approximately 2,677 GiB free. The 3,200 × 2,000 batch is consequently within
the practical limits of the current implementation.

These figures are estimates, not enforced resource limits. Other applications
left running overnight reduce the available-memory margin.

## Schedule a 23:00 run

Run the following block once before 23:00 on the day the batch should start:

```powershell
$taskName = 'Sumo forgetting 3200x2000 ' + (Get-Date -Format 'yyyyMMdd')
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
```

The task uses the absolute path of the `python` command available when it is
registered and fixes the working directory to the repository root.

The user must remain logged in, although the computer may be locked. The
`WakeToRun` setting requests that Windows wake the computer from sleep, subject
to its power and firmware settings.

## Verify the scheduled task

In the same PowerShell session, inspect the task with:

```powershell
Get-ScheduledTask -TaskName $taskName
Get-ScheduledTaskInfo -TaskName $taskName
```

Check that `NextRunTime` is 23:00 on the intended date.

The following command can be used in a later PowerShell session, substituting
the actual task name shown by Task Scheduler:

```powershell
Get-ScheduledTaskInfo -TaskName 'Sumo forgetting 3200x2000 20260822'
```

## Completion and cleanup

Successful completion creates the timestamped output directory described
above. Its `manifest.json` contains the authoritative parameters and elapsed
time.

The one-time Windows task remains registered after it finishes. Remove it with:

```powershell
Unregister-ScheduledTask -TaskName $taskName
```

PowerShell asks for confirmation before unregistering it. Removing the
scheduled task does not remove the experiment outputs.

