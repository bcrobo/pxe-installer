import logging
from tasks import Task
from shell import run

logger = logging.getLogger(__name__)

class LiveCDZfsInstall(Task):
    name = "Install zfs in the LiveCD environment"

    def execute(self):
        # Install missing prerequisites in zfsutils-linux package
        # See: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1091428
        ok = run(["apt", "install", "--yes", "linux-headers-generic"])
        if not ok:
            return ok

        return run(["apt", "install", "--yes", "debootstrap", "gdisk", "zfsutils-linux"])
        
