from abc import ABC, abstractmethod 

""" Parent class for all vehicle types """
class Vehicle(ABC):
    def __init__(self, name, base_fee, cost_per_mile, capacity, luxury_fee=0, rate_per_minute=0) -> None:
        self.name = name
        self._base_fee = base_fee
        self._cost_per_mile = cost_per_mile
        self._capacity = capacity
        self._luxury_fee = luxury_fee
        self._rate_per_minute = rate_per_minute
    
    @abstractmethod
    def calculate_cost(self) -> float:
        pass

""" Child class vehicle types """   
  
class Motorcycle(Vehicle):
    
    def __init__(self):
        pass
    
    def calculate_cost(self, distance: float) -> float:
        total_cost = self._base_fee + (distance * self._cost_per_mile)
        return total_cost 

class Taxi(Vehicle):
    
    def __init__(self):
        pass
    
    def calculate_cost(self):
        pass

class Car(Vehicle):
    
    def __init__(self):
        pass
    
    def calculate_cost(self, distance: float, time: float = 0) -> float:
        rate_per_minute = self._rate_per_minute
        total_cost = self._base_fee + (distance * self._cost_per_mile) + (time * rate_per_minute)
        return total_cost
        

class ElectricCar(Vehicle):
    
    def __init__(self):
        pass
    
    def calculate_cost(self, distance: float, time: float = 0, luxury_fee: float = 0) -> float:
        rate_per_minute = self._rate_per_minute
        total_cost = self._base_fee + (distance * self._cost_per_mile) + (time * rate_per_minute) + luxury_fee
        return total_cost

class Van(Vehicle):
    
    def __init__(self):
        pass
    
    def calculate_cost(self, distance: float, time: float = 0, group_size: int = 1, luxury_fee: float = 0) -> float:
        rate_per_minute = self._rate_per_minute
        if group_size > 8:
            group_size_fee = 50  # Additional fee for large groups
        else:
            group_size_fee = 30
            
        total_cost = self._base_fee + (distance * self._cost_per_mile) + (time * rate_per_minute) + group_size_fee + luxury_fee
        return total_cost




# Test case     
sedan = Car("Sedan")

print(sedan.name)
print(sedan.cost_calculation(10))  # Example distance of 10 miles
print(sedan.capacity())  # Should print 4, the capacity of the car