"""Satın Alma Toplam Maliyet Hesaplayıcı"""
from dataclasses import dataclass

@dataclass
class SupplierCost:
    name: str
    purchase_price: float = 0.0
    rework_cost: float = 0.0
    delay_cost: float = 0.0
    quality_cost: float = 0.0
    
    @property
    def total(self) -> float:
        return self.purchase_price + self.rework_cost + self.delay_cost + self.quality_cost

def compare_suppliers(a: SupplierCost, b: SupplierCost) -> tuple:
    if a.total < b.total:
        return a, b.total - a.total
    elif b.total < a.total:
        return b, a.total - b.total
    return None, 0.0
