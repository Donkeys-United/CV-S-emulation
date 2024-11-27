from threading import Thread
import json
import numpy as np
from uuid import getnode
from math import ceil

class OrbitalPositionThread(Thread):
    RADIUS_EARTH: float = 6378000.0
    MASS_EARTH: float = 5.97219 * 10**24
    GRAVITATIONAL_CONSTANT: float = 6.6743 * 10**-11
    GROUND_STATION_ANGLE: float = 0.0
    altitude: float
    satelliteID: int
    orbitalPeriod: float
    neighbourSatDist: float
    currentAngle: dict[int, float] = {}
    connections: dict[int, list[int, int]] = {}
    timeStamp: float = 0.0
    satClosestToGround: int
    orbitalRadius: float
    tickRate: float
    
    def __init__(self, config: str, tickRate: float):
        config_json  = json.loads(config)
        
        self.satelliteID = getnode()
        
        for i in config_json["satellites"]:
            self.currentAngle[i["id"]] = i["initial_angle"]
            self.connections[i["id"]] = i["connections"]
        
        self.altitude = config_json["altitude"]
        self.orbitalRadius = self.altitude + self.RADIUS_EARTH
        
        #Calculate the orbital period of the satellite
        self.orbitalPeriod = self.calculateOrbitalPeriodSeconds(self.altitude)
        
        #Calculate the distance to other satellites
        temp_list = list(self.currentAngle.values())
        self.neighbourSatDist = self.calculateDistance(temp_list[0], self.orbitalRadius ,temp_list[1], self.orbitalRadius)

        self.tickRate = tickRate
    def run(self) -> None:
        print("Do stuff")
    
    def calculateOrbitalPeriodSeconds(self, altitude: float) -> float:
        return 2*np.pi * np.sqrt((self.RADIUS_EARTH + altitude)**3 
                                / (self.MASS_EARTH * self.GRAVITATIONAL_CONSTANT))
    
    def calculateDistance(self, angle1: float, radius1: float ,angle2: float, radius2: float) -> float:
        return np.abs(self.calculatePosition(angle1, radius1) - self.calculatePosition(angle2, radius1))
    
    def canExecuteMission(self, radian: float, orbitNumber: int) -> bool:
        angle = radian * orbitNumber
        return angle >= self.currentAngle[self.satelliteID]
    
    def getCurrentPosition(self) -> complex:
        return self.calculatePosition(self.currentAngle[self.satelliteID], self.orbitalRadius)
    
    def __updatePositions(self, forwardTime: float) -> None:
        for key in self.currentAngle.keys():
            self.currentAngle[key] = self.currentAngle[key] + 2 * np.pi / self.orbitalPeriod * forwardTime
    
    def getSatellitePriorityList(self) -> list[int]:
        priorityList = []
        priorityList.append(self.satelliteID)
        
        if self.satelliteID == self.satClosestToGround:
            priorityList.append("GROUND")
            return priorityList
        
        nodes = list(self.currentAngle.keys())
        N = len(nodes)
        
        startIdx = nodes.index(self.satelliteID)
        satClosestToGroundIdx = nodes.index(self.satClosestToGround)
        
        for i in range(1, ceil(N/2) + 1):
            counterclockwiseDistance = np.abs(satClosestToGroundIdx - (startIdx - i))
            clockwiseDistance = N - np.abs((startIdx + i) - satClosestToGroundIdx)
            
            if clockwiseDistance <= counterclockwiseDistance:
                priorityList.append(nodes[(startIdx + i) % N])
                priorityList.append(nodes[(startIdx - i) % N])
            else:
                priorityList.append(nodes[(startIdx - i) % N])
                priorityList.append(nodes[(startIdx + i) % N])
            
            if (startIdx + i) % N == satClosestToGroundIdx or (startIdx - i) % N == satClosestToGroundIdx:
                priorityList.append("GROUND")
                break
        
        return priorityList
    
    def getPathDistanceToGround(self) -> float:
        nodes = list(self.currentAngle.keys())
        N = len(nodes)
        
        targetIdx = nodes.index(self.satClosestToGround)
        startIdx = nodes.index(self.satelliteID)
        
        counterclockwiseDistance = np.abs(targetIdx - startIdx) % N
        clockwiseDistance = N - np.abs(startIdx - targetIdx) % N
        
        minimumHops = min(clockwiseDistance, counterclockwiseDistance)
        
        return minimumHops * self.neighbourSatDist + self.calculateDistance(self.currentAngle[self.satClosestToGround], 
                                                                            self.orbitalRadius, 
                                                                            self.GROUND_STATION_ANGLE, 
                                                                            self.RADIUS_EARTH)
    
    def getSatClosestToGround(self) -> int:
        return self.satClosestToGround
                
    def calculateSatClosestToGround(self) -> None:
        smallestDistance = float('inf')
        ID = 0
        for key in self.currentAngle.keys():
            distance = self.calculateDistance(self.currentAngle[key], 
                                              self.orbitalRadius,
                                              self.GROUND_STATION_ANGLE,
                                              self.RADIUS_EARTH)
            if distance < smallestDistance:
                ID = key
                smallestDistance = distance
        
        self.satClosestToGround = ID
        
    def calculatePosition(self, angle:float, radius: float) -> complex:
        return radius * np.exp(angle*1j)
    
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
        },
        {
        "id": 5,
        "ip_address": "192.168.1.104",
        "connections": [3,1],
        "initial_angle": 5.71239
        }
    ],
    "altitude": 200000
    }"""

    testObject = OrbitalPositionThread(test_json)
    testObject.satelliteID = 3
    print(testObject.currentAngle)
    print(testObject.orbitalPeriod)
    print(testObject.satelliteID)
    print(testObject.neighbourSatDist)
    print(testObject.currentAngle)
    print(testObject.connections)
    testObject.calculateSatClosestToGround()
    print(testObject.getSatClosestToGround())
    print(testObject.getSatellitePriorityList())