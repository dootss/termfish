import struct
import os
import time
import sys
import yaml
from datetime import datetime
from pathlib import Path


# --- config ---

SCRIPT_DIR = Path(__file__).resolve().parent

DEFAULT_CONFIG = """\
# path to your webfishing save directory
# usually here on windows
save_directory: "%AppData%/Godot/app_userdata/webfishing_2_newver"

# which save slot to read (1-4)
save_slot: 1

# how often code check the save file for changes (seconds)
# note this is not how often it will update because the game autosaves every 5 minutes.
poll_interval: 2

# if u don't use windows terminal, this probably won't do anything. otherwise it'll change the tab color & name
windows_terminal:
  enabled: true
  tab_title: "termfish"
  tab_color: "FFB6C1"
"""


def load_config():
    config_path = SCRIPT_DIR / "config.yaml"
    if not config_path.exists():
        config_path.write_text(DEFAULT_CONFIG)
        print(f"created default config.yaml at {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def resolve_save_path(config):
    directory = os.path.expandvars(config.get("save_directory", ""))
    slot = config.get("save_slot", 2)
    filename = f"webfishing_save_slot_{slot - 1}.sav"
    return os.path.join(directory, filename)


def setup_terminal(config):
    # enable ansi on windows
    os.system("")
    wt = config.get("windows_terminal", {})
    if not wt.get("enabled", False):
        return
    title = wt.get("tab_title", "")
    if title:
        sys.stdout.write(f"\x1b]2;{title}\x07")
    color_hex = wt.get("tab_color", "")
    if color_hex:
        color_hex = color_hex.lstrip("#")
        if len(color_hex) == 6:
            r = int(color_hex[0:2], 16) * 257
            g = int(color_hex[2:4], 16) * 257
            b = int(color_hex[4:6], 16) * 257
            sys.stdout.write(f"\x1b]4;264;rgb:{r:04x}/{g:04x}/{b:04x}\x1b\\")
    sys.stdout.flush()


# --- ansi ---

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[90m"
WHITE = "\033[97m"

QUALITY_INFO = {
    0: {"name": "Normal",     "color": "\033[38;5;180m", "bright": "\033[1;38;5;180m"},
    1: {"name": "Shining",    "color": "\033[38;5;137m", "bright": "\033[1;38;5;137m"},
    2: {"name": "Glistening", "color": "\033[38;5;247m", "bright": "\033[1;38;5;247m"},
    3: {"name": "Opulent",    "color": "\033[38;5;30m",  "bright": "\033[1;38;5;30m"},
    4: {"name": "Radiant",    "color": "\033[38;5;172m", "bright": "\033[1;38;5;172m"},
    5: {"name": "Alpha",      "color": "\033[38;5;161m", "bright": "\033[1;38;5;161m"},
}

BLOCK_FILLED = "\u2b1b"
BLOCK_EMPTY = "\u2b1c"
NAME_WIDTH = 20


# --- fish data ---

LOCATION_STYLE = {
    "lake":        {"name": "FRESHWATER", "bg": "\033[48;5;194m\033[38;5;22m"},
    "ocean":       {"name": "SALTWATER",  "bg": "\033[48;5;189m\033[38;5;18m"},
    "rain":        {"name": "RAIN",       "bg": "\033[48;5;195m\033[38;5;23m"},
    "water_trash": {"name": "TRASH",      "bg": "\033[48;5;230m\033[38;5;94m"},
    "alien":       {"name": "ALIEN",      "bg": "\033[48;5;225m\033[38;5;54m"},
    "void":        {"name": "VOID",       "bg": "\033[48;5;219m\033[38;5;54m"},
}

LOCATION_ORDER = ["lake", "ocean", "water_trash", "rain", "void", "alien"]

FISH_ORDER = {
    "lake": [
        "fish_lake_alligator", "fish_lake_axolotl", "fish_lake_bass", "fish_lake_bluegill",
        "fish_lake_bowfin", "fish_lake_bullshark", "fish_lake_carp", "fish_lake_catfish",
        "fish_lake_crab", "fish_lake_crappie", "fish_lake_crayfish", "fish_lake_drum",
        "fish_lake_frog", "fish_lake_gar", "fish_lake_golden_bass", "fish_lake_goldfish",
        "fish_lake_guppy", "fish_lake_kingsalmon", "fish_lake_koi", "fish_lake_leech",
        "fish_lake_mooneye", "fish_lake_muskellunge", "fish_lake_perch", "fish_lake_pike",
        "fish_lake_pupfish", "fish_lake_rainbowtrout", "fish_lake_salmon", "fish_lake_snail",
        "fish_lake_sturgeon", "fish_lake_toad", "fish_lake_turtle", "fish_lake_walleye",
    ],
    "ocean": [
        "fish_ocean_angelfish", "fish_ocean_atlantic_salmon", "fish_ocean_bluefish",
        "fish_ocean_clownfish", "fish_ocean_coalacanth", "fish_ocean_dogfish", "fish_ocean_eel",
        "fish_ocean_flounder", "fish_ocean_golden_manta_ray", "fish_ocean_greatwhiteshark",
        "fish_ocean_grouper", "fish_ocean_hammerhead_shark", "fish_ocean_herring", "fish_ocean_krill",
        "fish_ocean_lionfish", "fish_ocean_lobster", "fish_ocean_manowar", "fish_ocean_manta_ray",
        "fish_ocean_marlin", "fish_ocean_octopus", "fish_ocean_oyster", "fish_ocean_sawfish",
        "fish_ocean_sea_turtle", "fish_ocean_seahorse", "fish_ocean_shrimp", "fish_ocean_squid",
        "fish_ocean_stingray", "fish_ocean_sunfish", "fish_ocean_swordfish", "fish_ocean_tuna",
        "fish_ocean_whale", "fish_ocean_wolffish",
    ],
    "water_trash": [
        "wtrash_bone", "wtrash_boot", "wtrash_branch", "wtrash_diamond",
        "wtrash_drink_rings", "wtrash_plastic_bag", "wtrash_sodacan", "wtrash_weed",
    ],
    "rain": [
        "fish_rain_anomalocaris", "fish_rain_heliocoprion",
        "fish_rain_horseshoe_crab", "fish_rain_leedsichthys",
    ],
    "void": ["fish_void_voidfish"],
    "alien": ["fish_alien_dog"],
}

# fish whose display name can't be derived from their id
NAME_OVERRIDES = {
    "fish_alien_dog": "UFO",
    "fish_deep_test": "Axolotl",
    "fish_deep_testb": "Axolotl",
    "fish_deep_testc": "Axolotl",
    "fish_lake_bass": "Largemouth Bass",
    "fish_lake_bullshark": "Bull Shark",
    "fish_lake_kingsalmon": "King Salmon",
    "fish_lake_rainbowtrout": "Rainbow Trout",
    "fish_ocean_coalacanth": "Coelacanth",
    "fish_ocean_greatwhiteshark": "Great White Shark",
    "fish_ocean_manowar": "Man O' War",
    "fish_ocean_stingray": "Sting Ray",
    "fish_rain_heliocoprion": "Helicoprion",
    "fish_void_voidfish": "CREATURE",
    "wtrash_boot": "Old Boot",
    "wtrash_sodacan": "Soda Can",
}

PREFIXES = ("fish_lake_", "fish_ocean_", "fish_rain_", "fish_void_", "fish_alien_", "fish_deep_", "wtrash_")


def _derive_name(fish_id):
    for prefix in PREFIXES:
        if fish_id.startswith(prefix):
            return fish_id[len(prefix):].replace("_", " ").title()
    return fish_id


def _build_fish_names():
    names = {}
    for fish_list in FISH_ORDER.values():
        for fish_id in fish_list:
            names[fish_id] = NAME_OVERRIDES.get(fish_id, _derive_name(fish_id))
    for fish_id, name in NAME_OVERRIDES.items():
        if fish_id not in names:
            names[fish_id] = name
    return names


FISH_NAMES = _build_fish_names()


# --- godot 3.x binary variant parser (read-only) ---

def _read_uint16(data, pos):
    return struct.unpack_from("<H", data, pos)[0], pos + 2

def _read_uint32(data, pos):
    return struct.unpack_from("<I", data, pos)[0], pos + 4

def _read_int32(data, pos):
    return struct.unpack_from("<i", data, pos)[0], pos + 4

def _read_int64(data, pos):
    return struct.unpack_from("<q", data, pos)[0], pos + 8

def _read_float(data, pos):
    return struct.unpack_from("<f", data, pos)[0], pos + 4

def _read_double(data, pos):
    return struct.unpack_from("<d", data, pos)[0], pos + 8

def _read_string(data, pos):
    length, pos = _read_uint32(data, pos)
    s = data[pos:pos + length].decode("utf-8")
    pos += length
    pos += (4 - (length % 4)) % 4
    return s, pos

def _read_variant(data, pos):
    vtype, pos = _read_uint16(data, pos)
    flags, pos = _read_uint16(data, pos)
    is_64 = (flags & 1) != 0

    if vtype == 0:
        return None, pos
    elif vtype == 1:
        val, pos = _read_uint32(data, pos)
        return val != 0, pos
    elif vtype == 2:
        return _read_int64(data, pos) if is_64 else _read_int32(data, pos)
    elif vtype == 3:
        return _read_double(data, pos) if is_64 else _read_float(data, pos)
    elif vtype == 4:
        return _read_string(data, pos)
    elif vtype == 5:
        if is_64:
            x, pos = _read_double(data, pos)
            y, pos = _read_double(data, pos)
        else:
            x, pos = _read_float(data, pos)
            y, pos = _read_float(data, pos)
        return (x, y), pos
    elif vtype == 7:
        if is_64:
            x, pos = _read_double(data, pos)
            y, pos = _read_double(data, pos)
            z, pos = _read_double(data, pos)
        else:
            x, pos = _read_float(data, pos)
            y, pos = _read_float(data, pos)
            z, pos = _read_float(data, pos)
        return (x, y, z), pos
    elif vtype == 14:
        r, pos = _read_float(data, pos)
        g, pos = _read_float(data, pos)
        b, pos = _read_float(data, pos)
        a, pos = _read_float(data, pos)
        return (r, g, b, a), pos
    elif vtype == 15:
        name_count, pos = _read_uint32(data, pos)
        subname_count = (name_count >> 16) & 0xFFFF
        name_count = name_count & 0xFFFF
        _, pos = _read_uint32(data, pos)
        parts = []
        for _ in range(name_count + subname_count):
            s, pos = _read_string(data, pos)
            parts.append(s)
        return "/".join(parts), pos
    elif vtype == 18:
        size, pos = _read_uint32(data, pos)
        size &= 0x7FFFFFFF
        result = {}
        for _ in range(size):
            key, pos = _read_variant(data, pos)
            val, pos = _read_variant(data, pos)
            result[key] = val
        return result, pos
    elif vtype == 19:
        size, pos = _read_uint32(data, pos)
        size &= 0x7FFFFFFF
        result = []
        for _ in range(size):
            val, pos = _read_variant(data, pos)
            result.append(val)
        return result, pos
    elif vtype == 20:
        length, pos = _read_uint32(data, pos)
        val = data[pos:pos + length]
        pos += length
        pos += (4 - (length % 4)) % 4
        return val, pos
    elif vtype in (21, 22, 23):
        length, pos = _read_uint32(data, pos)
        vals = []
        for _ in range(length):
            if vtype == 21:
                v, pos = _read_int32(data, pos)
            elif vtype == 22:
                v, pos = _read_float(data, pos)
            else:
                v, pos = _read_string(data, pos)
            vals.append(v)
        return vals, pos
    else:
        raise ValueError(f"unsupported godot variant type: {vtype} at position {pos - 4}")


def read_save(path):
    data = Path(path).read_bytes()
    _size, pos = _read_uint32(data, 0)
    save_data, _ = _read_variant(data, pos)
    return save_data


def safe_read_save(path):
    try:
        return read_save(path)
    except (OSError, PermissionError, struct.error, ValueError, UnicodeDecodeError, OverflowError):
        return None


# --- journal extraction ---

def extract_journal(save_data):
    journal = save_data.get("journal", {})
    snapshot = {}
    counts = {}
    for location, fish_dict in journal.items():
        if not isinstance(fish_dict, dict):
            continue
        for fish_id, info in fish_dict.items():
            if fish_id.startswith("_") or not isinstance(info, dict):
                continue
            if fish_id not in FISH_NAMES:
                continue
            qualities = info.get("quality", [])
            snapshot[(location, fish_id)] = set(int(q) for q in qualities) if isinstance(qualities, list) else set()
            counts[(location, fish_id)] = info.get("count", 0)
    return snapshot, counts


# --- display ---

def make_row(name, qualities, bg, count=0, new_qualities=None):
    if new_qualities is None:
        new_qualities = set()
    name_part = f"{bg} {name:<{NAME_WIDTH}} {RESET}"
    cells = ""
    for q in range(6):
        info = QUALITY_INFO[q]
        if q in new_qualities or q in qualities:
            cells += f" {info['bright']}{BLOCK_FILLED}{RESET}  "
        else:
            cells += f" {DIM}{BLOCK_EMPTY}{RESET}  "
    count_str = f"{DIM}x{count}{RESET}" if count else ""
    return f"{name_part}{cells} {count_str}"


def make_stats(snapshot):
    total_fish = len(snapshot)
    if total_fish == 0:
        return ""

    lines = []
    lines.append(f"  {BOLD}{WHITE}COMPLETION{RESET}")
    lines.append("")

    total_owned = 0
    total_slots = total_fish * 6

    for q in range(6):
        info = QUALITY_INFO[q]
        count = sum(1 for qualities in snapshot.values() if q in qualities)
        pct = (count / total_fish) * 100
        total_owned += count

        bar_filled = int(pct / 5)
        bar_empty = 20 - bar_filled
        bar = f"{info['color']}{chr(0x2588) * bar_filled}{DIM}{chr(0x2591) * bar_empty}{RESET}"

        lines.append(f"  {info['bright']}{info['name']:<12}{RESET} {bar} {BOLD}{WHITE}{pct:5.1f}%{RESET}")

    total_pct = (total_owned / total_slots) * 100 if total_slots else 0
    lines.append(f"  {'':12} {'':20} {'':5}")
    bar_filled = round(total_pct / 5)
    bar_empty = 20 - bar_filled
    bar = f"{WHITE}{chr(0x2588) * bar_filled}{DIM}{chr(0x2591) * bar_empty}{RESET}"
    lines.append(f"  {BOLD}{WHITE}{'Total':<12}{RESET} {bar} {BOLD}{WHITE}{total_pct:5.1f}%{RESET}")
    lines.append(f"  {DIM}{total_owned}/{total_slots} uniques{RESET}")

    return "\n".join(lines)


def build_display(snapshot, counts, total_caught, mtime, newly_obtained=None):
    if newly_obtained is None:
        newly_obtained = {}

    lines = []

    for location_key in LOCATION_ORDER:
        style = LOCATION_STYLE.get(location_key)
        if not style:
            continue

        order = FISH_ORDER.get(location_key, [])
        caught_here = {fid: qualities for (location, fid), qualities in snapshot.items() if location == location_key}
        ordered_ids = [fid for fid in order if fid in caught_here]
        ordered_ids += [fid for fid in caught_here if fid not in order]
        if not ordered_ids:
            continue

        for fish_id in ordered_ids:
            name = FISH_NAMES.get(fish_id, fish_id)
            qualities = caught_here[fish_id]
            new_quals = newly_obtained.get((location_key, fish_id), set())
            count = counts.get((location_key, fish_id), 0)
            lines.append(make_row(name, qualities, style["bg"], count, new_quals))

    lines.append("")
    lines.append(make_stats(snapshot))
    lines.append(f"  {DIM}total catches: {total_caught}{RESET}")
    timestamp = datetime.fromtimestamp(mtime).strftime("%H:%M:%S")
    lines.append(f"  {DIM}last updated {timestamp}{RESET}")

    return "\n".join(lines)


def format_new_log(fish_id, location, new_qualities):
    name = FISH_NAMES.get(fish_id, fish_id)
    timestamp = datetime.now().strftime("%H:%M:%S")

    entries = []
    for q in sorted(new_qualities):
        info = QUALITY_INFO[q]
        entries.append(f"  {DIM}[{timestamp}]{RESET} {info['bright']}{info['name']}{RESET} {BOLD}{WHITE}{name}{RESET}")

    return entries


def full_draw(snapshot, counts, total_caught, mtime, log_lines, newly_obtained=None):
    content = build_display(snapshot, counts, total_caught, mtime, newly_obtained)
    if log_lines:
        content += f"\n\n  {BOLD}{WHITE}NEW CATCHES{RESET}\n"
        for line in log_lines:
            content += line + "\n"

    frame = f"\033[?25l\033[H\033[2J\033[3J{content}\033[?25h"
    sys.stdout.write(frame)
    sys.stdout.flush()


# --- main ---

def main():
    config = load_config()
    save_path = resolve_save_path(config)
    poll_interval = config.get("poll_interval", 2)

    setup_terminal(config)

    if not os.path.exists(save_path):
        print(f"save file not found: {save_path}")
        sys.exit(1)

    save_data = None
    while save_data is None:
        save_data = safe_read_save(save_path)
        if save_data is None:
            print("save file busy, retrying...")
            time.sleep(2)

    prev_snapshot, prev_counts = extract_journal(save_data)
    total_caught = save_data.get("fish_caught", 0)
    prev_mtime = os.path.getmtime(save_path)
    log_lines = []

    full_draw(prev_snapshot, prev_counts, total_caught, prev_mtime, log_lines)

    try:
        while True:
            time.sleep(poll_interval)

            try:
                current_mtime = os.path.getmtime(save_path)
            except OSError:
                continue

            if current_mtime == prev_mtime:
                continue

            save_data = safe_read_save(save_path)
            if save_data is None:
                continue

            prev_mtime = current_mtime
            new_snapshot, new_counts = extract_journal(save_data)
            total_caught = save_data.get("fish_caught", 0)

            newly_obtained = {}
            for key, new_qualities in new_snapshot.items():
                old_qualities = prev_snapshot.get(key, set())
                fresh = new_qualities - old_qualities
                if fresh:
                    newly_obtained[key] = fresh
                    location, fish_id = key
                    log_lines.extend(format_new_log(fish_id, location, fresh))

            full_draw(new_snapshot, new_counts, total_caught, prev_mtime, log_lines, newly_obtained or None)
            prev_snapshot = new_snapshot
            prev_counts = new_counts

    except KeyboardInterrupt:
        print(f"\n{RESET}stopped")


if __name__ == "__main__":
    main()
