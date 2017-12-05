# Python script to design patch antennas

PyPatch calculates, given center frequency, substrate properties and input impedance,
the physical dimensions of the patch.

Usage:

python patch_design.py -f <center_frequency> -z <input_impedance> -h <substrate_height> -e <substrate_relative_permittivity>
[-c <convergence_speed>]

Default convergence speed is 1000 which seems to work fine, setting it too high will get the algorithm to diverge, setting
it low will just make it run longer.
