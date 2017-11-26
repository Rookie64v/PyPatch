"""Miscellaneous functions not directly related to patch design"""

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
    f_0, Z, h, eps_r = [None] * 4
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
    if not f_0 or not Z or not h or not eps_r:
        print("ERROR: not all parameters were defined")
        exit(EX_USAGE)
    return f_0, Z, h, eps_r, convergence_speed
