import logging
from pathlib import Path
from tasks import Task
from shell import run

logger = logging.getLogger(__name__)

class UpdateRepo(Task):
    name = "Setup and update repositories"

    def check(self):
        text = Path("/etc/apt/sources.list").read_text()
        return "main contrib non-free-firmware" in text

    def execute(self):
        path = Path("/etc/apt/sources.list")
        text = path.read_text()

        if "main contrib non-free-firmware" not in text:
            text = text.replace(
                "main non-free-firmware",
                "main contrib non-free-firmware",
            )
            path.write_text(text)

        return run(["apt", "update"])
