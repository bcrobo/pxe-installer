import logging
from tasks import Task
from shell import run

logger = logging.getLogger(__name__)

class DisableAutoMounting(Task):
    name = "Disable automounting"

    def execute(self):
        return run(["gsettings", "set", "org.gnome.desktop.media-handling", "automount", "false"])
        
