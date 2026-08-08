from config import InstallConfig
from shell import exists, run
from tasks.task import Task


class PartitionDisk(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Partition disks for UEFI, boot pool, and LUKS"

    def check(self):
        for disk in self.config.disks:
            if not all(exists(["sgdisk", "-i", str(i), disk]) for i in (1, 2, 3)):
                return False
        return True

    def execute(self):
        ok = True
        for disk in self.config.disks:
            ok = (
                run(
                    [
                        "sgdisk",
                        "-n",
                        "1:1M:+512M",
                        "-t",
                        "1:EF00",
                        "-c",
                        "1:EFI",
                        disk,
                    ]
                )
                and run(
                    [
                        "sgdisk",
                        "-n",
                        "2:0:+1G",
                        "-t",
                        "2:BF01",
                        "-c",
                        "2:BOOT",
                        disk,
                    ]
                )
                and run(
                    [
                        "sgdisk",
                        "-n",
                        "3:0:0",
                        "-t",
                        "3:8309",
                        "-c",
                        "3:LUKS",
                        disk,
                    ]
                )
                and run(["partprobe", disk])
                and ok
            )
        return ok
