from pathlib import Path

from config import InstallConfig
from shell import chroot_run, run_output
from tasks.task import Task


class ChrootPackages(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Install base packages in the target system"

    def _package_installed(self, package: str) -> bool:
        status = run_output(
            [
                "chroot",
                self.config.root_mount,
                "dpkg-query",
                "-W",
                "-f=${Status}",
                package,
            ]
        )
        return status == "install ok installed"

    def check(self):
        required = [
            "zfs-initramfs",
            "cryptsetup-initramfs",
            "grub-efi-amd64",
            "shim-signed",
            "openssh-server",
        ]
        return all(self._package_installed(pkg) for pkg in required)

    def execute(self):
        packages = [
            "console-setup",
            "locales",
            "dpkg-dev",
            "linux-headers-generic",
            "linux-image-generic",
            "zfs-initramfs",
            "cryptsetup",
            "cryptsetup-initramfs",
            "systemd-timesyncd",
            "grub-efi-amd64",
            "shim-signed",
            "openssh-server",
            *self.config.firmware_packages,
        ]
        return (
            chroot_run(self.config.root_mount, "apt", "update")
            and chroot_run(
                self.config.root_mount,
                "apt",
                "install",
                "--yes",
                *packages,
            )
            and chroot_run(
                self.config.root_mount,
                "bash",
                "-c",
                "grep -q 'en_US.UTF-8 UTF-8' /etc/locale.gen || echo 'en_US.UTF-8 UTF-8' >> /etc/locale.gen; locale-gen",
            )
        )
