#!/usr/bin/python

import math
import sys
import support
import data


# Function to get input impedance from electrical length and width (polynomial approximation)
def get_G_rad(L_norm, W_norm):
    c_rows = len(data.G_rad_coefficients)
    c_cols = len(data.G_rad_coefficients[0])
    w_coefficients = []
    for i in range(c_rows):
        l_coefficients = data.G_rad_coefficients[i]  # i_th row of coefficient matrix
        w_coeff = 0
        # (a2, a1, a0) = l_coefficients
        # w_coeff = a2 * L_norm**2 + a1 * L_norm**1 + a0 * L_norm**0
        for j in range(c_cols):
            l_coeff = l_coefficients[j]
            w_coeff += l_coeff * L_norm**(c_cols-1-j)
        w_coefficients.append(w_coeff)
    # Now we have w_coefficients
    G_rad = 0
    for i in range(c_rows):
        w_coeff = w_coefficients[i]
        G_rad += w_coeff * W_norm**(c_rows-1-i)
    # Get results from mS to S
    G_rad *= 0.001
    return G_rad


# Function to get coefficients for Newton-Raphson approximation
def get_coeff(L_norm, W_norm):
    C = data.G_rad_coefficients
    c_rows = len(C)
    c_cols = len(C[0])
    C_w = [0] * c_rows
    for i in range(c_rows):
        for j in range(c_cols):
            C_w[i] += C[i][j] * L_norm**(c_cols-1-j)
    C_l = [0] * c_cols
    for j in range(c_cols):
        for i in range(c_rows):
            C_l[j] += C[i][j] * W_norm**(c_rows-i-j)
    return C_l, C_w


# Function to find, given the electrical length, the electrical width that guarantees the wanted input impedance
def get_W_norm(L_norm, W_norm, Z_target, C_w, convergence_speed):
    global G_rad
    global Z_in
    G_rad_target = 1.0/Z_target
    # Loop a Newton-Raphson refinement
    sys.stdout.write('\t')
    for i in range(50):
        sys.stdout.write('.')
        W_norm = W_norm + (G_rad_target-G_rad)/(2*C_w[0]*W_norm+C_w[1])*convergence_speed
        G_rad = get_G_rad(L_norm, W_norm)
        Z_in = 1/G_rad
        if abs(Z_target-Z_in) < 0.000001:
            break
    sys.stdout.write('\n')
    return W_norm


def get_eps_eff(W, h, eps_r):
    eps_eff = (eps_r+1)/2.0 + (eps_r-1)/2.0 / math.sqrt(1 + 10*h/W)
    return eps_eff


def get_effective_length(W, h, eps_eff):
    delta_L = h*0.412 * (eps_eff+0.3)/(eps_eff-0.258) * (W/h+0.264)/(W/h+0.8)
    L = 1.0/2 * lmbd_0/math.sqrt(eps_eff) - 2*delta_L
    return L

# Needed constants
c = 299792458  # about 3*10**8 m/s

# Design parameters and options
f_0, Z_target, h, eps_r, convergence_speed = support.get_options(sys.argv)
names = ("Center frequency", "Maximum input impedance", "Substrate relative permittivity", "Substrate height")
variables = (f_0, Z_target, eps_r, h)
units = ("Hz", "Ohm", "", "m")
print("Data recap:")
for i in range(4):
    print("\t" + names[i] + ": " + str(variables[i]) + " " + units[i])
print()

# Get free-space wavelength
print("Calculating free-space wavelength...")
lmbd_0 = 1.0*c/f_0
print("\tFree-space wavelength: " + str(lmbd_0) + " m\n")

# Guess patch length
print("Calculating tentative patch length...")
L = 1.0/2*lmbd_0/math.sqrt(eps_r)
L_norm = L/lmbd_0  # Electrical length
if L_norm < 0.2 or L_norm > 0.5:  # Polynomial approximation for G_rad not valid
    print("\tWARNING: electrical length of patch is " + str(L_norm) +
          ", approximations are valid in range 0.2 to 0.5.")
    print("\tResults might be inaccurate")
print("\tTentative patch length: " + str(L) + " m\n")

# Guess patch width
print("Calculating tentative patch width...")
W = L  # In absence of better ideas, just start from a square patch
W_norm = L_norm
if W_norm < 0.35:  # If we are outside of range of polynomial approximation for G_rad
    W_norm = 0.35
    W = W_norm * lmbd_0
if W_norm > 1:  # If we are outside of range of polynomial approximation for G_rad
    W_norm = 1
    W = lmbd_0
print("\tTentative patch width: " + str(W) + " m\n")

# Get approximate input impedance
print("Calculating input impedance...")
G_rad = get_G_rad(L_norm, W_norm)
Z_in = 1/G_rad
print("\tInput impedance: " + str(Z_in) + " Ohm\n")

# Results likely to be completely off from what we want, modify W to get better Z_in
print("Iterating to get better input impedance...")
C_l, C_w = get_coeff(L_norm, W_norm)
W_norm = get_W_norm(L_norm, W_norm, Z_target, C_w, convergence_speed)
W = W_norm*lmbd_0
G_rad = get_G_rad(L_norm, W_norm)
Z_in = 1.0/G_rad
print("\tPatch width: " + str(W) + " m")
print("\tInput impedance: " + str(Z_in) + " Ohm\n")

# Get effective permittivity
print("Calculating effective permittivity")
eps_eff = get_eps_eff(W, h, eps_r)
print("\tEffective permittivity: " + str(eps_eff) + "\n")

# Get effective length
print("Calculating effective patch length")
L = get_effective_length(W, h, eps_eff)
print("Effective patch length: " + str(L) + " m\n")

# Design results
print("\n\nDesign results:")
print("\tPatch length: " + str(L) + " m")
print("\tPatch width: " + str(W) + " m")
print("\tSubstrate height: " + str(h) + " m")
print("\tSubstrate permittivity: " + str(eps_r) + "\n")