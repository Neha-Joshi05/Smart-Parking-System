"""
parking_simulator.py
Main parking lot simulation engine.
Manages slots, vehicles, revenue and events.
"""

import random
import time
import math
from datetime import datetime, timedelta
from simulation.sensor  import SensorArray
from simulation.vehicle import Vehicle


class ParkingSlot:
    """Represents a single parking slot."""

    SLOT_TYPES = ["Standard", "Premium",
                  "Handicap", "EV Charging"]

    def __init__(self, slot_id, floor,
                 slot_type="Standard"):
        self.slot_id    = slot_id
        self.floor      = floor
        self.slot_type  = slot_type
        self.is_occupied= False
        self.vehicle    = None
        self.reserved   = False
        self.total_uses = 0

    def park_vehicle(self, vehicle):
        """Park a vehicle in this slot."""
        self.is_occupied = True
        self.vehicle     = vehicle
        self.total_uses += 1

    def remove_vehicle(self):
        """Remove vehicle from slot."""
        v = self.vehicle
        if v:
            v.depart()
        self.is_occupied = False
        self.vehicle     = None
        return v

    def to_dict(self):
        """Convert to dict for dashboard."""
        return {
            "slot_id":   self.slot_id,
            "floor":     self.floor,
            "type":      self.slot_type,
            "occupied":  self.is_occupied,
            "reserved":  self.reserved,
            "total_uses":self.total_uses,
            "vehicle":   self.vehicle.plate_number
                         if self.vehicle else None,
            "entry_time":self.vehicle.entry_time
                         .strftime("%H:%M:%S")
                         if self.vehicle else None,
            "duration":  self.vehicle.duration_str()
                         if self.vehicle else None,
        }


class ParkingLot:
    """
    Main parking lot simulation.
    Manages all floors, slots, vehicles and revenue.
    """

    def __init__(self, name="TechPark Mall",
                 floors=3, slots_per_floor=8,
                 seed=42):
        self.name            = name
        self.floors          = floors
        self.slots_per_floor = slots_per_floor
        self.total_slots     = floors * slots_per_floor
        self.slots           = {}
        self.vehicles_history= []
        self.current_vehicles= {}
        self.total_revenue   = 0.0
        self.total_vehicles  = 0
        self.entry_log       = []
        self.hourly_traffic  = [0] * 24
        self.sensor_array    = SensorArray(
            num_slots=self.total_slots,
            floors=floors
        )
        self._init_slots()
        self._seed_initial_state(seed)

    def _init_slots(self):
        """Initialize all parking slots."""
        slot_types = (
            ["Standard"]    * 5 +
            ["Premium"]     * 2 +
            ["EV Charging"] * 1
        )
        for floor in range(1, self.floors + 1):
            for s in range(1, self.slots_per_floor + 1):
                sid       = f"F{floor}-S{s:02d}"
                slot_type = random.choice(slot_types)
                self.slots[sid] = ParkingSlot(
                    sid, f"Floor {floor}", slot_type
                )

    def _seed_initial_state(self, seed):
        """Pre-populate with some parked vehicles."""
        random.seed(seed)
        occupied_count = int(self.total_slots * 0.4)
        slot_ids = random.sample(
            list(self.slots.keys()), occupied_count
        )
        for sid in slot_ids:
            v = Vehicle(sid)
            # Backdate entry time
            v.entry_time = datetime.now() - \
                timedelta(
                    minutes=random.randint(10, 180)
                )
            self.slots[sid].park_vehicle(v)
            self.current_vehicles[sid] = v
            self.sensor_array.sensors[
                list(self.slots.keys()).index(sid)
            ].simulate_vehicle_arrival()

    def get_available_slots(self):
        """Get list of available slots."""
        return [
            s for s in self.slots.values()
            if not s.is_occupied
        ]

    def get_occupied_slots(self):
        """Get list of occupied slots."""
        return [
            s for s in self.slots.values()
            if s.is_occupied
        ]

    def vehicle_entry(self, preferred_floor=None):
        """Handle vehicle entry."""
        available = self.get_available_slots()
        if not available:
            return None, "Parking Full! 🚫"

        # Find best slot
        if preferred_floor:
            floor_slots = [
                s for s in available
                if s.floor == preferred_floor
            ]
            if floor_slots:
                available = floor_slots

        slot    = random.choice(available)
        vehicle = Vehicle(slot.slot_id)
        slot.park_vehicle(vehicle)
        self.current_vehicles[slot.slot_id] = vehicle
        self.total_vehicles += 1

        # Update sensor
        idx = list(self.slots.keys()).index(slot.slot_id)
        if idx < len(self.sensor_array.sensors):
            self.sensor_array.sensors[idx]\
                .simulate_vehicle_arrival()

        # Log entry
        self.entry_log.append({
            "time":    datetime.now().strftime(
                "%H:%M:%S"
            ),
            "plate":   vehicle.plate_number,
            "slot":    slot.slot_id,
            "type":    vehicle.vehicle_type,
            "event":   "ENTRY",
        })
        if len(self.entry_log) > 50:
            self.entry_log.pop(0)

        # Update hourly traffic
        hour = datetime.now().hour
        self.hourly_traffic[hour] += 1

        return vehicle, slot.slot_id

    def vehicle_exit(self, slot_id=None):
        """Handle vehicle exit."""
        occupied = self.get_occupied_slots()
        if not occupied:
            return None, 0

        if slot_id and slot_id in self.slots:
            slot = self.slots[slot_id]
            if not slot.is_occupied:
                slot = random.choice(occupied)
        else:
            slot = random.choice(occupied)

        vehicle = slot.remove_vehicle()
        if vehicle:
            import math
            hours = max(
                1,
                math.ceil(
                    (datetime.now() - vehicle.entry_time)
                    .total_seconds() / 3600
                )
            )
            fee = hours * vehicle.fee_per_hour
            self.total_revenue += fee
            self.vehicles_history.append(
                vehicle.to_dict()
            )
            if len(self.vehicles_history) > 100:
                self.vehicles_history.pop(0)
            if slot.slot_id in self.current_vehicles:
                del self.current_vehicles[slot.slot_id]

            # Update sensor
            idx = list(self.slots.keys()).index(
                slot.slot_id
            )
            if idx < len(self.sensor_array.sensors):
                self.sensor_array.sensors[idx]\
                    .simulate_vehicle_departure()

            # Log exit
            self.entry_log.append({
                "time":  datetime.now().strftime(
                    "%H:%M:%S"
                ),
                "plate": vehicle.plate_number,
                "slot":  slot.slot_id,
                "type":  vehicle.vehicle_type,
                "event": "EXIT",
                "fee":   f"₹{fee}",
            })
            if len(self.entry_log) > 50:
                self.entry_log.pop(0)

            return vehicle, fee
        return None, 0

    def auto_simulate(self):
        """
        Randomly simulate vehicle entry/exit.
        Called every dashboard refresh.
        """
        action = random.choice(
            ["entry", "entry", "exit", "none"]
        )
        if action == "entry":
            self.vehicle_entry()
        elif action == "exit":
            self.vehicle_exit()

    def get_dashboard_stats(self):
        """Get all stats for dashboard."""
        occupied  = len(self.get_occupied_slots())
        available = len(self.get_available_slots())
        occ_rate  = round(
            occupied / self.total_slots * 100, 1
        )

        floor_stats = {}
        for floor in range(1, self.floors + 1):
            fname = f"Floor {floor}"
            floor_slots = [
                s for s in self.slots.values()
                if s.floor == fname
            ]
            f_occ = sum(
                1 for s in floor_slots if s.is_occupied
            )
            floor_stats[fname] = {
                "total":     len(floor_slots),
                "occupied":  f_occ,
                "available": len(floor_slots) - f_occ,
                "rate":      round(
                    f_occ / max(len(floor_slots),1)
                    * 100, 1
                ),
            }

        return {
            "total":       self.total_slots,
            "occupied":    occupied,
            "available":   available,
            "reserved":    sum(
                1 for s in self.slots.values()
                if s.reserved
            ),
            "occ_rate":    occ_rate,
            "revenue":     round(self.total_revenue, 2),
            "total_vehicles": self.total_vehicles,
            "floor_stats": floor_stats,
            "slots":       [
                s.to_dict()
                for s in self.slots.values()
            ],
            "entry_log":   self.entry_log[-10:],
            "history":     self.vehicles_history[-20:],
            "hourly":      self.hourly_traffic,
        }