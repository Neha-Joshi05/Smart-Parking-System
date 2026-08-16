"""
sensor.py
Simulates HC-SR04 Ultrasonic Sensor behavior.
Measures distance and detects vehicle presence.
"""

import random
import time
import math


class UltrasonicSensor:
    """
    Simulates HC-SR04 Ultrasonic Sensor.

    Real sensor specs:
    - Range       : 2cm to 400cm
    - Accuracy    : ±3mm
    - Trigger pulse: 10µs
    - Working freq : 40Hz
    - Beam angle  : 15°

    Formula:
    Distance = (Time × Speed of Sound) / 2
    Speed of sound = 343 m/s = 0.0343 cm/µs
    """

    # Constants
    MAX_RANGE    = 400   # cm
    MIN_RANGE    = 2     # cm
    VEHICLE_THRESHOLD = 20  # cm — if < 20cm, slot occupied
    NOISE_FACTOR = 0.02  # 2% noise simulation

    def __init__(self, sensor_id, slot_id,
                 location="Floor 1"):
        self.sensor_id   = sensor_id
        self.slot_id     = slot_id
        self.location    = location
        self.is_occupied = False
        self.distance_cm = self.MAX_RANGE
        self.last_reading= time.time()
        self.reading_count = 0
        self.error_count   = 0

        # Calibration offset (simulates real sensor variance)
        self.calibration_offset = random.uniform(-2, 2)

    def trigger_pulse(self):
        """
        Simulates sending 10µs trigger pulse.
        Returns raw echo time in microseconds.
        """
        # Simulate processing delay (real: ~60ms per reading)
        time.sleep(0.001)

        if self.is_occupied:
            # Vehicle present: distance 5-15 cm
            base_dist = random.uniform(5, 15)
        else:
            # Slot empty: distance 80-200 cm
            base_dist = random.uniform(80, 200)

        # Add sensor noise
        noise = base_dist * self.NOISE_FACTOR * \
                random.uniform(-1, 1)
        raw_distance = base_dist + noise + \
                       self.calibration_offset

        # Clamp to valid range
        return max(self.MIN_RANGE,
                   min(self.MAX_RANGE, raw_distance))

    def read_distance(self):
        """
        Read distance from sensor.
        Returns distance in cm.
        """
        try:
            self.distance_cm = self.trigger_pulse()
            self.last_reading  = time.time()
            self.reading_count += 1
            return round(self.distance_cm, 2)
        except Exception:
            self.error_count += 1
            return self.MAX_RANGE

    def is_vehicle_detected(self):
        """
        Returns True if vehicle detected
        (distance < threshold).
        """
        dist = self.read_distance()
        return dist < self.VEHICLE_THRESHOLD

    def get_status(self):
        """Get full sensor status dict."""
        dist = self.read_distance()
        return {
            "sensor_id":    self.sensor_id,
            "slot_id":      self.slot_id,
            "location":     self.location,
            "distance_cm":  dist,
            "occupied":     dist < self.VEHICLE_THRESHOLD,
            "last_reading": self.last_reading,
            "readings":     self.reading_count,
            "errors":       self.error_count,
            "health":       "OK"
                            if self.error_count < 5
                            else "FAULT",
        }

    def simulate_vehicle_arrival(self):
        """Simulate a vehicle parking."""
        self.is_occupied = True

    def simulate_vehicle_departure(self):
        """Simulate a vehicle leaving."""
        self.is_occupied = False


class SensorArray:
    """
    Array of ultrasonic sensors for
    multi-slot parking management.
    """

    def __init__(self, num_slots=12,
                 floors=3):
        self.sensors  = []
        self.num_slots= num_slots
        self.floors   = floors
        self._init_sensors()

    def _init_sensors(self):
        """Initialize sensor array."""
        slot_num = 1
        for floor in range(1, self.floors + 1):
            slots_per_floor = self.num_slots // \
                              self.floors
            for slot in range(1, slots_per_floor + 1):
                sensor = UltrasonicSensor(
                    sensor_id =f"SNS-{slot_num:03d}",
                    slot_id   =f"F{floor}-S{slot:02d}",
                    location  =f"Floor {floor}"
                )
                self.sensors.append(sensor)
                slot_num += 1

    def read_all(self):
        """Read all sensors."""
        return [s.get_status() for s in self.sensors]

    def get_available_count(self):
        """Count available slots."""
        return sum(
            1 for s in self.sensors
            if not s.is_vehicle_detected()
        )

    def get_occupied_count(self):
        """Count occupied slots."""
        return self.num_slots - \
               self.get_available_count()