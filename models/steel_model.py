"""Material model"""
from dataclasses import dataclass
import json, os

@dataclass
class Material:
    name: str
    composition: dict
    Ms: float = 300
    Mf: float = 150
    Ae1: float = 727
    Ae3: float = 780
    density: float = 7850
    thermal_conductivity: float = 42.0
    specific_heat: float = 475
    
    @classmethod
    def from_database(cls, name):
        db_path = os.path.join(os.path.dirname(__file__), "..", "database", "steels.json")
        with open(db_path) as f:
            db = json.load(f)
        if name not in db:
            raise KeyError(f"Steel '{name}' not found")
        data = db[name]
        return cls(
            name=name,
            composition=data["composition"],
            Ms=data.get("Ms",300),
            Mf=data.get("Mf",150),
            Ae1=data.get("Ae1",727),
            Ae3=data.get("Ae3",780),
            density=data.get("density",7850),
            thermal_conductivity=data.get("thermal_conductivity",42.0),
            specific_heat=data.get("specific_heat",475)
        )
    
    @property
    def carbon(self):
        return self.composition.get("C",0.0)
