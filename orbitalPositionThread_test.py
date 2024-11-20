class orbitalPositionThread_test:
    
    def __init__(self):
        self.radian = 1.0471975512
        self.orbitNumber = 1
        
    def canExecuteMission(self, radian, orbitNumber):
        if (radian == self.radian) and (orbitNumber == self.orbitNumber):
            return True
        else:
            return False
