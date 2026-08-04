import logging
from tasks import Task
from shell import run, exists

logger = logging.getLogger(__name__)

class OpenSSHServerInstall(Task):
    name = "Install and start the OpenSSH server"

    def check(self):
        return (
            exists(["dpkg", "-s", "openssh-server"])
            and exists(["systemctl", "is-enabled", "ssh"])
            and exists(["systemctl", "is-active", "ssh"])
            )

    def execute(self):
        return (
            run(["apt", "install", "-y", "openssh-server"])
            and run(["systemctl", "restart", "ssh"])
        )
