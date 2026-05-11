"""Fırın profili"""
class FurnaceProfile:
    def __init__(self):
        self.segments = []
    def add_segment(self, time_min, temp_C):
        self.segments.append((time_min * 60, temp_C))
    def get_temperature(self, time_s):
        if not self.segments:
            return 850.0
        for t_end, T in self.segments:
            if time_s <= t_end:
                return T
        return self.segments[-1][1]
