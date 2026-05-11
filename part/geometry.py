"""Parça geometri"""
from dataclasses import dataclass

@dataclass
class Cylinder:
    diameter_mm: float = 25.0
    length_mm: float = 100.0

@dataclass
class Plate:
    thickness_mm: float = 10.0
    width_mm: float = 50.0
    length_mm: float = 100.0

@dataclass
class Sphere:
    diameter_mm: float = 30.0
