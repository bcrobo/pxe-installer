from config import InstallConfig
from shell import exists, run
from tasks.task import Task


class CreateRootPool(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Create mirrored ZFS root pool on LUKS"

    def check(self):
        return exists(["zpool", "list", "rpool"])

    def execute(self):
        luks_devices = [
            self.config.luks_mapper_path(index)
            for index in range(1, len(self.config.disks) + 1)
        ]
        cmd = [
            "zpool",
            "create",
            "-o",
            "ashift=12",
            "-o",
            "autotrim=on",
            "-O",
            "acltype=posixacl",
            "-O",
            "xattr=sa",
            "-O",
            "dnodesize=auto",
            "-O",
            "compression=lz4",
            "-O",
            "normalization=formD",
            "-O",
            "relatime=on",
            "-O",
            "canmount=off",
            "-O",
            "mountpoint=/",
            "-R",
            self.config.root_mount,
            "rpool",
        ]
        if len(luks_devices) > 1:
            cmd.extend(["mirror", *luks_devices])
        else:
            cmd.extend(luks_devices)
        return run(cmd)
