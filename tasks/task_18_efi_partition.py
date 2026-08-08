import os
from pathlib import Path

from config import InstallConfig
from shell import run, run_output
from tasks.task import Task


class SetupEfiPartition(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Format and mount the EFI system partition"

    def check(self):
        fstab = Path(self.config.root_mount, "etc/fstab")
        efi_mount = Path(self.config.root_mount, "boot/efi")
        return (
            fstab.is_file()
            and "boot/efi" in fstab.read_text(encoding="utf-8")
            and os.path.ismount(efi_mount)
        )

    def execute(self):
        root = self.config.root_mount
        efi_partition = self.config.efi_partition()
        uuid = run_output(["blkid", "-s", "UUID", "-o", "value", efi_partition])
        if not uuid:
            if not run(["mkdosfs", "-F", "32", "-s", "1", "-n", "EFI", efi_partition]):
                return False
            uuid = run_output(["blkid", "-s", "UUID", "-o", "value", efi_partition])
            if not uuid:
                return False
        return (
            run(["mkdir", "-p", f"{root}/boot/efi"])
            and run(["mount", efi_partition, f"{root}/boot/efi"])
            and self._ensure_fstab(uuid)
        )

    def _ensure_fstab(self, uuid: str) -> bool:
        fstab_path = Path(self.config.root_mount, "etc/fstab")
        entry = f"UUID={uuid} /boot/efi vfat defaults 0 0\n"
        text = fstab_path.read_text(encoding="utf-8") if fstab_path.is_file() else ""
        if entry.strip() not in text:
            fstab_path.write_text(text + entry, encoding="utf-8")
        return True
