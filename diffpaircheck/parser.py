# diffpaircheck/parser.py

from diffpaircheck import utils

def parse_file(filename):
    """
    Parse the text file and return a list of differential pairs.
    The file should have at least two columns: the signal name and its length (in mm).
    Only signals whose names end with '_N' or '_P' are retained.
    
    Grouping is done by collecting signals by their grouping key (using utils.get_matching_key)
    and then pairing the _N and _P signals in the order they are encountered.
    """
    raw_signals = []
    with open(filename, "r") as f:
        lines = f.readlines()
    data_started = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if not data_started:
            if "l [mm]" in line or "Signal" in line:
                data_started = True
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        signal_name = parts[0].strip()
        try:
            length = float(parts[1].strip())
        except ValueError:
            continue
        raw_signals.append((signal_name, length))
    # Filter signals: keep only those ending with _N or _P.
    filtered = [(name, length) for name, length in raw_signals if name.endswith("_N") or name.endswith("_P")]
    groups = {}  # key: grouping key, value: {"N": [], "P": []}
    for name, length in filtered:
        key = utils.get_matching_key(name)
        channel = name[-1]  # "N" or "P"
        if key not in groups:
            groups[key] = {"N": [], "P": []}
        groups[key][channel].append((name, length))
    pairs = []
    for key, channels in groups.items():
        list_n = channels["N"]
        list_p = channels["P"]
        pair_count = min(len(list_n), len(list_p))
        for i in range(pair_count):
            pairs.append({"key": key, "N": list_n[i], "P": list_p[i]})
        if len(list_n) > pair_count:
            for extra in list_n[pair_count:]:
                pairs.append({"key": key, "N": extra, "P": None})
        if len(list_p) > pair_count:
            for extra in list_p[pair_count:]:
                pairs.append({"key": key, "N": None, "P": extra})
    return pairs
