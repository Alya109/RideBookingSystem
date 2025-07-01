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
    
    def get_vehicle_name(self) -> str:
        return self.name
    
""" Child class vehicle types """   
  
class Motorcycle(Vehicle):
    
    def __init__(self) -> None:
        super().__init__(name="Motorcycle", base_fee=60, cost_per_mile=10, capacity=1, luxury_fee=0, rate_per_minute=0)
    
    def calculate_cost(self, distance: float) -> float:
        total_cost = self._base_fee + (distance * self._cost_per_mile)
        return total_cost 

class Taxi(Vehicle):
    
    def __init__(self) -> None:
        super().__init__(name="Taxi", base_fee=80, cost_per_mile=12, capacity=4, luxury_fee=0, rate_per_minute=1.5)
    
    def calculate_cost(self, distance: float, time: float = 0) -> float:
        total_cost = self._base_fee + (distance * self._cost_per_mile) + (time * self._rate_per_minute) # Assuming a fixed distance of 10 miles for simplicity
        return total_cost
    
class Car(Vehicle):
    def __init__(self, name: str) -> None:
        super().__init__(name, base_fee=100, cost_per_mile=14, capacity=4, rate_per_minute=2, luxury_fee=0)
    
    def calculate_cost(self, distance: float, time: float = 0) -> float:
        total_cost = self._base_fee + (distance * self._cost_per_mile) + (time * self._rate_per_minute)
        return total_cost
        

class ElectricCar(Vehicle):
    
    def __init__(self) -> None:
        super().__init__(name="Electric Car", base_fee=80, cost_per_mile=14, capacity=4, rate_per_minute=2, luxury_fee=20)
    
    def calculate_cost(self, distance: float, time: float = 0) -> float:
        total_cost = self._base_fee + (distance * self._cost_per_mile) + (time * self._rate_per_minute) + self._luxury_fee
        return total_cost

class Van(Vehicle):
    
    def __init__(self) -> None:
        super().__init__(name="Van", base_fee=120, cost_per_mile=16, capacity=12, rate_per_minute=3, luxury_fee=60)
    
    def calculate_cost(self, distance: float, time: float = 0, group_size: int = 1, luxury_fee: float = 0) -> float:
        group_size_fee = 50 if group_size > 8 else 30
        total_cost = self._base_fee + (distance * self._cost_per_mile) + (time * self._rate_per_minute) + group_size_fee + luxury_fee
        return total_cost


# Test
van = Van()
print(van.calculate_cost(10, 30, group_size=9, luxury_fee=20))  # Example usage
