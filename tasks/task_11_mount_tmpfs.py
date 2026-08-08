from pathlib import Path

from config import InstallConfig
from shell import run
from tasks.task import Task


class MountTmpfsRun(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Mount tmpfs for /run"

    def check(self):
        return Path(self.config.root_mount, "run/lock").is_dir()

    def execute(self):
        root = self.config.root_mount
        return (
            run(["mkdir", "-p", f"{root}/run"])
            and run(["mount", "-t", "tmpfs", "tmpfs", f"{root}/run"])
            and run(["mkdir", "-p", f"{root}/run/lock"])
        )
