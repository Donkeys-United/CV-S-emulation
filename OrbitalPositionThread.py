from threading import Thread

class OrbitalPositionThread(Thread):
    RADIUS_EARTH: float = 63710000.0
    GROUND_STATION_POSITION: complex = 1 + 0j
    altitude: float
    satelliteID: int
    initialAngle: dict[int, float]
    orbitalPeriod: float
    neighbourSatDist: float
    currentPosition: dict[int, complex]
    timeStamp: float = 0.0
    
    def __init__(self, config: str):
        print("Do stuff")
    
    def run() -> None:
        print("Do stuff")
    
    def canExecuteMission(radian: float, orbitNumber: int) -> bool:
        print("Do stuff")
    
    def getCurrentPosition() -> complex:
        print("Do stuff")
    
    def __updatePositions(forwardTime: float) -> None:
        print("Do stuff")
    
    def getSatellitePriorityList() -> list[int]:
        print("Do stuff")
    
    def getPathDistanceToGround() -> float:
        print("Do stuff")
    