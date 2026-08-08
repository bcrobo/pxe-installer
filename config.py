from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class NetworkConfig:
    mode: str = "dhcp"
    interface: str | None = None
    address: str | None = None
    gateway: str | None = None
    netmask: str | None = None

    def initramfs_ip_line(self, hostname: str) -> str | None:
        if self.mode != "static" or not self.address:
            return None
        gateway = self.gateway or ""
        netmask = self.netmask or "255.255.255.0"
        nic = self.interface or ""
        return f"IP={self.address}::{gateway}:{netmask}:{hostname}:{nic}"


@dataclass
class DropbearConfig:
    authorized_keys: str | None = None
    convert_openssh_keys: bool = True


@dataclass
class LuksConfig:
    passphrase_env: str = "LUKS_PASSPHRASE"
    cipher: str = "aes-xts-plain64"
    key_size: int = 512
    hash: str = "sha256"


@dataclass
class InstallConfig:
    disks: list[str] = field(default_factory=list)
    hostname: str = "pve"
    domain: str = "local"
    debian_suite: str = "trixie"
    root_mount: str = "/mnt"
    root_dataset: str = "rpool/ROOT/debian"
    boot_dataset: str = "bpool/BOOT/debian"
    network: NetworkConfig = field(default_factory=NetworkConfig)
    dropbear: DropbearConfig = field(default_factory=DropbearConfig)
    luks: LuksConfig = field(default_factory=LuksConfig)
    firmware_packages: list[str] = field(
        default_factory=lambda: [
            "firmware-linux",
            "firmware-realtek",
            "firmware-mediatek",
        ]
    )

    @property
    def fqdn(self) -> str:
        return f"{self.hostname}.{self.domain}"

    @property
    def primary_disk(self) -> str:
        if not self.disks:
            raise ValueError("At least one disk must be configured")
        return self.disks[0]

    def efi_partition(self, disk: str | None = None) -> str:
        return f"{disk or self.primary_disk}-part1"

    def boot_partition(self, disk: str | None = None) -> str:
        return f"{disk or self.primary_disk}-part2"

    def luks_partition(self, disk: str | None = None) -> str:
        return f"{disk or self.primary_disk}-part3"

    def luks_mapper(self, index: int) -> str:
        return f"luks{index}"

    def luks_mapper_path(self, index: int) -> str:
        return f"/dev/mapper/{self.luks_mapper(index)}"

    def luks_passphrase(self) -> str:
        env_name = self.luks.passphrase_env
        value = os.environ.get(env_name)
        if not value:
            raise RuntimeError(
                f"Set {env_name} with the LUKS passphrase before running pre-install"
            )
        return value

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> InstallConfig:
        network = NetworkConfig(**data.get("network", {}))
        dropbear = DropbearConfig(**data.get("dropbear", {}))
        luks = LuksConfig(**data.get("luks", {}))
        known = {
            "disks",
            "hostname",
            "domain",
            "debian_suite",
            "root_mount",
            "root_dataset",
            "boot_dataset",
            "firmware_packages",
        }
        return cls(
            **{k: v for k, v in data.items() if k in known},
            network=network,
            dropbear=dropbear,
            luks=luks,
        )

    @classmethod
    def from_file(cls, path: str | Path) -> InstallConfig:
        with open(path, encoding="utf-8") as handle:
            return cls.from_dict(yaml.safe_load(handle) or {})


def detect_interface() -> str | None:
    output = Path("/proc/net/dev").read_text(encoding="utf-8").splitlines()[2:]
    for line in output:
        name = line.split(":", 1)[0].strip()
        if name and name != "lo":
            return name
    return None
