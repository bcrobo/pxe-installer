import logging
from tasks import Task
from shell import run, package_installed

logger = logging.getLogger(__name__)

class ZfsPrerequisitesInstall(Task):
    name = "Install zfs in the LiveCD environment"
    packages = [
        "linux-headers-generic",
        "debootstrap",
        "gdisk",
        "zfsutils-linux",
    ]

    def check(self):
        return all(
            package_installed(package)
            for package in self.packages
        )

    def execute(self):
        # Install missing prerequisites in zfsutils-linux package
        # See: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1091428
        return run([
            "apt",
            "install",
            "--yes",
            *self.packages,
        ])

