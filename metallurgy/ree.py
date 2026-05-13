"""Nadir Toprak Elementleri Modülü"""
import json, os

class REEDatabase:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "..", "database", "ree_data.json")
        with open(path, encoding='utf-8') as f:
            self.data = json.load(f)
    
    def get_all(self): return self.data
    def get_applications(self): return self.data["applications"]
    def get_usage_distribution(self): return self.data["usage_distribution"]
    def get_extraction_steps(self): return self.data["extraction_steps"]
    def get_minerals(self): return self.data["minerals"]
