"""Print a privacy-safe inventory for reproducible local benchmarks."""

import json
import os
import platform
import re
import shutil
import subprocess
from typing import TypedDict


class HardwareInfo(TypedDict):
    os: str
    architecture: str
    chip: str
    cpu_cores: int | None
    memory_gb: float | None
    apple_silicon: bool
    disk_free_gb: float


def _sysctl(name: str) -> str | None:
    try:
        result = subprocess.run(
            ["sysctl", "-n", name],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def _mac_profile() -> dict[str, object]:
    if platform.system() != "Darwin":
        return {}
    try:
        result = subprocess.run(
            ["system_profiler", "SPHardwareDataType", "-json"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        hardware = payload.get("SPHardwareDataType", [])
        if isinstance(hardware, list) and hardware and isinstance(hardware[0], dict):
            return dict(hardware[0])
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError):
        pass
    return {}


def _memory_gb(sysctl_memory: str | None, profile: dict[str, object]) -> float | None:
    if sysctl_memory:
        return round(int(sysctl_memory) / 1_000_000_000, 1)
    physical = profile.get("physical_memory")
    if isinstance(physical, str):
        match = re.search(r"([0-9.]+)\s*GB", physical, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def inspect_hardware() -> HardwareInfo:
    """Collect only benchmark-relevant fields, excluding device identifiers."""

    architecture = platform.machine()
    profile = _mac_profile()
    profile_chip = profile.get("chip_type")
    chip = (
        _sysctl("machdep.cpu.brand_string")
        or (profile_chip if isinstance(profile_chip, str) else None)
        or platform.processor()
        or "unknown"
    )
    memory = _sysctl("hw.memsize")
    disk = shutil.disk_usage(".")
    return {
        "os": f"{platform.system()} {platform.mac_ver()[0]}",
        "architecture": architecture,
        "chip": chip,
        "cpu_cores": os.cpu_count(),
        "memory_gb": _memory_gb(memory, profile),
        "apple_silicon": platform.system() == "Darwin" and architecture == "arm64",
        "disk_free_gb": round(disk.free / 1_000_000_000, 1),
    }


def main() -> None:
    print(json.dumps(inspect_hardware(), indent=2))


if __name__ == "__main__":
    main()
