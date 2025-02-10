# diffpaircheck/config.py

import customtkinter as ctk

# Set dark mode and default color theme.
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Define interface tolerances in mm (1 mil = 0.0254 mm)
INTERFACE_TOLERANCES = {
    "USB 2.0": {"pair_tol": 150 * 0.0254, "inter_pair_tol": None},
    "USB 3.0": {"pair_tol": 2 * 0.0254, "inter_pair_tol": 5 * 0.0254},
    "USB 3.1/3.2": {"pair_tol": 2 * 0.0254, "inter_pair_tol": 5 * 0.0254},
    "USB4 / Thunderbolt 3": {"pair_tol": 1 * 0.0254, "inter_pair_tol": 3 * 0.0254},
    "Ethernet 100BASE-TX": {"pair_tol": 50 * 0.0254, "inter_pair_tol": 100 * 0.0254},
    "Ethernet 1000BASE-T": {"pair_tol": 5 * 0.0254, "inter_pair_tol": 10 * 0.0254},
    "Ethernet 10GBASE-T": {"pair_tol": 2 * 0.0254, "inter_pair_tol": 5 * 0.0254},
    "HDMI 1.4": {"pair_tol": 5 * 0.0254, "inter_pair_tol": 20 * 0.0254},
    "HDMI 2.0": {"pair_tol": 2 * 0.0254, "inter_pair_tol": 10 * 0.0254},
    "DisplayPort 1.2": {"pair_tol": 3 * 0.0254, "inter_pair_tol": 10 * 0.0254},
    "DisplayPort 2.0": {"pair_tol": 2 * 0.0254, "inter_pair_tol": 5 * 0.0254},
    "PCIe Gen1/2": {"pair_tol": 5 * 0.0254, "inter_pair_tol": 20 * 0.0254},
    "PCIe Gen3": {"pair_tol": 2 * 0.0254, "inter_pair_tol": 10 * 0.0254},
    "PCIe Gen4": {"pair_tol": 1 * 0.0254, "inter_pair_tol": 5 * 0.0254},
    "PCIe Gen5": {"pair_tol": 0.5 * 0.0254, "inter_pair_tol": 2 * 0.0254},
    "SATA 3.0": {"pair_tol": 5 * 0.0254, "inter_pair_tol": 20 * 0.0254},
    "SAS 12G": {"pair_tol": 2 * 0.0254, "inter_pair_tol": 5 * 0.0254},
    "MIPI DSI/CSI": {"pair_tol": 2 * 0.0254, "inter_pair_tol": 10 * 0.0254},
    "LVDS": {"pair_tol": 5 * 0.0254, "inter_pair_tol": 20 * 0.0254},
}

# For the dropdown menu, add an "Unassigned" option as the first item.
INTERFACE_OPTIONS = list(INTERFACE_TOLERANCES.keys())
INTERFACE_OPTIONS.insert(0, "Unassigned")
