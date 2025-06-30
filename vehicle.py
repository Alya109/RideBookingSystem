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
    
    @abstractmethod
    def calculate_cost(self) -> float:
        pass

""" Child class vehicle types """     
class Motorcycle(Vehicle):
    pass

class Taxi(Vehicle):
    pass

class Car(Vehicle):
    pass

class ElectricCar(Vehicle):
    pass

class Van(Vehicle):
    pass





# Test case     
sedan = Car("Sedan")

print(sedan.name)
print(sedan.cost_calculation(10))  # Example distance of 10 miles
print(sedan.capacity())  # Should print 4, the capacity of the car