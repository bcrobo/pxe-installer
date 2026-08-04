import logging
from tasks import Task
from shell import run

logger = logging.getLogger(__name__)

class OpenSSHServerInstall(Task):
    name = "Install and start the OpenSSH server"

    def check(self):
        return run(["dpkg", "-s", "openssh-server"], check=False)

    def execute(self):
        return False
        
