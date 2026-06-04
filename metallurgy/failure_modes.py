"""Malzeme Hata Modları Modülü"""
import json, os

class FailureModes:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "..", "database", "failure_modes.json")
        with open(path, encoding='utf-8') as f:
            self.data = json.load(f)
    
    def get_all(self): return self.data
    def get_modes(self): return self.data["modes"]
    def get_intro(self): return self.data["intro"]
    def get_prevention(self): return self.data["prevention"]
    def get_fractography(self): return self.data["fractography"]
