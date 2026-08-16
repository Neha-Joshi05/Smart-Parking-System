"""
alerts.py
Smart alert system for parking management.
"""

from datetime import datetime, timedelta


class AlertSystem:
    """
    Generates smart alerts for parking events.
    """

    def __init__(self, parking_lot):
        self.lot    = parking_lot
        self.alerts = []

    def check_all(self):
        """Run all alert checks."""
        self.alerts = []
        self._check_capacity()
        self._check_long_parked()
        self._check_revenue()
        self._check_sensors()
        return self.alerts

    def _check_capacity(self):
        """Alert on high/low occupancy."""
        stats = self.lot.get_dashboard_stats()
        rate  = stats["occ_rate"]

        if rate >= 90:
            self.alerts.append({
                "type":    "CRITICAL",
                "icon":    "🔴",
                "message": f"Parking {rate}% full! "
                           f"Only {stats['available']}"
                           f" slots left!",
                "time":    datetime.now().strftime(
                    "%H:%M"
                ),
            })
        elif rate >= 75:
            self.alerts.append({
                "type":    "WARNING",
                "icon":    "🟡",
                "message": f"Parking {rate}% full. "
                           f"{stats['available']} "
                           f"slots available.",
                "time":    datetime.now().strftime(
                    "%H:%M"
                ),
            })
        elif rate < 20:
            self.alerts.append({
                "type":    "INFO",
                "icon":    "🟢",
                "message": f"Parking only {rate}% "
                           f"occupied. "
                           f"{stats['available']} "
                           f"slots free!",
                "time":    datetime.now().strftime(
                    "%H:%M"
                ),
            })

    def _check_long_parked(self):
        """Alert for vehicles parked too long."""
        for slot in self.lot.get_occupied_slots():
            if slot.vehicle:
                hours = (
                    datetime.now() -
                    slot.vehicle.entry_time
                ).total_seconds() / 3600

                if hours >= 8:
                    self.alerts.append({
                        "type":    "WARNING",
                        "icon":    "⏰",
                        "message": f"Vehicle "
                                   f"{slot.vehicle.plate_number}"
                                   f" in {slot.slot_id}"
                                   f" parked for "
                                   f"{hours:.1f}h!",
                        "time":    datetime.now()
                                   .strftime("%H:%M"),
                    })

    def _check_revenue(self):
        """Alert on revenue milestones."""
        rev = self.lot.total_revenue
        milestones = [
            1000, 5000, 10000,
            25000, 50000, 100000
        ]
        for m in milestones:
            if rev >= m and rev < m * 1.05:
                self.alerts.append({
                    "type":    "SUCCESS",
                    "icon":    "💰",
                    "message": f"Revenue milestone! "
                               f"₹{m:,} collected!",
                    "time":    datetime.now()
                               .strftime("%H:%M"),
                })
                break

    def _check_sensors(self):
        """Alert on sensor faults."""
        readings = self.lot.sensor_array.read_all()
        faults   = [
            r for r in readings
            if r["health"] == "FAULT"
        ]
        if faults:
            self.alerts.append({
                "type":    "CRITICAL",
                "icon":    "📡",
                "message": f"{len(faults)} sensor(s)"
                           f" reporting faults! "
                           f"Check immediately.",
                "time":    datetime.now()
                           .strftime("%H:%M"),
            })

    def get_alert_color(self, alert_type):
        """Get color for alert type."""
        return {
            "CRITICAL": "#c9866b",
            "WARNING":  "#d4a76a",
            "INFO":     "#7a9e9f",
            "SUCCESS":  "#8b9e7a",
        }.get(alert_type, "#c9b99a")