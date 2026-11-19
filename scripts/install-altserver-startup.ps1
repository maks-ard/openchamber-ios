param(
    [string]$Executable = (Join-Path $PSScriptRoot '../.tools/altstore/AltServer/AltServer.exe'),
    [switch]$StartNow
)
$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run this script as administrator. No Apple credentials are needed.'
}
$resolved = (Resolve-Path -LiteralPath $Executable).Path
if ([IO.Path]::GetFileName($resolved) -ne 'AltServer.exe') { throw 'Expected AltServer.exe' }
$taskName = 'OpenChamber AltServer'
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing -and (@($existing.Actions).Count -ne 1 -or $existing.Actions[0].Execute -ne $resolved)) {
    throw 'An unrelated task already uses this name; no changes were made.'
}
$action = New-ScheduledTaskAction -Execute $resolved -WorkingDirectory (Split-Path $resolved)
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $identity.Name
$taskPrincipal = New-ScheduledTaskPrincipal -UserId $identity.Name -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -StartWhenAvailable
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Principal $taskPrincipal -Settings $settings -Description 'Run AltServer for local iPhone application signature refresh.' -Force | Out-Null
Write-Output "Installed task: $taskName"
if ($StartNow) {
    Get-Process AltServer -ErrorAction SilentlyContinue |
        Where-Object { $_.Path -eq $resolved } | Stop-Process
    Start-ScheduledTask -TaskName $taskName
    Write-Output 'Started AltServer through the scheduled task.'
}
