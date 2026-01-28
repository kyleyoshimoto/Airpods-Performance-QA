from __future__ import annotations

import subprocess
import time


class BluetoothController:
    """
    Manual Bluetooth controller (macOS) that determines connection state by parsing:

        system_profiler SPBluetoothDataType

    Newer macOS versions do NOT emit per-device "Connected: Yes/No". Instead, devices appear under
    "Connected:" and "Not Connected:" sections. This controller parses those sections and matches
    the device by name.

    Connect/disconnect actions are MANUAL (user clicks Connect/Disconnect in the Bluetooth menu),
    and this controller waits (with a universal timeout) until the target state is reached.
    """

    def __init__(self, device_name: str, device_address: str, timeout_sec: int = 30):
        self.device_name = device_name
        self.device_address = device_address
        self.timeout_sec = timeout_sec

        # Normalize smart quotes to avoid mismatches like:
        # "Kyle’s AirPods Pro" (U+2019) vs "Kyle's AirPods Pro" (ASCII)
        self.device_name_normalized = self._normalize_quotes(device_name)

    def _normalize_quotes(self, s: str) -> str:
        return s.replace("’", "'").replace("‘", "'")

    def _get_bluetooth_profile_text(self) -> str:
        try:
            return subprocess.check_output(
                ["system_profiler", "SPBluetoothDataType"],
                text=True,
            )
        except subprocess.CalledProcessError:
            return ""
        
    import subprocess

    def has_blueutil(self) -> bool:
        try:
            subprocess.run(
                ["blueutil", "--version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("✅ 'blueutil' is installed. Test will proceed automatically.")
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("⚠️ 'blueutil' is not installed or not found in PATH. Test will proceed manually.Please install it via Homebrew: 'brew install blueutil'")
            return False

    def is_connected(self) -> bool:
        """
        Returns True if the device appears under the 'Connected:' section, False if it appears
        under 'Not Connected:' section, otherwise False.
        """
        output = self._get_bluetooth_profile_text()
        if not output:
            return False

        in_connected = False
        in_not_connected = False

        for raw_line in output.splitlines():
            line = raw_line.strip()
            norm_line = self._normalize_quotes(line)

            # Section transitions
            if norm_line == "Connected:":
                in_connected = True
                in_not_connected = False
                continue
            if norm_line == "Not Connected:":
                in_connected = False
                in_not_connected = True
                continue

            # Device entries look like "Kyle’s AirPods Pro:" (ending with :)
            # Only treat a match as a device header line if it ends with ":".
            if norm_line.endswith(":"):
                # strip the trailing ":" for comparison
                device_header = norm_line[:-1].strip()
                if device_header == self.device_name_normalized:
                    if in_connected:
                        return True
                    if in_not_connected:
                        return False

        return False

    def _wait_for_state(self, target_state: bool) -> None:
        poll_interval = 0.5
        deadline = time.time() + self.timeout_sec

        while time.time() < deadline:
            if self.is_connected() == target_state:
                return
            time.sleep(poll_interval)

        state_str = "connected" if target_state else "disconnected"
        raise TimeoutError(
            f"Timeout waiting for '{self.device_name}' to be {state_str}."
        )

    def connect(self) -> None:
        if self.is_connected():
            print(f"✅ Already connected: '{self.device_name}'")
            return
        if self.has_blueutil():
            subprocess.run(["blueutil", "--connect", self.device_address], check=False) 

        print(f"Please connect to '{self.device_name}' manually (Bluetooth menu).")
        self._wait_for_state(True)
        print(f"✅ Connected: '{self.device_name}'")

    def disconnect(self) -> None:
        if not self.is_connected():
            print(f"✅ Already disconnected: '{self.device_name}'")
            return
        if self.has_blueutil():
            subprocess.run(["blueutil", "--disconnect", self.device_address], check=False)
        print(f"Please disconnect '{self.device_name}' manually (Bluetooth menu).")
        self._wait_for_state(False)
        print(f"✅ Disconnected: '{self.device_name}'")