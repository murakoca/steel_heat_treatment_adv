"""Thermodynamic calculations"""
import numpy as np
def calculate_Ms(comp: dict) -> float:
    C = comp.get("C",0)*100; Mn = comp.get("Mn",0)*100; Si = comp.get("Si",0)*100
    Cr = comp.get("Cr",0)*100; Ni = comp.get("Ni",0)*100; Mo = comp.get("Mo",0)*100
    return 539 - 423*C - 30.4*Mn - 17.7*Ni - 12.1*Cr - 7.5*Mo
