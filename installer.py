import logging
import os
import sys

from logging_config import configure
from tasks import UpdateRepo, OpenSSHServerInstall

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    configure(logging.DEBUG)
    if os.geteuid() != 0:
        logger.error("Please run this installer as root.")
        sys.exit(1)

    tasks = [
        #UpdateRepo(),
        OpenSSHServerInstall()
    ]

    for task in tasks:
        logger.info(f"[Task: {task.name}]")
        if task.check():
            logger.info(f"[Task: {task.name} ✓]")
            continue

        if not task.execute():
            logger.error(f"[Task: {task.name} ×]")
            break

