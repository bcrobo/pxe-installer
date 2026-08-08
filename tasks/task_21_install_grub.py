from config import InstallConfig
from shell import chroot_run
from tasks.task import Task


class InstallGrub(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Install GRUB to the primary EFI partition"

    def check(self):
        return chroot_run(
            self.config.root_mount,
            "test",
            "-f",
            "/boot/efi/EFI/debian/grubx64.efi",
        )

    def execute(self):
        root = self.config.root_mount
        return (
            chroot_run(root, "grub-probe", "/boot")
            and chroot_run(root, "update-grub")
            and chroot_run(
                root,
                "grub-install",
                "--target=x86_64-efi",
                "--efi-directory=/boot/efi",
                "--bootloader-id=debian",
                "--recheck",
            )
        )
