# Define commands for each computer
$big_guy = "ssh the-big-guy@192.168.0.106 'python3 ~/P5/CV-S-emulation/main.py > big_guy.log 2>&1'"
$nano_1 = "ssh comtek550nano@192.168.0.106 'python3 ~/P5/CV-S-emulation/main.py > nano_1.log 2>&1'"
$nano_2 = "ssh jetson-nano@192.168.0.110 'source /media/jetson-nano/Data/comtek550/bin/activate && python3 /media/jetson-nano/Data/CV-S-emulation/main.py > nano_2.log 2>&1'"

# Run commands concurrently
Start-Job -ScriptBlock {Invoke-Expression $using:big_guy}
Start-Job -ScriptBlock {Invoke-Expression $using:nano_1}
Start-Job -ScriptBlock {Invoke-Expression $using:nano_2}

# Wait for all jobs to finish
Get-Job | Wait-Job
Get-Job | Receive-Job

Write-Host "Scripts started on all computers."


