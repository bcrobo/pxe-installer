import logging
import subprocess

logger = logging.getLogger(__name__)


def run(cmd, check=True, input_text=None):
    result = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        input=input_text,
    )

    if check and result.returncode != 0:
        logger.error("Command failed: %s", " ".join(map(str, cmd)))
        if result.stdout:
            logger.error(result.stdout.strip())
        if result.stderr:
            logger.error(result.stderr.strip())

    return result.returncode == 0


def run_output(cmd):
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def exists(cmd):
    return subprocess.run(cmd, text=True, capture_output=True).returncode == 0


def package_installed(package):
    result = subprocess.run(
        ["dpkg-query", "-W", "-f=${Status}", package],
        text=True,
        capture_output=True,
    )
    return (
        result.returncode == 0
        and result.stdout.startswith("install ok installed")
    )


def chroot_run(root, *args, env=None):
    cmd = ["chroot", root]
    if env:
        env_args = [f"{k}={v}" for k, v in env.items()]
        cmd.extend(["/usr/bin/env", *env_args])
    cmd.extend(args)
    return run(cmd)
