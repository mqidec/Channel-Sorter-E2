# sorter.py

def extract_sid_key(service_line):
    try:
        if not service_line.startswith("1:"):
            return "0:0:0"
        parts = service_line.split(":")
        sid = parts[3].lower()
        tsid = parts[4].lower()
        nid = parts[5].lower()
        return f"{sid}:{tsid}:{nid}"
    except Exception:
        return "0:0:0"

def parse_lamedb(filepath="/etc/enigma2/lamedb"):
    freq_map = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except IOError:
        return freq_map

    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.count(":") == 2:
            key = line.lower()
            index += 2
            if index < len(lines):
                freq_line = lines[index].strip()
                parts = freq_line.split()
                if len(parts) >= 2:
                    try:
                        freq = int(parts[1])
                    except ValueError:
                        freq = 0
                    freq_map[key] = freq
            index += 1
        else:
            index += 1
    return freq_map
