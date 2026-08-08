from config import InstallConfig
from shell import run, run_output
from tasks.task import Task


class UnmountAndExport(Task):
    def __init__(self, config: InstallConfig, reboot: bool = True):
        self.config = config
        self.reboot = reboot
        self.name = "Unmount filesystems and export ZFS pools"

    def check(self):
        return run_output(["zpool", "list", "rpool"]) is None

    def execute(self):
        root = self.config.root_mount
        ok = run(
            [
                "bash",
                "-c",
                f"mount | grep -v zfs | tac | awk '/{root}/ {{print $3}}' | xargs -r -I{{}} umount -lf {{}}",
            ]
        )
        ok = run(["zpool", "export", "-a"]) and ok
        if self.reboot:
            ok = run(["reboot"]) and ok
        return ok
