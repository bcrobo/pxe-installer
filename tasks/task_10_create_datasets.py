from config import InstallConfig
from shell import exists, run
from tasks.task import Task


class CreateDatasets(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Create minimal ZFS datasets"

    def check(self):
        return exists(["zfs", "list", self.config.root_dataset])

    def execute(self):
        commands = [
            ["zfs", "create", "-o", "canmount=off", "-o", "mountpoint=none", "rpool/ROOT"],
            ["zfs", "create", "-o", "canmount=off", "-o", "mountpoint=none", "bpool/BOOT"],
            [
                "zfs",
                "create",
                "-o",
                "canmount=noauto",
                "-o",
                "mountpoint=/",
                self.config.root_dataset,
            ],
            ["zfs", "mount", self.config.root_dataset],
            [
                "zfs",
                "create",
                "-o",
                "mountpoint=/boot",
                self.config.boot_dataset,
            ],
            ["zfs", "create", "-o", "canmount=off", "rpool/var"],
            ["zfs", "create", "rpool/var/log"],
        ]
        ok = True
        for command in commands:
            ok = run(command) and ok
        return ok
