from pathlib import Path

from config import InstallConfig
from shell import chroot_run
from tasks.task import Task

ZFS_IMPORT_BPOOL_SERVICE = """[Unit]
DefaultDependencies=no
Before=zfs-import-scan.service
Before=zfs-import-cache.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/zpool import -N -o cachefile=none bpool
ExecStartPre=-/bin/mv /etc/zfs/zpool.cache /etc/zfs/preboot_zpool.cache
ExecStartPost=-/bin/mv /etc/zfs/preboot_zpool.cache /etc/zfs/zpool.cache

[Install]
WantedBy=zfs-import.target
"""


class EnableBpoolImport(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Enable automatic bpool import at boot"

    def check(self):
        service = Path(
            self.config.root_mount,
            "etc/systemd/system/zfs-import-bpool.service",
        )
        return service.is_file() and "zpool import -N -o cachefile=none bpool" in service.read_text(
            encoding="utf-8"
        )

    def execute(self):
        service_path = Path(
            self.config.root_mount,
            "etc/systemd/system/zfs-import-bpool.service",
        )
        service_path.write_text(ZFS_IMPORT_BPOOL_SERVICE, encoding="utf-8")
        return chroot_run(
            self.config.root_mount,
            "systemctl",
            "enable",
            "zfs-import-bpool.service",
        )
