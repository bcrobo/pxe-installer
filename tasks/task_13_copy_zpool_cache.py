from pathlib import Path

from config import InstallConfig
from shell import run
from tasks.task import Task


class CopyZpoolCache(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Copy zpool.cache into the target system"

    def check(self):
        return Path(self.config.root_mount, "etc/zfs/zpool.cache").is_file()

    def execute(self):
        root = self.config.root_mount
        return (
            run(["mkdir", "-p", f"{root}/etc/zfs"])
            and run(["cp", "/etc/zfs/zpool.cache", f"{root}/etc/zfs/zpool.cache"])
        )
