"""Periyodik Tablo Modülü"""
import json, os

class PeriodicTable:
    def __init__(self):
        base = os.path.dirname(os.path.abspath(__file__))
        db = os.path.join(base, "..", "database")
        with open(os.path.join(db, "periodic_table.json"), encoding='utf-8') as f:
            self.elements = json.load(f)
        with open(os.path.join(db, "steel_element_effects.json"), encoding='utf-8') as f:
            self.steel_effects = json.load(f)
        with open(os.path.join(db, "element_interactions.json"), encoding='utf-8') as f:
            self.interactions = json.load(f)
        with open(os.path.join(db, "element_categories.json"), encoding='utf-8') as f:
            cat = json.load(f)
            self.categories = cat["categories"]
            self.element_cat = cat["element_cat"]

    def get(self, num):
        return self.elements.get(str(num))

    def get_effect(self, sym):
        return self.steel_effects.get(sym)

    def get_interactions(self, sym):
        return [i for i in self.interactions if sym in i["pair"]]

    def get_color(self, num):
        cat = self.element_cat.get(str(num), "bilinmeyen")
        return self.categories.get(cat, "#666666")
