from scipy.optimize import minimize, OptimizeResult
from typing import Callable

class EnergyOptimiser:
    MU_INFERENCE: float = 0.049
    P_GPU_FIXED: float = 4.55
    F_FIXED: int = 612000000
    F_MIN: int = 306000000
    F_MAX: int = 612000000
    
    def totalEnergy(self, frequencies: list[float]) -> float:
        """Calculates the total amount of energy it would take to calculate some tasks at some frequencies

        Args:
            frequencies (list[float]): The frequencies each individual task would be executed at

        Returns:
            float: The energy consumption in joules
        """
        return sum(1 + self.MU_INFERENCE * (self.P_GPU_FIXED/self.F_FIXED**2) * f**2 
                   for f in frequencies)
    
    def taskConstraint(self, k: int, busytime: float, timeLimit: float) -> Callable:
        """Method for generating a constraint function for the tasks

        Args:
            k (int): The task index
            busyTime (float): The time until the current executed is expected to be finished
            timeLimit (float): Time limit of task k

        Returns:
            Callable: The constraint function
        """
        def constraint(frequencies):
            cumulativeTime = sum(1 + self.MU_INFERENCE * (float(self.F_FIXED) / float(frequencies[i])) for i in range(k+1))
            return timeLimit - cumulativeTime
        return constraint
    
    def getBounds(self, K: int) -> list[tuple[int, int]]:
        """Generates the bound for each frequency for each task

        Args:
            K (int): Number of tasks

        Returns:
            list[tuple[int, int]]: The frequency bounds
        """
        return [(self.F_MIN, self.F_MAX) for _ in range(K)]

    def getInitialFrequencies(self, K: int) -> list[int]:
        """The initial frequencies which will be F_MIN 

        Args:
            K (int): Number of tasks

        Returns:
            list[int]: The list containing the start frequencies
        """
        return [(self.F_MAX-self.F_MIN)/2 for _ in range(K)]
    
    def getConstraints(self, K: int, busyTime: float, timeLimits: list[float]) -> list[dict[str, Callable]]:
        """Function that generates constraints

        Args:
            K (int): The number of tasks
            busyTime (float): The time until the current executed is expected to be finished
            timeLimits (list[float]): The list of time limits

        Returns:
            list[dict[str, function]]: List containing the constraints
        """
        return [{'type': 'ineq', 'fun': self.taskConstraint(k, busyTime, timeLimits[k])} for k in range(K)]
    
    def minimiseEnergyConsumption(self, timeLimits: list[float], busyTime: float) -> OptimizeResult:
        """Function that minimizes the energy consumption

        Args:
            timeLimits (list[float]): The list of time limits
            busyTime (float): The time until the current executed is expected to be finished

        Returns:
            OptimizeResult: The frequencies of the minimized results
        """
        K = len(timeLimits)
        bounds = self.getBounds(K)
        initialFrequencies = self.getInitialFrequencies(K)
        
        constraints = self.getConstraints(K, busyTime, timeLimits)
        
        result = minimize(
            self.totalEnergy,
            initialFrequencies,
            constraints=constraints,
            bounds=bounds,
            method='CG'
        )
        
        return result

if __name__ == "__main__":
    optimiser = EnergyOptimiser()
    timeLimits = [1, 2.2]
    result = optimiser.minimiseEnergyConsumption(timeLimits, 0)
    print(result.x)
    print(result.success)
    
    for k in range(len(result.x)):
        print(sum(1 + 0.057 * (float(510000000) / result.x[i]) for i in range(k+1)))

    
    