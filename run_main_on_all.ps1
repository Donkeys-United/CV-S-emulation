# Define hosts with specific paths for main.py
$hosts = @(
    @{
        Name = "nano_2"
        User = "jetson-nano"
        IP = "192.168.0.110"
        Path = "/media/jetson-nano/Data/CV-S-emulation/main.py"
        ConfigDir = "/media/jetson-nano/Data/CV-S-emulation"
        Log = "nano_2.log"
        VirtualEnv = "/media/jetson-nano/Data/comtek550/bin/activate"
    },
    @{
        Name = "big_guy"
        User = "the-big-guy"
        IP = "192.168.0.106"
        Path = "~/P5/CV-S-emulation/main.py"
        ConfigDir = "~/P5/CV-S-emulation"
        Log = "big_guy.log"
    },
    @{
        Name = "nano_1"
        User = "comtek550nano"
        IP = "192.168.0.108"
        Path = "~/P5/CV-S-emulation/main.py"
        ConfigDir = "~/P5/CV-S-emulation"
        Log = "nano_1.log"
    }
)

# Function to send config_test.JSON to each host
function Send-ConfigFile {
    $configFilePath = ".\config_test.JSON"
    if (-Not (Test-Path $configFilePath)) {
        Write-Error "Config file not found at $configFilePath"
        return
    }

    foreach ($currentHost in $hosts) {
        Write-Host "Sending config_test.JSON to $($currentHost.Name)..."
        scp $configFilePath "$($currentHost.User)@$($currentHost.IP):$($currentHost.ConfigDir)"
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to send config_test.JSON to $($currentHost.Name)"
        } else {
            Write-Host "Config file sent to $($currentHost.Name)."
        }
    }
}

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

    Send-ConfigFile

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
