from pathlib import Path

from config import InstallConfig, detect_interface
from shell import run, run_output
from tasks.task import Task


class MirrorGrubEfi(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Mirror EFI partitions and boot entries"

    def check(self):
        if len(self.config.disks) < 2:
            return True
        entries = run_output(["efibootmgr"]) or ""
        for index in range(2, len(self.config.disks) + 1):
            if f"debian-{index}" not in entries:
                return False
        return True

    def execute(self):
        if len(self.config.disks) < 2:
            return True
        primary_efi = self.config.efi_partition(self.config.primary_disk)
        ok = run(["umount", "/boot/efi"], check=False)
        for index, disk in enumerate(self.config.disks[1:], start=2):
            target_efi = self.config.efi_partition(disk)
            ok = (
                run(["dd", f"if={primary_efi}", f"of={target_efi}", "bs=1M"])
                and run(
                    [
                        "efibootmgr",
                        "-c",
                        "-g",
                        "-d",
                        disk,
                        "-p",
                        "1",
                        "-L",
                        f"debian-{index}",
                        "-l",
                        r"\EFI\debian\grubx64.efi",
                    ]
                )
                and ok
            )
        return run(["mount", "/boot/efi"]) and ok


class ConfigureProxmoxHosts(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Configure /etc/hosts for Proxmox"

    def check(self):
        hosts = Path("/etc/hosts").read_text(encoding="utf-8")
        ip = self._target_ip()
        if not ip:
            return False
        return f"{ip}   {self.config.fqdn} {self.config.hostname}" in hosts

    def execute(self):
        ip = self._target_ip()
        if not ip:
            return False
        hosts_path = Path("/etc/hosts")
        lines = []
        for line in hosts_path.read_text(encoding="utf-8").splitlines():
            if self.config.hostname in line and line.strip().startswith("127.0.1.1"):
                continue
            lines.append(line)
        lines.append(f"{ip}   {self.config.fqdn} {self.config.hostname}")
        hosts_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        current = run_output(["hostname", "--ip-address"])
        return current is not None and ip in current.split()

    def _target_ip(self) -> str | None:
        if self.config.network.mode == "static" and self.config.network.address:
            return self.config.network.address
        interface = self.config.network.interface or detect_interface()
        if not interface:
            return None
        output = run_output(["ip", "-4", "-o", "addr", "show", interface, "scope", "global"])
        if not output:
            return None
        parts = output.split()
        if len(parts) < 4:
            return None
        return parts[3].split("/")[0]


class DistUpgrade(Task):
    name = "Upgrade installed system"

    def check(self):
        output = run_output(["apt", "list", "--upgradable"])
        if output is None:
            return False
        lines = [line for line in output.splitlines() if line and not line.startswith("Listing")]
        return len(lines) == 0

    def execute(self):
        return run(["apt", "update"]) and run(["apt", "dist-upgrade", "--yes"])
