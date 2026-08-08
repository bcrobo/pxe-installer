from shell import run, exists

class CreateBootPool(Task):
    name = "Create ZFS boot pool"

    def __init__(self, boot_partition, root_mount="/mnt"):
        self.boot_partition = boot_partition
        self.root_mount = root_mount

    def check(self):
        return exists([
            "zpool",
            "list",
            "bpool",
        ])

    def execute(self):
        return run([
            "zpool",
            "create",
            "-o", "ashift=12",
            "-o", "autotrim=on",
            "-o", "compatibility=grub2",
            "-o", "cachefile=/etc/zfs/zpool.cache",
            "-O", "devices=off",
            "-O", "acltype=posixacl",
            "-O", "xattr=sa",
            "-O", "compression=lz4",
            "-O", "normalization=formD",
            "-O", "relatime=on",
            "-O", "canmount=off",
            "-O", "mountpoint=/boot",
            "-R", self.root_mount,
            "bpool",
            self.boot_partition,
        ])
