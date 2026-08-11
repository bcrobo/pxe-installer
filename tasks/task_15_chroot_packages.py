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
        
        root = self.config.root_mount
        noninteractive = {"DEBIAN_FRONTEND": "noninteractive"}
        
        return (
            chroot_run(
                root,
                "apt",
                "update",
            )
            and chroot_run(
                root,
                "bash",
                "-c",
                """
                printf '%s\\n' \
                    'keyboard-configuration keyboard-configuration/modelcode string pc105' \
                    'keyboard-configuration keyboard-configuration/layoutcode string fr' \
                    'keyboard-configuration keyboard-configuration/variantcode string' \
                    'keyboard-configuration keyboard-configuration/optionscode string' \
                    | debconf-set-selections
                """,
                env=noninteractive,
            )
            and chroot_run(
                root,
                "apt",
                "install",
                "--yes",
                *packages,
                env=noninteractive,
            )
            and chroot_run(
                root,
                "bash",
                "-c",
                """
                printf '%s\\n' 'en_US.UTF-8 UTF-8' > /etc/locale.gen
                locale-gen
                update-locale LANG=en_US.UTF-8
                """,
                env=noninteractive,
            )
        )
