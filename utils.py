import cmath
from math import sqrt
import numpy as np

# Speed of light
C = 299.792458 * (10**6)


# Wave length
def WL(f):
    return C / f


# Normalized impedance to Reflection coefficient (Gamma)
def z2RefCoef(z):
    g = (z - 1) / (z + 1)
    return g


# Reflection coefficient (Gamma) angle from normalized impedance
def z2RefCoefPhDeg(z):
    g = z2RefCoef(z)
    gRad = cmath.phase(g)
    gDeg = np.degrees(gRad)
    return gDeg


# Reflection coefficient (Gamma) modulus from normalized impedance
def z2RefCoefAmp(z):
    g = z2RefCoef(z)
    gpolar = cmath.polar(g)
    return gpolar[0]


# VSWR from Gamma
def vswr(g):
    gabs = cmath.polar(g)[0]
    v = (1 + gabs) / (1 - gabs)
    return v


# calculate propagation velocity in cable
def cableVP(cable):
    if cable == "RG-213" or cable == "RG-214":
        # Polyethylene
        epsilonr = 2.29
    v = C / sqrt(epsilonr)
    return v


# calculate propagation velocity in cable
def cableWL(vp, f):
    wl = vp / f
    return wl


# propagation constant (beta)
def beta(vp, f):
    b = (2 * np.pi * f) / vp
    return b


def complexReciprocal(t):
    try:
        c = complex(t)
        if cmath.isinf(c):
            return 0 + 0j
        if c.real == 0 and c.imag == 0:
            return complex("inf")
        else:
            return 1 / c
    except ValueError:
        return complex("inf")


def Zi(Z0, ZL, v, f, L):
    """
    Finds new Z for line terminated with ZL
    works also to find new Y if a line is terminated with YL
    """
    b = beta(v, f)
    t = np.tan(b * L)
    Z = (Z0 * (ZL + 1j * Z0 * t)) / (Z0 + 1j * ZL * t)
    return Z
