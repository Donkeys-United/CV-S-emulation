import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from RadioEnergy import RadioEnergy

DB_PATH = '../power_logging.db'
POWER_LOGGING_INTERVAL = 0.04

def get_data_from_db(db_path, run_id):
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT id, run_id, unix_timestamp, power_consumption_mw, data_sent_bytes
    FROM power_logs
    WHERE run_id = {run_id}
    """ 
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

data = get_data_from_db(DB_PATH,89)

data["data_was_sent"] = data['data_sent_bytes'] != data["data_sent_bytes"].shift(1)
data_sent_indices = data[data["data_was_sent"]].index
data["data_sent_difference"] = data["data_sent_bytes"].diff()
print(data["data_was_sent"])
print(data["data_sent_difference"][0])
print(data_sent_indices)



data["energy"] = (data["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL


for i in data_sent_indices[1:]:
    data.loc[i, "energy"] += data.loc[i, "energy"] +  RadioEnergy.getEnergyForTransmission(22094040.101391997, data.loc[i, "data_sent_difference"]) 

data["cumulative_energy"] = data["energy"].cumsum()

plt.figure(figsize=(12, 6))
plt.plot(data.index*POWER_LOGGING_INTERVAL, data['cumulative_energy'], label=f'Run 89')
plt.title(f'Cumulative Energy Consumption for Run 89')
plt.xlabel('Time (s)')
plt.ylabel('Cumulative Energy (J)')
plt.legend()
plt.grid()
plt.tight_layout()

# Step 6: Show or Save Plot
plt.show()