from threading import Thread
import json
import numpy as np
from uuid import getnode

class OrbitalPositionThread(Thread):
    RADIUS_EARTH: float = 6378000.0
    MASS_EARTH: float = 5.97219 * 10**24
    GRAVITATIONAL_CONSTANT: float = 6.6743 * 10**-11
    GROUND_STATION_POSITION: complex = 1 + 0j
    altitude: float
    satelliteID: int
    orbitalPeriod: float
    neighbourSatDist: float
    currentAngle: dict[int, float] = {}
    timeStamp: float = 0.0
    
    def __init__(self, config: str):
        config_json  = json.loads(config)
        
        self.satelliteID = getnode()
        
        for i in config_json["satellites"]:
            self.currentAngle[i["id"]] = i["initial_angle"]
        
        self.altitude = config_json["altitude"]
        
        #Calculate the orbital period of the satellite
        self.orbitalPeriod = self.calculateOrbitalPeriodSeconds(self.altitude)
        
        #Calculate the distance to other satellites
        temp_list = list(self.currentAngle.values())
        self.neighbourSatDist = self.calculateDistance(temp_list[0], temp_list[1])
    
    def run(self) -> None:
        print("Do stuff")
    
    def calculateOrbitalPeriodSeconds(self, altitude: float) -> float:
        return 2*np.pi * np.sqrt((self.RADIUS_EARTH + altitude)**3 
                                / (self.MASS_EARTH * self.GRAVITATIONAL_CONSTANT))
    
    def calculateDistance(self, angle1: float, angle2: float) -> float:
        return np.abs((self.RADIUS_EARTH + self.altitude) * (np.exp(angle1*1j) - np.exp(angle2*1j)))
    
    def canExecuteMission(self, radian: float, orbitNumber: int) -> bool:
        angle = radian * orbitNumber
        return angle >= self.currentAngle[self.satelliteID]
    
    def getCurrentPosition(self) -> complex:
        return np.exp(1j * self.currentAngle[self.satelliteID])
    
    def __updatePositions(self, forwardTime: float) -> None:
        for key in self.currentAngle.keys():
            self.currentAngle[key] = self.currentAngle[key] + 2 * np.pi / self.orbitalPeriod * forwardTime
    
    def getSatellitePriorityList(self) -> list[int]:
        print("Do stuff")
    
    def getPathDistanceToGround(self) -> float:
        print("Do stuff")
    


if __name__ == "__main__":
    test_json = """{
    "satellites": [
        {
        "id": 1,
        "ip_address": "192.168.1.101",
        "connections": [1, 4],
        "initial_angle": 0.0
        },
        {
        "id": 2,
        "ip_address": "192.168.1.102",
        "connections": [2,3],
        "initial_angle": 1.5708
        },
        {
        "id": 3,
        "ip_address": "192.168.1.103",
        "connections": [2,3],
        "initial_angle": 3.14159
        },
        {
        "id": 4,
        "ip_address": "192.168.1.104",
        "connections": [3,1],
        "initial_angle": 4.71239
        }
    ],
    "altitude": 200000
    }"""

    testObject = OrbitalPositionThread(test_json)
    print(testObject.currentAngle)
    print(testObject.orbitalPeriod)
    print(testObject.satelliteID)
    print(testObject.neighbourSatDist)
    print(testObject.currentAngle)