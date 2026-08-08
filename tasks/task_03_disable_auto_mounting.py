from shell import run_output
from tasks.task import Task


class DisableAutoMounting(Task):
    name = "Disable automounting"

    def check(self):
        value = run_output(
            [
                "gsettings",
                "get",
                "org.gnome.desktop.media-handling",
                "automount",
            ]
        )
        if value is None:
            return True
        return value == "false"

    def execute(self):
        value = run_output(
            [
                "gsettings",
                "get",
                "org.gnome.desktop.media-handling",
                "automount",
            ]
        )
        if value is None:
            return True
        from shell import run

        return run(
            [
                "gsettings",
                "set",
                "org.gnome.desktop.media-handling",
                "automount",
                "false",
            ]
        )
