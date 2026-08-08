from pathlib import Path

from config import InstallConfig
from shell import run
from tasks.task import Task


class Debootstrap(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Debootstrap Debian into the root dataset"

    def check(self):
        return Path(self.config.root_mount, "etc/debian_version").is_file()

    def execute(self):
        return run(
            [
                "debootstrap",
                self.config.debian_suite,
                self.config.root_mount,
            ]
        )
