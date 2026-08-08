from pathlib import Path

from config import InstallConfig
from shell import chroot_run, run
from tasks.task import Task


class ZfsListCache(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Generate ZFS mount generator cache"

    def check(self):
        bpool_cache = Path(self.config.root_mount, "etc/zfs/zfs-list.cache/bpool")
        rpool_cache = Path(self.config.root_mount, "etc/zfs/zfs-list.cache/rpool")
        return (
            bpool_cache.is_file()
            and rpool_cache.is_file()
            and bpool_cache.read_text(encoding="utf-8").strip()
            and rpool_cache.read_text(encoding="utf-8").strip()
        )

    def execute(self):
        root = self.config.root_mount
        cache_dir = Path(root, "etc/zfs/zfs-list.cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "bpool").touch()
        (cache_dir / "rpool").touch()
        return (
            chroot_run(root, "zfs", "set", "canmount=on", self.config.boot_dataset)
            and chroot_run(root, "zfs", "set", "canmount=noauto", self.config.root_dataset)
            and chroot_run(
                root,
                "bash",
                "-c",
                "zed -F & sleep 2; kill %1",
            )
            and run(
                [
                    "sed",
                    "-Ei",
                    f"s|{root}/?|/|",
                    f"{root}/etc/zfs/zfs-list.cache/bpool",
                    f"{root}/etc/zfs/zfs-list.cache/rpool",
                ]
            )
        )
