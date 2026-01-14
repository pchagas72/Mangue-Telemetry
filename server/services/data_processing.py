"""
    This class is responsable for any processing that is needed before data is
    sent to the client interface.
"""

import math
import time

class DataProcessing:
    def __init__(self):
        self.sf_line = None # (lat, lon)
        self.sf_radius = 10 # meters
        self.current_lap_start = 0 # ms
        self.best_lap = 0  # ms
        self.lap_count = 0 # int
        self.last_pos = None # (lat, lon) or None
        self.total_distance = 0 # m
        self.lap_distance = 0 # m
        
    def set_sf_line(self, lat, lon):
        self.sf_line = (lat, lon)
        print(f"[DataProcessing] Start/Finish line set to: {self.sf_line}")

    def haversine(self, lat1, lon1, lat2, lon2):
        """ Calculates distance in meters between two coordinates """
        R = 6371000 # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def process_packet(self, data):
        """ Enriches the packet with race data """
        # Ensures that the GPS data exists
        if data.get('latitude') is None or data.get('longitude') is None:
            return data

        current_time = data.get('timestamp', time.time() * 1000)
        # Handling timestamp is to be properly defined
        try:
            current_time = float(current_time)
        except:
            current_time = time.time() * 1000

        # Initialize start time on first packet
        if self.current_lap_start == 0:
            self.current_lap_start = current_time

        # Calculate distance from S/F
        if self.sf_line:
            dist = self.haversine(data['latitude'], data['longitude'], *self.sf_line)
            
            # Must be close to line AND have spent at least 10 seconds on the lap
            # This is simple but works well
            if dist < self.sf_radius and (current_time - self.current_lap_start) > 10000:
                self.complete_lap(current_time)

            data['sf_lat'] = self.sf_line[0]
            data['sf_lon'] = self.sf_line[1]

        # Append calculated fields to the data dict
        data['lap_count'] = self.lap_count
        data['current_lap_time'] = current_time - self.current_lap_start
        data['best_lap_time'] = self.best_lap # Renamed to match frontend expectation
        data['last_lap_time'] = getattr(self, 'last_lap_time', 0)

        # Distance Calculation
        if self.last_pos != None:
            dist_delta = self.haversine(data['latitude'], data['longitude'], *self.last_pos)
            self.total_distance += dist_delta
            self.lap_distance += dist_delta
            
        self.last_pos = (data['latitude'], data['longitude'])
        
        # Add to packet
        data['total_distance'] = self.total_distance
        data['lap_distance'] = self.lap_distance
        
        return data

    def complete_lap(self, now):
        lap_time = now - self.current_lap_start
        self.lap_count += 1
        self.last_lap_time = lap_time
        self.lap_distance = 0
        
        # Check if it's a best lap (0 means unset)
        if self.best_lap == 0 or lap_time < self.best_lap:
            self.best_lap = lap_time
            print(f"[DataProcessing] New Best Lap: {self.best_lap/1000:.2f}s")
            
        self.current_lap_start = now
        print(f"[DataProcessing] Lap {self.lap_count} completed.")
