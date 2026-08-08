from shell import run

class WipeDisk(Task):

    def __init__(self, disk):
        self.disk = disk
        self.name = f"Wipe {disk} signatures"

    def check(self):
        return False  # always considered incomplete until partitioning succeeds

    def execute(self):
        return (
            run(["wipefs", "-a", self.disk])
            and run(["sgdisk", "--zap-all", self.disk])
        )
