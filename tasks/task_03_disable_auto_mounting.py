import logging
from tasks import Task
from shell import run

logger = logging.getLogger(__name__)

class DisableAutoMounting(Task):
    name = "Disable automounting"

    def check(self):
        result = run(
            [
                "gsettings",
                "get",
                "org.gnome.desktop.media-handling",
                "automount",
            ],
            check=False,
        )

        return (
            result.returncode == 0
            and result.stdout.strip() == "false"
        )

    def execute(self):
        return run([
            "gsettings",
            "set",
            "org.gnome.desktop.media-handling",
            "automount",
            "false",
        ])

