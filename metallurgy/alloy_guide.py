"""Alaşım Elementleri Rehberi Modülü"""
import json, os

class AlloyGuide:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "..", "database", "alloy_effects.json")
        with open(path, encoding='utf-8') as f:
            self.data = json.load(f)
    
    def get_all(self): return self.data
    def get_elements(self): return self.data["elements"]
    def get_classification(self): return self.data["classification"]
    def get_trends(self): return self.data["trends"]
    def get_examples(self): return self.data["examples"]