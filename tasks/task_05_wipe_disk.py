from config import InstallConfig
from shell import exists, run
from tasks.task import Task


class WipeDisk(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Wipe disk signatures"

    def check(self):
        for disk in self.config.disks:
            if not all(exists(["sgdisk", "-i", str(i), disk]) for i in (1, 2, 3)):
                return False
        return True

    def execute(self):
        ok = True
        for disk in self.config.disks:
            ok = (
                run(["swapoff", "--all"], check=False)
                and run(["wipefs", "-a", disk])
                and run(["sgdisk", "--zap-all", disk])
                and ok
            )
        return ok
