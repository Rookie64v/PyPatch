# Python script to design patch antennas

PyPatch calculates, given center frequency, substrate properties and input impedance,
the physical dimensions of the patch. patch_design.py designs a rectangular patch starting from substrate characteristics, desired center frequency and desired input impedance, while square_patch.py designs a square patch starting from substrate characteristics and desired center frequency (input impedance cannot be adjusted without an inset feeding like a coaxial probe).

Usage:

python patch_design.py -f <center_frequency> -z <input_impedance> -h <substrate_height> -e <substrate_relative_permittivity>
[-c <convergence_speed>]

python square_patch.py -f <center_frequency> -h <substrate_height> -e <substrate_relative_permittivity>

Default convergence speed is 1000 which seems to work fine, setting it too high will get the algorithm to diverge, setting
it low will just make it run longer.
