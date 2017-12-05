#!/etc/python3

import math
import sys
import data


# Standard error codes as defined in sysexits.h
EX_USAGE = 64
EX_DATAERR = 65
EX_CMD_NOT_FOUND = 127


def is_number(s):
    try:
        number = float(s)
        return number
    except ValueError:
        return None


def get_options(argv):
    f_0, h, eps_r = [None] * 3
    convergence_speed = 1000  # Works for my case
    argc = len(argv)
    i = 1  # ignore argv[0], name of script
    while i < argc:
        if argv[i] == "-f" or argv[i] == "--frequency":
            i += 1
            # Check if next argument is a positive number
            f_0 = is_number(argv[i])
            if not f_0 or f_0 < 0:
                print("ERROR: center frequency must be a positive number")
                exit(EX_USAGE)
        elif argv[i] == "-z" or argv[i] == "--impedance":
            i += 1
            # Check if next argument is a positive number
            Z = is_number(argv[i])
            if not Z or Z < 0:
                print("ERROR: input impedance must be a positive number")
                exit(EX_USAGE)
        elif argv[i] == "-h" or argv[i] == "--height":
            i += 1
            # Check if next argument is a positive number
            h = is_number(argv[i])
            if not h or h < 0:
                print("ERROR: substrate height must be a positive number")
                exit(EX_USAGE)
        elif argv[i] == "-e" or argv[i] == "--eps":
            i += 1
            # Check if next argument is a positive number
            eps_r = is_number(argv[i])
            if not eps_r or eps_r < 0:
                print("ERROR: relative permittivity must be a positive number")
                exit(EX_USAGE)
        elif argv[i] == "-c" or argv[i] == "-- convergence_speed":
            i += 1
            # Check if next argument is a positive number
            convergence_speed = is_number(argv[i])
            if not convergence_speed or convergence_speed < 0:
                print("ERROR: convergence_speed must be a positive number")
                exit(EX_USAGE)
        i += 1
    if not f_0 or not h or not eps_r:
        print("ERROR: not all parameters were defined")
        exit(EX_USAGE)
    return f_0, h, eps_r, convergence_speed


# Get input impedance from electrical length and width (polynomial approximation)
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


# Get coefficients for Newton-Raphson approximation
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


# Find electrical width given electrical length and wanted impedance
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


# Get effective permittivity given patch cross-section
def get_eps_eff(W, h, eps_r):
    eps_eff = (eps_r+1)/2.0 + (eps_r-1)/2.0 / math.sqrt(1 + 10*h/W)
    return eps_eff


# Get effective length given width, height and effective permittivity
def get_effective_length(W, h, eps_eff):
    delta_L = h*0.412 * (eps_eff+0.3)/(eps_eff-0.258) * (W/h+0.264)/(W/h+0.8)
    L = 1.0/2 * lmbd_0/math.sqrt(eps_eff) - 2*delta_L
    return L

# Needed constants
c = data.c

# Design parameters and options
f_0, h, eps_r, convergence_speed = get_options(sys.argv)
names = ("Center frequency", "Substrate relative permittivity", "Substrate height")
variables = (f_0, eps_r, h)
units = ("Hz", "", "m")
print("Data recap:")
for i in range(3):
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

# Get effective permittivity
print("Calculating effective permittivity...")
eps_eff = get_eps_eff(W, h, eps_r)
print("\tEffective permittivity: " + str(eps_eff) + "\n")

# Get effective length
print("Calculating effective patch length...")
L = get_effective_length(W, h, eps_eff)
print("\tEffective patch length: " + str(L) + " m\n")

# Rinse and repeat until found L is close enough to W
print("Iterating to get length equal to width...")
max_error = 0.00001
sys.stdout.write('\t')
while abs(W-L) > max_error:
    sys.stdout.write('.')
    W = L
    eps_eff = get_eps_eff(W, h, eps_r)
    L = get_effective_length(W, h, eps_eff)
L_norm = L/lmbd_0
W_norm = W/lmbd_0

# Get final input impedance
print("Calculating input impedance...")
G_rad = get_G_rad(L_norm, W_norm)
Z_in = 1/G_rad
print("\tInput impedance: " + str(Z_in) + " Ohm\n")


# Design results
print("\n\nDesign results:")
print("\tPatch length: " + str(L) + " m")
print("\tPatch width: " + str(W) + " m")
print("\tSubstrate height: " + str(h) + " m")
print("\tSubstrate permittivity: " + str(eps_r))
print("\tInput impedance: " + str(Z_in) + "\n")

# Clean exit
exit(0)
