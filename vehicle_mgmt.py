from abc import ABC, abstractmethod 

class Vehicle:
    def __init__(self, cost_per_mile, capacity) -> None:
        self.cost_per_mile = cost_per_mile
        self.capacity = capacity
    
    @abstractmethod    
    def cost_calculation(self, distance):
        """Implementation per vehicle"""
    
    