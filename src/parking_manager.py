"""
parking_manager.py
Manages parking operations and business logic.
"""

import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


class ParkingManager:
    """
    High-level parking management operations.
    """

    def __init__(self, parking_lot):
        self.lot = parking_lot

    def get_best_slot(self, preference="nearest"):
        """
        Find best available slot based on preference.
        preference: nearest | ev | premium | handicap
        """
        available = self.lot.get_available_slots()
        if not available:
            return None

        if preference == "ev":
            ev_slots = [
                s for s in available
                if s.slot_type == "EV Charging"
            ]
            return ev_slots[0] if ev_slots else available[0]

        elif preference == "premium":
            premium = [
                s for s in available
                if s.slot_type == "Premium"
            ]
            return premium[0] if premium else available[0]

        elif preference == "handicap":
            hand = [
                s for s in available
                if s.slot_type == "Handicap"
            ]
            return hand[0] if hand else available[0]

        # Default: nearest (Floor 1 first)
        return sorted(
            available,
            key=lambda s: s.slot_id
        )[0]

    def get_floor_recommendation(self):
        """
        Recommend which floor to go to.
        Returns floor with most available slots.
        """
        stats = self.lot.get_dashboard_stats()
        floor_stats = stats["floor_stats"]

        best_floor = max(
            floor_stats.items(),
            key=lambda x: x[1]["available"]
        )
        return best_floor[0], best_floor[1]["available"]

    def get_peak_hours(self):
        """
        Analyze traffic to find peak hours.
        Returns list of (hour, count) tuples.
        """
        hourly = self.lot.hourly_traffic
        peak   = sorted(
            enumerate(hourly),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        return [
            (f"{h:02d}:00", count)
            for h, count in peak
            if count > 0
        ]

    def calculate_revenue_projection(self):
        """
        Project daily/monthly revenue.
        """
        current_revenue = self.lot.total_revenue
        hour = datetime.now().hour
        if hour == 0:
            daily_proj = current_revenue * 24
        else:
            daily_proj = (current_revenue / hour) * 24

        return {
            "current":   round(current_revenue, 2),
            "daily":     round(daily_proj, 2),
            "monthly":   round(daily_proj * 30, 2),
            "yearly":    round(daily_proj * 365, 2),
        }

    def get_slot_heatmap_data(self):
        """
        Generate heatmap data for slot usage.
        Returns 2D array for plotly heatmap.
        """
        slots = list(self.lot.slots.values())
        floors = self.lot.floors
        spf    = self.lot.slots_per_floor

        matrix = []
        for f in range(floors):
            row = []
            for s in range(spf):
                idx = f * spf + s
                if idx < len(slots):
                    row.append(
                        1 if slots[idx].is_occupied
                        else 0
                    )
                else:
                    row.append(-1)
            matrix.append(row)
        return matrix

    def get_vehicle_type_breakdown(self):
        """
        Count vehicles by type.
        """
        occupied = self.lot.get_occupied_slots()
        counts   = {}
        for slot in occupied:
            if slot.vehicle:
                vtype = slot.vehicle.vehicle_type
                counts[vtype] = counts.get(vtype, 0) + 1
        return counts

    def get_duration_stats(self):
        """
        Average parking duration of current vehicles.
        """
        durations = []
        for slot in self.lot.get_occupied_slots():
            if slot.vehicle:
                mins = (
                    datetime.now() -
                    slot.vehicle.entry_time
                ).total_seconds() / 60
                durations.append(mins)

        if not durations:
            return {"avg": 0, "min": 0, "max": 0}

        return {
            "avg": round(np.mean(durations), 1),
            "min": round(min(durations), 1),
            "max": round(max(durations), 1),
        }