#concept ko incase

import abc

class Vehicle(abc.ABC):
    def __init__(self, name, cost, fuel_cost, luxury_tax, capacity):
        self.__name = name
        self.__cost = cost
        self.__fuel_cost = fuel_cost  # per liter
        self.__luxury_tax = luxury_tax
        self.__capacity = capacity

    def getvehicle_info(self):
        return {
            "name": self.__name,
            "cost": self.__cost,
            "fuel_cost": self.__fuel_cost,
            "luxury_tax": self.__luxury_tax,
            "capacity": self.__capacity
        }

    @abc.abstractmethod
    def calculate_cost_permile(self):
        pass

    def calculate_fare(self, distance):
        return self.calculate_cost_permile() * distance

"""Vehicle Subclasses"""

class Car(Vehicle):
    def __init__(self, name, cost, fuel_cost, luxury_tax, capacity):
        super().__init__(name, cost, fuel_cost, luxury_tax, capacity)
        self.__cost_per_mile = self._calculate_cost_permile_internal()

    def _calculate_cost_permile_internal(self):
        info = self.getvehicle_info()
        cost = info['cost']
        fuel_cost = info['fuel_cost']
        luxury_tax = info['luxury_tax']
        
        fuel_efficiency_kpl = 15  # Assumed for cars
        km_per_mile = 1.60934
        miles_per_liter = fuel_efficiency_kpl / km_per_mile
        lifetime_miles = 100000 / km_per_mile

        depreciation_per_mile = cost / lifetime_miles
        fuel_cost_per_mile = fuel_cost / miles_per_liter
        luxury_tax_per_mile = luxury_tax / lifetime_miles

        return depreciation_per_mile + fuel_cost_per_mile + luxury_tax_per_mile

    def calculate_cost_permile(self):
        return self.__cost_per_mile
    def calculate_fare(self, distance):
        return super().calculate_fare(distance) + self.getvehicle_info()['luxury_tax'] * distance / 1000
    pass


class Van(Vehicle):
    def __init__(self, name, cost, fuel_cost, luxury_tax, capacity):
        super().__init__(name, cost, fuel_cost, luxury_tax, capacity)
        self.__cost_per_mile = self._calculate_cost_permile_internal()

    def _calculate_cost_permile_internal(self):
        info = self.getvehicle_info()
        cost = info['cost']
        fuel_cost = info['fuel_cost']
        luxury_tax = info['luxury_tax']

        fuel_efficiency_kpl = 10  # Vans are less efficient
        km_per_mile = 1.60934
        miles_per_liter = fuel_efficiency_kpl / km_per_mile
        lifetime_miles = 100000 / km_per_mile

        depreciation_per_mile = cost / lifetime_miles
        fuel_cost_per_mile = fuel_cost / miles_per_liter
        luxury_tax_per_mile = luxury_tax / lifetime_miles

        return depreciation_per_mile + fuel_cost_per_mile + luxury_tax_per_mile

    def calculate_cost_permile(self):
        return self.__cost_per_mile

    def calculate_fare(self, distance):
        return super().calculate_fare(distance) + self.getvehicle_info()['luxury_tax'] * distance / 1000


class Motorcycle(Vehicle):
    def __init__(self, name, cost, fuel_cost, luxury_tax, capacity):
        super().__init__(name, cost, fuel_cost, luxury_tax, capacity)
        self.__cost_per_mile = self._calculate_cost_permile_internal()

    def _calculate_cost_permile_internal(self):
        info = self.getvehicle_info()
        cost = info['cost']
        fuel_cost = info['fuel_cost']
        luxury_tax = info['luxury_tax']

        fuel_efficiency_kpl = 40  # Motorcycles are very efficient
        km_per_mile = 1.60934
        miles_per_liter = fuel_efficiency_kpl / km_per_mile
        lifetime_miles = 100000 / km_per_mile

        depreciation_per_mile = cost / lifetime_miles
        fuel_cost_per_mile = fuel_cost / miles_per_liter
        luxury_tax_per_mile = luxury_tax / lifetime_miles

        return depreciation_per_mile + fuel_cost_per_mile + luxury_tax_per_mile

    def calculate_cost_permile(self):
        return self.__cost_per_mile

    def calculate_fare(self, distance):
        return super().calculate_fare(distance) + self.getvehicle_info()['luxury_tax'] * distance / 1000



class Bike(Vehicle):
    def __init__(self, name, cost, fuel_cost, luxury_tax, capacity):
        super().__init__(name, cost, 0, 0, capacity)  # Bike has no fuel or luxury cost
        self.__cost_per_mile = self._calculate_cost_permile_internal()

    def _calculate_cost_permile_internal(self):
        info = self.getvehicle_info()
        cost = info['cost']

        lifetime_miles = 100000 / 1.60934  # same lifetime as others

        depreciation_per_mile = cost / lifetime_miles
        return depreciation_per_mile  # No fuel or tax

    def calculate_cost_permile(self):
        return self.__cost_per_mile

    def calculate_fare(self, distance):
        return super().calculate_fare(distance)

    

        

"""TESTING
    Simple test cases for the Vehicle classes
    Erase this section when integrating into a larger application
"""


v1 = Car("Toyota Camry", float("2000000"), 50, 10000, 5)
v2 = Van("Toyota Hiace", 2500000, 60, 15000, 12)
v3 = Motorcycle("Yamaha MT-15", 150000, 30, 5000, 2)
v4 = Bike("Giant Escape 3", 15000, 0, 0, 1)

print(f"Car Cost per mile: ₱{v1.calculate_cost_permile():.2f}")
print(f"Van Cost per mile: ₱{v2.calculate_cost_permile():.2f}")
print(f"Motorcycle Cost per mile: ₱{v3.calculate_cost_permile():.2f}")
print(f"Bike Cost per mile: ₱{v4.calculate_cost_permile():.2f}")

print(f"Car Fare for 100 miles: ₱{v1.calculate_fare(100):.2f}")
print(f"Van Fare for 100 miles: ₱{v2.calculate_fare(100):.2f}")
print(f"Motorcycle Fare for 100 miles: ₱{v3.calculate_fare(100):.2f}")
print(f"Bike Fare for 100 miles: ₱{v4.calculate_fare(100):.2f}")
