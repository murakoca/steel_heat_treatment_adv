
"""Kapsamlı Veri Analizi (Origin benzeri)"""
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

def linear_fit(x, y):
    slope, intercept, r, p, std = stats.linregress(x, y)
    return {'slope': slope, 'intercept': intercept, 'r_squared': r**2}

def poly_fit(x, y, degree=2):
    coeffs = np.polyfit(x, y, degree)
    y_pred = np.polyval(coeffs, x)
    r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)
    return {'coeffs': coeffs.tolist(), 'r_squared': r2, 'y_pred': y_pred}

def exp_fit(x, y):
    try:
        popt, _ = curve_fit(lambda x, a, b: a * np.exp(b * x), x, y, p0=[1, 0.1])
        y_pred = popt[0] * np.exp(popt[1] * x)
        r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)
        return {'a': popt[0], 'b': popt[1], 'r_squared': r2}
    except:
        return None

def gaussian_fit(x, y):
    def gauss(x, a, mu, sigma):
        return a * np.exp(-(x - mu)**2 / (2 * sigma**2))
    try:
        popt, _ = curve_fit(gauss, x, y, p0=[max(y), np.mean(x), np.std(x)])
        y_pred = gauss(x, *popt)
        r2 = 1 - np.sum((y - y_pred)**2) / np.sum((y - np.mean(y))**2)
        return {'amplitude': popt[0], 'mean': popt[1], 'sigma': popt[2], 'r_squared': r2}
    except:
        return None

def descriptive_stats(data):
    d = np.array(data)
    return {'mean': np.mean(d), 'std': np.std(d, ddof=1), 'skew': stats.skew(d), 'kurtosis': stats.kurtosis(d)}

def anova(*groups):
    return stats.f_oneway(*groups)
