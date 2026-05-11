"""Scheil additivity rule"""
import numpy as np
def get_tau_from_ttt(T, TTT_curve):
    T_arr = np.array(TTT_curve["T"])
    t_arr = np.array(TTT_curve["t"])
    if T > T_arr[0] or T < T_arr[-1]: return np.inf
    return np.interp(T, T_arr[::-1], t_arr[::-1])
