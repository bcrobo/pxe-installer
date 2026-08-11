from shell import package_installed, run
from tasks.task import Task


class ZfsPrerequisitesInstall(Task):
    name = "Install ZFS prerequisites in the live environment"
    packages = [
        "linux-headers-generic",
        "debootstrap",
        "gdisk",
        "zfsutils-linux",
        "cryptsetup",
        "dosfstools",
    ]

    def check(self):
        return all(package_installed(package) for package in self.packages)

    def execute(self):
        return run(["env", "DEBIAN_FRONTEND=noninteractive", "apt", "install", "--yes", *self.packages])
