import logging
from pathlib import Path

from config import InstallConfig
from shell import run
from tasks.task import Task

logger = logging.getLogger(__name__)


class UpdateRepo(Task):
    name = "Setup and update repositories"

    def check(self):
        text = Path("/etc/apt/sources.list").read_text(encoding="utf-8")
        return "main contrib non-free-firmware" in text and run(["apt", "update"])

    def execute(self):
        path = Path("/etc/apt/sources.list")
        text = path.read_text(encoding="utf-8")
        if "main contrib non-free-firmware" not in text:
            text = text.replace(
                "main non-free-firmware",
                "main contrib non-free-firmware",
            )
            path.write_text(text, encoding="utf-8")
        return run(["apt", "update"])
