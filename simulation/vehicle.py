"""
vehicle.py
Simulates vehicles entering and leaving parking lot.
"""

import random
import time
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("en_IN")

VEHICLE_TYPES = [
    "Car", "SUV", "Bike",
    "Truck", "Van", "Auto"
]
VEHICLE_COLORS = [
    "White", "Black", "Silver",
    "Red", "Blue", "Grey", "Brown"
]

class Vehicle:
    """Represents a vehicle in the parking lot."""

    def __init__(self, slot_id):
        self.plate_number  = self._generate_plate()
        self.vehicle_type  = random.choice(VEHICLE_TYPES)
        self.color         = random.choice(VEHICLE_COLORS)
        self.slot_id       = slot_id
        self.entry_time    = datetime.now()
        self.exit_time     = None
        self.fee_per_hour  = {
            "Car":   40, "SUV":  60, "Bike": 20,
            "Truck": 80, "Van":  60, "Auto": 20,
        }.get(self.vehicle_type, 40)
        self.owner_name    = fake.name()
        self.phone         = fake.phone_number()

    def _generate_plate(self):
        """Generate realistic Indian number plate."""
        states = [
            "MH", "DL", "KA", "TN",
            "UP", "GJ", "RJ", "MP"
        ]
        state  = random.choice(states)
        dist   = random.randint(10, 99)
        series = random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
        series += random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
        num    = random.randint(1000, 9999)
        return f"{state}{dist}{series}{num}"

    def calculate_fee(self):
        """Calculate parking fee."""
        end   = self.exit_time or datetime.now()
        hours = max(
            1,
            math.ceil(
                (end - self.entry_time)
                .total_seconds() / 3600
            )
        )
        return hours * self.fee_per_hour

    def depart(self):
        """Mark vehicle as departed."""
        self.exit_time = datetime.now()

    def duration_str(self):
        """Human readable duration."""
        end     = self.exit_time or datetime.now()
        seconds = int(
            (end - self.entry_time).total_seconds()
        )
        hours   = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def to_dict(self):
        """Convert to dictionary."""
        import math
        return {
            "plate_number": self.plate_number,
            "vehicle_type": self.vehicle_type,
            "color":        self.color,
            "slot_id":      self.slot_id,
            "entry_time":   self.entry_time.strftime(
                "%H:%M:%S"
            ),
            "exit_time":    self.exit_time.strftime(
                "%H:%M:%S"
            ) if self.exit_time else "—",
            "duration":     self.duration_str(),
            "fee":          f"₹{self.calculate_fee()}",
            "owner":        self.owner_name,
            "phone":        self.phone,
            "status":       "Departed"
                            if self.exit_time
                            else "Parked",
        }


import math