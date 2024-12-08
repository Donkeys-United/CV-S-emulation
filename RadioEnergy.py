import numpy as np

#Numbers are based on the SWIFT-X KTRX transceiver https://satcatalog.s3.amazonaws.com/components/575/SatCatalog_-_Tethers_Unlimited_-_SWIFT-KTRX_Transceiver_-_Datasheet.pdf?lastmod=20210708075150
class RadioEnergy:
    MINIMUM_RECEIVER_SENSITIVITY: int = -90
    MAX_TX_POWER: int = 32
    MAX_PEAK_TX_POWER_CONSUMPTION: int = 27
    ANTENNA_GAIN: int = 25 #Typical antenna gain
    RADIO_FREQUENCY: int = 27 * 10**9
    SYMBOL_RATE: int = 150 * 10**6
    FORWARD_ERROR_CORRECTION: float = 1/2
    SPEED_OF_LIGHT: int = 299792458
    
    @staticmethod
    def getFreeSpacePathLoss(distance: float) -> float:
        """Calculate and get the FSPL based on the transmission distance

        Args:
            distance (float): The distance to the receiver

        Returns:
            float: The free space path loss
        """
        return 20*np.log10(distance) + 20*np.log10(RadioEnergy.RADIO_FREQUENCY) + 20*np.log10(4*np.pi/RadioEnergy.SPEED_OF_LIGHT)
    
    @staticmethod
    def getMinimumTxPower(distance: float) -> float:
        """Calculate the minimum required Tx power

        Args:
            distance (float): The distance to the receiver

        Returns:
            float: The minimum Tx power
        """
        return (RadioEnergy.MINIMUM_RECEIVER_SENSITIVITY 
                - 2*RadioEnergy.ANTENNA_GAIN
                + RadioEnergy.getFreeSpacePathLoss(distance))
    
    @staticmethod
    def getOperationalPower(distance: float) -> float:
        """Calculate the operational power for the transmitter at a given distance

        Args:
            distance (float): The distance to the receiver

        Returns:
            float: The operational power
        """
        return (RadioEnergy.convertDbmToWatt(RadioEnergy.getMinimumTxPower(distance))
                /RadioEnergy.convertDbmToWatt(RadioEnergy.MAX_TX_POWER)) * RadioEnergy.MAX_PEAK_TX_POWER_CONSUMPTION
    
    @staticmethod
    def convertDbmToWatt(dbm: float) -> float:
        return 10**((dbm-30)/10)
    
    @staticmethod
    def getEnergyForTransmission(distance: float, dataSizeBits: int) -> float:
        """Calculate the required energy for transmission of some data size

        Args:
            distance (float): The distance to the receiver
            dataSizeBits (int): The data size in bits

        Returns:
            float: The energy consumption of the data transmission
        """
        return (RadioEnergy.getOperationalPower(distance)/
                (RadioEnergy.SYMBOL_RATE*4*RadioEnergy.FORWARD_ERROR_CORRECTION)) * dataSizeBits
    
    
if __name__ == "__main__":
    print(RadioEnergy.getFreeSpacePathLoss(6367000.0))
    print(RadioEnergy.getMinimumTxPower(6367000.0))
    print(RadioEnergy.getOperationalPower(6367000.0))
    print(RadioEnergy.convertDbmToWatt(32))
    print(RadioEnergy.getEnergyForTransmission(6367000.0, 6*10**6))