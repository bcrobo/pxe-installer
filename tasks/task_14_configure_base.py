from pathlib import Path

from config import InstallConfig, detect_interface
from shell import run
from tasks.task import Task


class ConfigureBaseSystem(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Configure hostname, hosts, network, and apt sources"

    def check(self):
        hostname_path = Path(self.config.root_mount, "etc/hostname")
        sources_path = Path(self.config.root_mount, "etc/apt/sources.list")
        return hostname_path.read_text(encoding="utf-8").strip() == self.config.hostname and sources_path.is_file()

    def execute(self):
        root = self.config.root_mount
        interface = self.config.network.interface or detect_interface() or "enp5s0"
        hosts_lines = [
            "127.0.0.1       localhost",
            f"127.0.1.1       {self.config.fqdn} {self.config.hostname}",
            "",
            "::1             localhost ip6-localhost ip6-loopback",
            "ff02::1         ip6-allnodes",
            "ff02::2         ip6-allrouters",
            "",
        ]
        sources = f"""deb http://deb.debian.org/debian {self.config.debian_suite} main contrib non-free-firmware
deb-src http://deb.debian.org/debian {self.config.debian_suite} main contrib non-free-firmware

deb http://deb.debian.org/debian-security {self.config.debian_suite}-security main contrib non-free-firmware
deb-src http://deb.debian.org/debian-security {self.config.debian_suite}-security main contrib non-free-firmware

deb http://deb.debian.org/debian {self.config.debian_suite}-updates main contrib non-free-firmware
deb-src http://deb.debian.org/debian {self.config.debian_suite}-updates main contrib non-free-firmware
"""
        if self.config.network.mode == "static" and self.config.network.address:
            network = f"""auto {interface}
iface {interface} inet static
    address {self.config.network.address}
    netmask {self.config.network.netmask or "255.255.255.0"}
    gateway {self.config.network.gateway or "192.168.1.254"}
"""
        else:
            network = f"""auto {interface}
iface {interface} inet dhcp
"""
        Path(root, "etc/hostname").write_text(f"{self.config.hostname}\n", encoding="utf-8")
        Path(root, "etc/hosts").write_text("\n".join(hosts_lines), encoding="utf-8")
        Path(root, "etc/apt/sources.list").write_text(sources, encoding="utf-8")
        iface_dir = Path(root, "etc/network/interfaces.d")
        iface_dir.mkdir(parents=True, exist_ok=True)
        Path(iface_dir, interface).write_text(network, encoding="utf-8")
        return (
            run(["mkdir", "-p", f"{root}/dev", f"{root}/proc", f"{root}/sys"])
            and run(["mount", "--make-private", "--rbind", "/dev", f"{root}/dev"])
            and run(["mount", "--make-private", "--rbind", "/proc", f"{root}/proc"])
            and run(["mount", "--make-private", "--rbind", "/sys", f"{root}/sys"])
        )
