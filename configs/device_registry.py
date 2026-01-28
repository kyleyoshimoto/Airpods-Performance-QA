from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass(frozen=True)
class DeviceConfig:
    key: str
    display_name: str
    bluetooth_address: str

def load_device_registry(path: str | Path = "configs/devices.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Device registry not found: {p}")
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def get_device(device_key: str | None = None, path: str | Path = "configs/devices.yaml") -> DeviceConfig:
    data = load_device_registry(path)
    devices = data.get("devices", {})

    if device_key is None:
        device_key = data.get("default_device")

    if not device_key or device_key not in devices:
        raise KeyError(f"Unknown device '{device_key}'. Available: {list(devices.keys())}")

    d = devices[device_key]
    return DeviceConfig(
        key=device_key,
        display_name=str(d["display_name"]),
        bluetooth_address=str(d["bluetooth_address"]),
    )