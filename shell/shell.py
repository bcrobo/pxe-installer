import logging
import subprocess
from subprocess import CalledProcessError

logger = logging.getLogger(__name__)

def run(cmd, check=True):
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
    )

    if check and result.returncode != 0:
        logger.error("Command failed: %s", " ".join(cmd))
        if result.stderr:
            logger.error(result.stderr.strip())

    return result

def chroot_run(root, *args, env=None):
    cmd = ["chroot", root]

    if env:
        env_args = [f"{k}={v}" for k, v in env.items()]
        cmd.extend(["/usr/bin/env", *env_args])

    cmd.extend(args)
    return run(cmd)
