from abc import ABC, abstractmethod 

class Vehicle(ABC):
    def __init__(self, name, cost_per_mile, capacity) -> None:
        sef.name = name
        self._cost_per_mile = cost_per_mile
        self._capacity = capacity
    
    @abstractmethod
    def cost_calculation(self, distance) -> float:
        pass
        
class Van(Vehicle):
    def cost_calculation(self, distance) -> float:
        return distance * self._cost_per_mile # Extra fee 
        
class Car(Vehicle):
    def cost_calculation(self, distance) -> float:
        return distance * self._cost_per_mile + 10 # Extra fee
        
class Motorcycle(Vehicle):
    def cost_calculation(self, distance) -> float:
        return distance * self._cost_per_mile # Base cost fee // only 1 capacity

