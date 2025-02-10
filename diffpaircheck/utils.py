# diffpaircheck/utils.py

def get_matching_key(signal_name):
    """
    Given a full signal name that ends with '_N' or '_P', return the grouping key.
    If the signal name has exactly two tokens (e.g. "DP_N"), the key is just the first token.
    If it has three or more tokens (e.g. "HDMI0_TDMS0_N"), the key is built from the first token
    (the expansion) and the token immediately before the trailing channel indicator.
    """
    tokens = signal_name.split("_")
    if len(tokens) == 2:
        return tokens[0]
    elif len(tokens) >= 3:
        return tokens[0] + "_" + tokens[-2]
    else:
        return signal_name

def recommend_interface_for_pair(pair):
    """
    Given a differential pair (a dict with keys "N", "P", and "key"),
    return a recommended interface.
    
    This function splits the grouping key into an expansion and a base.
    If an overriding recommendation is found based on the expansion (e.g. "PCIE" or "HDMI"),
    that takes precedence. Otherwise, the base token is used.
    """
    group_key = pair["key"]
    tokens = group_key.split("_")
    if len(tokens) == 1:
        expansion = ""
        base = tokens[0]
    else:
        expansion = tokens[0]
        base = tokens[1]
    
    if expansion.upper().startswith("PCIE"):
        return "PCIe Gen1/2"
    if expansion.upper().startswith("HDMI"):
        if base.upper().startswith("TMDS") or base.upper().startswith("TDMS"):
            return "HDMI 1.4"
    if expansion.upper().startswith("USB3"):
        if base.upper() in ["SSRX", "SSTX"]:
            return "USB 3.0"
    
    pk = base.upper()
    if pk == "DP":
        return "USB 2.0"
    elif pk in ["SSRX", "SSTX"]:
        return "USB 3.0"
    elif pk in ["HSRX", "HSTX"]:
        return "USB4 / Thunderbolt 3"
    elif pk in ["TD", "RD"]:
        return "Ethernet 100BASE-TX"
    elif pk in ["TXA", "TXB", "TXC", "TXD"]:
        return "Ethernet 10GBASE-T"
    elif pk in ["TX1", "TX2", "TX3", "TX4"]:
        return "Ethernet 1000BASE-T"
    elif pk.startswith("TMDS") or pk.startswith("TDMS"):
        return "HDMI 1.4"
    elif pk.startswith("ML") or pk == "AUX":
        return "DisplayPort 1.2"
    elif pk.startswith("PCIE"):
        return "PCIe Gen1/2"
    elif pk.startswith("SATA"):
        return "SATA 3.0"
    elif pk.startswith("SAS"):
        return "SAS 12G"
    elif pk.startswith("DSID") or pk.startswith("DSIC") or pk.startswith("DSI") or pk.startswith("CSI"):
        return "MIPI DSI/CSI"
    elif pk.startswith("LVDS"):
        return "LVDS"
    return "Unassigned"
