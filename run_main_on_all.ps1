# Define hosts with specific paths for main.py
$hosts = @(
    @{
        Name = "nano_2"
        User = "jetson-nano"
        IP = "192.168.0.110"
        Path = "/media/jetson-nano/Data/CV-S-emulation/main.py"
        Log = "nano_2.log"
        VirtualEnv = "/media/jetson-nano/Data/comtek550/bin/activate"
    },
    @{
        Name = "big_guy"
        User = "the-big-guy"
        IP = "192.168.0.106"
        Path = "~/P5/CV-S-emulation/main.py"
        Log = "big_guy.log"
    },
    @{
        Name = "nano_1"
        User = "comtek550nano"
        IP = "192.168.0.108"
        Path = "~/P5/CV-S-emulation/main.py"
        Log = "nano_1.log"
    }
)

# Function to start main.py scripts
function Start-MainPyScripts {
    foreach ($currentHost in $hosts) {
        Write-Host "Starting main.py on $($currentHost.Name)..."
        
        if ($currentHost.ContainsKey("VirtualEnv")) {
            ssh "$($currentHost.User)@$($currentHost.IP)" "nohup bash -c 'source $($currentHost.VirtualEnv) && python $($currentHost.Path) > $($currentHost.Log) 2>&1 &' > /dev/null 2>&1 &"
        }
        else {
            # Standard Python execution
            ssh "$($currentHost.User)@$($currentHost.IP)" "nohup python $($currentHost.Path) > $($currentHost.Log) 2>&1 &"
        }
    }
}

# Function to stop all main.py scripts
function Stop-MainPyScripts {
    foreach ($currentHost in $hosts) {
        Write-Host "Stopping main.py on $($currentHost.Name)..."
        ssh "$($currentHost.User)@$($currentHost.IP)" "pgrep -f $($currentHost.Path) | xargs kill -15 || echo 'No process found for $($currentHost.Path)'" 2>&1 | Tee-Object "./$($currentHost.Name)_stop.log"
    }
}

# Function to fetch logs
function Fetch-Logs {
    foreach ($currentHost in $hosts) {
        Write-Host "Fetching logs from $($currentHost.Name)..."
        scp "$($currentHost.User)@$($currentHost.IP):$($currentHost.Log)" "./$($currentHost.Name)_log.txt"
    }
}

# Trap Ctrl+C (BREAK) signal to ensure cleanup
function Stop-finally {
    Write-Host "`nCtrl+C detected. Initiating cleanup..."
    Stop-MainPyScripts
    Fetch-Logs
    Write-Host "Cleanup complete. Logs fetched. Exiting script."
}

try {
# Start the scripts
Start-MainPyScripts

Write-Host "Main.py scripts are running. Press Ctrl+C or close PowerShell to stop them gracefully."

# Keep the script alive until manually terminated

    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Stop-finally
}
