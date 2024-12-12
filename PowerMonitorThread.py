import subprocess
from threading import Thread
import TransmissionThread
import sqlite3
import time
import re

class PowerMonitorThread(Thread):
    
    def __init__(self, measuringIntervalms: int, 
                 emulationRunName: str, 
                 unixtimeStart: float, 
                 notes: str, 
                 isNano: bool,
                 transmissionThread: TransmissionThread,
                 satelliteDistance: float):
        
        super().__init__()
        self.PATH_TO_DATABASE = "power_logging.db"
        self.measuringIntervalms = measuringIntervalms
        self.transmissionThread: TransmissionThread = transmissionThread
        
        self.ensureDatabaseIsReady()
        self.conn = sqlite3.connect(self.PATH_TO_DATABASE)
        self.cursor = self.conn.cursor()
        self.runID = self.insertEmulationRun(emulationRunName, unixtimeStart, satelliteDistance, notes)
        
        self.conn.close()
        
        #Check what regular expression we should use since nano and agx have different power rails
        if isNano:
            self.regularExpression = r'VDD_CPU_GPU_CV\s(\d+)mW.*?VDD_SOC\s(\d+)mW'
        else:
            self.regularExpression = r'VDD_GPU_SOC\s(\d+)mW.*?VDD_CPU_CV\s(\d+)mW'
    
    def ensureDatabaseIsReady(self):
        conn = sqlite3.connect(self.PATH_TO_DATABASE)
        cursor = conn.cursor()
        
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS emulation_runs (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               name TEXT,
                               unix_start_time FLOAT,
                               satellite_distance_m FLOAT,
                               notes TEXT
                           )
                           """)
            
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS power_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            run_id INTEGER,
                            unix_timestamp FLOAT,
                            power_consumption_mw INTEGER,
                            data_sent_bytes INTEGER
                        )
                        """)
            
        conn.commit()
        conn.close()
        
    
    def insertEmulationRun(self, name: str, unixTime: float,satteliteDistance: float, notes: str):
        """
        Inserts a new emulation run into the database.
        """

        self.cursor.execute("INSERT INTO emulation_runs (name, unix_start_time, satellite_distance_m, notes) VALUES (?, ?, ?, ?);", (name, unixTime, satteliteDistance, notes))

        self.conn.commit()

        run_id = self.cursor.lastrowid  # Retrieve the ID of the newly inserted run

        return run_id

    def insertPowerLog(self, runID: int, timestamp: float, powerConsumption: int, data_sent_bytes: int):
        """
        Inserts power measurement into the data base
        """
        self.cursor.execute("INSERT INTO power_logs (run_id, unix_timestamp, power_consumption_mw, data_sent_bytes) VALUES (?, ?, ?, ?);", 
        (runID, timestamp, powerConsumption, data_sent_bytes))
        
        self.conn.commit()

    
    def parseTegrastatsOutput(self, output):
        """
        Parses the output of tegra stats
        """
        match = re.search(self.regularExpression, output)
        if match:
            return int(match.group(1)) + int(match.group(2))   # Power in mW
        return None
    
    def run(self):
        # Run tegrastats with the specified interval
        cmd = ["tegrastats", f"--interval", str(self.measuringIntervalms)]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        #Overwrite the connections and cursor as the previous ones where made in another thread
        self.conn = sqlite3.connect(self.PATH_TO_DATABASE)
        self.cursor = self.conn.cursor()

        try:
            while True:
                sampleStart = time.time()
                line = process.stdout.readline()
                if not line:
                    break
                power = self.parseTegrastatsOutput(line)
                if power is not None:
                    self.insertPowerLog(self.runID, sampleStart, power, self.transmissionThread.getDataTransmitted())
                
                #Ensure consistent sampling
                sleepTime = self.measuringIntervalms/1000 - (time.time()-sampleStart)
                if sleepTime < 0:
                    continue
                time.sleep(sleepTime)  
        except KeyboardInterrupt:
            print("Monitoring stopped.")
        finally:
            process.terminate()
            self.conn.close()


if __name__ == "__main__":
    powerMonitor = PowerMonitorThread(40,"Stuff", 0, "hi", True)
    powerMonitor.start()
    powerMonitor.join()