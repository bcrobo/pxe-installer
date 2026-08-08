from pathlib import Path

from config import InstallConfig
from shell import run_output
from tasks.task import Task


class SetupCrypttab(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Configure /etc/crypttab for LUKS mirrors"

    def check(self):
        path = Path(self.config.root_mount, "etc/crypttab")
        if not path.is_file():
            return False
        text = path.read_text(encoding="utf-8")
        return all(self.config.luks_mapper(index) in text for index in range(1, len(self.config.disks) + 1))

    def execute(self):
        lines = []
        for index, disk in enumerate(self.config.disks, start=1):
            partition = self.config.luks_partition(disk)
            uuid = run_output(["blkid", "-s", "UUID", "-o", "value", partition])
            if not uuid:
                return False
            mapper = self.config.luks_mapper(index)
            lines.append(
                f"{mapper} /dev/disk/by-uuid/{uuid} none luks,discard,initramfs"
            )
        path = Path(self.config.root_mount, "etc/crypttab")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True
