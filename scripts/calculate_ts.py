import numpy as np
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt

from ts_elastic_spheres.backscatter import target_strength
from ts_elastic_spheres.materials import MATERIALS


plt.close("all")


# ==============================================================
# Sphere
# ==============================================================

material_name = "Tungsten Carbide"
material = MATERIALS[material_name]

sphere_diameter = 38.1e-3  # m
sphere_radius = sphere_diameter / 2.0


# ==============================================================
# Water properties
# ==============================================================

rho_water = 1027.0  # kg/m^3
c_water = 1500.0    # m/s


# ==============================================================
# Frequency
# ==============================================================

f_start = 38_000.0   # Hz
f_end = 260_000.0    # Hz
delta_f = 500.0      # Hz

frequencies = np.arange(f_start, f_end, delta_f)


# ==============================================================
# Numerical parameters
# ==============================================================

far_field_distance = 100.0  # m

expansion_order = int(sphere_radius * 2.0 * np.pi * f_end / c_water) + 20

print(f"Material: {material_name}")
print(f"Sphere diameter: {sphere_diameter * 1e3:.1f} mm")
print(f"Expansion order: {expansion_order}")
print(f"Number of frequencies: {len(frequencies)}")


# ==============================================================
# Calculate target strength
# ==============================================================

TS = np.empty(len(frequencies))

for ii, frequency in enumerate(frequencies):
    TS[ii] = target_strength(
        sphere_radius,
        frequency,
        rho_water,
        c_water,
        material["density"],
        material["c_compressional"],
        material["c_shear"],
        far_field_distance,
        expansion_order,
    )


# ==============================================================
# Plot
# ==============================================================

fig, ax = plt.subplots(figsize=(8, 7))

ax.plot(
    frequencies / 1e3,
    TS,
    label=f"{sphere_diameter * 1e3:.1f} mm {material_name} sphere",
)

ax.set_xlabel("Frequency (kHz)")
ax.set_ylabel("Target Strength (dB)")
ax.grid(True, alpha=0.3)
ax.legend()

fig.tight_layout()

plt.show()