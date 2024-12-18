import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from RadioEnergy import RadioEnergy

def plot_with_values(ax, labels, values, title):
    bars = ax.bar(labels, values)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f'{value:.2f}',
            ha='center',
            va='bottom'
        )
    ax.set_ylabel("Energy Consumption (Joules)")
    ax.set_xlabel("Test Run")
    ax.set_title(title)

name_list_D5=["Dist_5_1", "Dist_5_2", "Dist_5_3"]
name_list_D50=["Dist_50_1", "Dist_50_2", "Dist_50_3"]
name_list_GS5=["GS_5_1", "GS_5_2", "GS_5_3"]
name_list_GS50=["GS_50_1", "GS_50_2", "GS_50_3"]
name_list_L5=["Local_5_1", "Local_5_2", "Local_5_3"]
name_list_L50=["Local_50_1", "Local_50_2", "Local_50_3"]


run_id_list_D5 = [(156, 157, 168), (157, 158, 169), (158, 159, 170)] #Dist_5_x
run_id_list_D50 = [(168, 169, 181), (161, 162, 173), (159, 160, 171)] #Dist_50_x
run_id_list_GS5 = [(162, 163, 174), (163, 164, 176), (164, 165, 177)] #GS_5_x
run_id_list_GS50 = [(165, 166, 178), (166, 167, 179), (167, 168, 180)] #GS_50_x
run_id_list_L5 = [(144, 145, 155), (145, 146, 157), (146, 147, 158)] #Local_5_x
run_id_list_L50 = [(147, 148, 159), (151, 152, 163), (149, 150, 161)] #Local_50_x

BIG_GUY_DB_PATH = 'big_guy_power_logging.db'
NANO_1_DB_PATH = 'nano_1_power_logging.db'
NANO_2_DB_PATH = 'nano_2_power_logging.db'
POWER_LOGGING_INTERVAL = 0.04
fig, ax = plt.subplots()
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

power_list_D5 = []
for i in run_id_list_D5:
    data_big = get_data_from_db(BIG_GUY_DB_PATH,i[0])
    data_big["energy"] = (data_big["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_big["cumulative_energy"] = data_big["energy"].cumsum()

    data_nano1 = get_data_from_db(NANO_1_DB_PATH,i[1])
    data_nano1["energy"] = (data_nano1["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano1["cumulative_energy"] = data_nano1["energy"].cumsum()
    
    data_nano2 = get_data_from_db(NANO_2_DB_PATH,i[2])
    data_nano2["energy"] = (data_nano2["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano2["cumulative_energy"] = data_nano2["energy"].cumsum()
    
    big_power = data_big["cumulative_energy"].max()
    nano1_power = data_nano1["cumulative_energy"].max()
    nano2_power = data_nano2["cumulative_energy"].max()


    big_power += RadioEnergy.getEnergyForTransmission(2588000, (data_big['data_sent_bytes'].max()*4)) * 7
    nano1_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano1['data_sent_bytes'].max()*4)) 
    nano2_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano2['data_sent_bytes'].max()*4)) * 7 

    total_power = big_power + nano1_power + nano2_power
    power_list_D5.append(total_power)


ax.bar(name_list_D5, power_list_D5)

power_list_GS5 = []
for i in run_id_list_GS5:
    data_big = get_data_from_db(BIG_GUY_DB_PATH,i[0])
    data_big["energy"] = (data_big["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_big["cumulative_energy"] = data_big["energy"].cumsum()

    data_nano1 = get_data_from_db(NANO_1_DB_PATH,i[1])
    data_nano1["energy"] = (data_nano1["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano1["cumulative_energy"] = data_nano1["energy"].cumsum()
    
    data_nano2 = get_data_from_db(NANO_2_DB_PATH,i[2])
    data_nano2["energy"] = (data_nano2["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano2["cumulative_energy"] = data_nano2["energy"].cumsum()
    
    big_power = data_big["cumulative_energy"].max()
    nano1_power = data_nano1["cumulative_energy"].max()
    nano2_power = data_nano2["cumulative_energy"].max()


    big_power += RadioEnergy.getEnergyForTransmission(2588000, (data_big['data_sent_bytes'].max()*4)) * 7
    nano1_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano1['data_sent_bytes'].max()*4)) 
    nano2_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano2['data_sent_bytes'].max()*4)) * 7 

    total_power = big_power + nano1_power + nano2_power
    power_list_GS5.append(total_power)

ax.bar(name_list_GS5, power_list_GS5)

power_list_L5 = []
for i in run_id_list_L5:
    data_big = get_data_from_db(BIG_GUY_DB_PATH,i[0])
    data_big["energy"] = (data_big["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_big["cumulative_energy"] = data_big["energy"].cumsum()

    data_nano1 = get_data_from_db(NANO_1_DB_PATH,i[1])
    data_nano1["energy"] = (data_nano1["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano1["cumulative_energy"] = data_nano1["energy"].cumsum()
    
    data_nano2 = get_data_from_db(NANO_2_DB_PATH,i[2])
    data_nano2["energy"] = (data_nano2["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano2["cumulative_energy"] = data_nano2["energy"].cumsum()
    
    big_power = data_big["cumulative_energy"].max()
    nano1_power = data_nano1["cumulative_energy"].max()
    nano2_power = data_nano2["cumulative_energy"].max()


    big_power += RadioEnergy.getEnergyForTransmission(2588000, (data_big['data_sent_bytes'].max()*4)) * 7
    nano1_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano1['data_sent_bytes'].max()*4)) 
    nano2_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano2['data_sent_bytes'].max()*4)) * 7 

    total_power = big_power + nano1_power + nano2_power
    power_list_L5.append(total_power)


plot_with_values(ax, name_list_D5, power_list_D5, "Test with 5 Images")
plot_with_values(ax, name_list_GS5, power_list_GS5, "Test with 5 Images")

plot_with_values(ax, name_list_L5, power_list_L5, "Test with 5 Images")


plt.show()

fig, ax = plt.subplots()


power_list_D50 = []
for i in run_id_list_D50:
    data_big = get_data_from_db(BIG_GUY_DB_PATH,i[0])
    data_big["energy"] = (data_big["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_big["cumulative_energy"] = data_big["energy"].cumsum()

    data_nano1 = get_data_from_db(NANO_1_DB_PATH,i[1])
    data_nano1["energy"] = (data_nano1["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano1["cumulative_energy"] = data_nano1["energy"].cumsum()
    
    data_nano2 = get_data_from_db(NANO_2_DB_PATH,i[2])
    data_nano2["energy"] = (data_nano2["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano2["cumulative_energy"] = data_nano2["energy"].cumsum()
    
    big_power = data_big["cumulative_energy"].max()
    nano1_power = data_nano1["cumulative_energy"].max()
    nano2_power = data_nano2["cumulative_energy"].max()


    big_power += RadioEnergy.getEnergyForTransmission(2588000, (data_big['data_sent_bytes'].max()*4)) * 7
    nano1_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano1['data_sent_bytes'].max()*4)) 
    nano2_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano2['data_sent_bytes'].max()*4)) * 7 

    total_power = big_power + nano1_power + nano2_power
    power_list_D50.append(total_power)



power_list_GS50 = []
for i in run_id_list_GS50:
    data_big = get_data_from_db(BIG_GUY_DB_PATH,i[0])
    data_big["energy"] = (data_big["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_big["cumulative_energy"] = data_big["energy"].cumsum()

    data_nano1 = get_data_from_db(NANO_1_DB_PATH,i[1])
    data_nano1["energy"] = (data_nano1["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano1["cumulative_energy"] = data_nano1["energy"].cumsum()
    
    data_nano2 = get_data_from_db(NANO_2_DB_PATH,i[2])
    data_nano2["energy"] = (data_nano2["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano2["cumulative_energy"] = data_nano2["energy"].cumsum()
    
    big_power = data_big["cumulative_energy"].max()
    nano1_power = data_nano1["cumulative_energy"].max()
    nano2_power = data_nano2["cumulative_energy"].max()


    big_power += RadioEnergy.getEnergyForTransmission(2588000, (data_big['data_sent_bytes'].max()*4)) * 7
    nano1_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano1['data_sent_bytes'].max()*4)) 
    nano2_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano2['data_sent_bytes'].max()*4)) * 7

    total_power = big_power + nano1_power + nano2_power
    power_list_GS50.append(total_power)


power_list_L50 = []
for i in run_id_list_L50:
    data_big = get_data_from_db(BIG_GUY_DB_PATH,i[0])
    data_big["energy"] = (data_big["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_big["cumulative_energy"] = data_big["energy"].cumsum()

    data_nano1 = get_data_from_db(NANO_1_DB_PATH,i[1])
    data_nano1["energy"] = (data_nano1["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano1["cumulative_energy"] = data_nano1["energy"].cumsum()
    
    data_nano2 = get_data_from_db(NANO_2_DB_PATH,i[2])
    data_nano2["energy"] = (data_nano2["power_consumption_mw"] / 1000) * POWER_LOGGING_INTERVAL
    data_nano2["cumulative_energy"] = data_nano2["energy"].cumsum()
    
    big_power = data_big["cumulative_energy"].max()
    nano1_power = data_nano1["cumulative_energy"].max()
    nano2_power = data_nano2["cumulative_energy"].max()


    big_power += RadioEnergy.getEnergyForTransmission(2588000, (data_big['data_sent_bytes'].max()*4)) * 7
    nano1_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano1['data_sent_bytes'].max()*4)) 
    nano2_power += RadioEnergy.getEnergyForTransmission(2588000, (data_nano2['data_sent_bytes'].max()*4)) *7

    total_power = big_power + nano1_power + nano2_power
    power_list_L50.append(total_power)


plot_with_values(ax, name_list_D50, power_list_D50, "Test with 50 Images")
plot_with_values(ax, name_list_GS50, power_list_GS50, "Test with 50 Images")

plot_with_values(ax, name_list_L50, power_list_L50, "Test with 50 Images")

plt.show()