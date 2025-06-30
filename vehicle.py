from abc import ABC, abstractmethod 

""" Parent class for all vehicle types """
class Vehicle(ABC):
    def __init__(self, name, base_fee, cost_per_mile, capacity) -> None:
        self.name = name
        self._base_fee = base_fee
        self._cost_per_mile = cost_per_mile
        self._capacity = capacity
    
    def capacity(self) -> int:
        return self._capacity
    
    def vehicle_type(self) -> str:
        return self.__class__.__name__
    
    def base_rate(self) -> float:
        return self._base_fee
    
    def calculate_cost(self) -> float:
        raise NotImplementedError("Subclasses must implement this method.")

""" Child class vehicle types """     
class Motorcycle(Vehicle):
    def cost_calculation(self, base_fee, distance) -> float:
        return self._base_fee + (distance * self._cost_per_mile) # Base cost fee // only 1 capacity
    
class Car(Vehicle):
    def __init__(self, name, base_fee=5.0, cost_per_mile=2.0, capacity=4) -> None: # Change later for csv integration
        super().__init__(name, base_fee, cost_per_mile, capacity)
        
    def cost_calculation(self, distance):
        return self._base_fee + (distance * self._cost_per_mile) # Base cost fee // only 4 capacity   
    
class Van(Vehicle):
    def cost_calculation(self, distance) -> float:
        return distance * self._cost_per_mile # Extra fee higher than car
        






# Test case     
sedan = Car("Sedan")

print(sedan.name)
print(sedan.cost_calculation(10))  # Example distance of 10 miles
print(sedan.capacity())  # Should print 4, the capacity of the car