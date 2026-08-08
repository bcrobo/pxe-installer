import logging
from pathlib import Path

from shell import package_installed, run, run_output
from tasks.task import Task

logger = logging.getLogger(__name__)

PVE_REPO = """Types: deb
URIs: http://download.proxmox.com/debian/pve
Suites: trixie
Components: pve-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
"""

PVE_KEY_URL = "https://enterprise.proxmox.com/debian/proxmox-archive-keyring-trixie.gpg"
PVE_KEY_SHA256 = "136673be77aba35dcce385b28737689ad64fd785a797e57897589aed08db6e45"


class AptFullUpgrade(Task):
    name = "Run apt full-upgrade before Proxmox install"

    def check(self):
        output = run_output(["apt", "list", "--upgradable"])
        if output is None:
            return False
        lines = [line for line in output.splitlines() if line and not line.startswith("Listing")]
        return len(lines) == 0

    def execute(self):
        return run(["apt", "update"]) and run(["apt", "full-upgrade", "--yes"])


class AddPveRepository(Task):
    name = "Add Proxmox VE apt repository"

    def check(self):
        repo = Path("/etc/apt/sources.list.d/pve-install-repo.sources")
        keyring = Path("/usr/share/keyrings/proxmox-archive-keyring.gpg")
        if not repo.is_file() or not keyring.is_file():
            return False
        digest = run_output(["sha256sum", str(keyring)])
        return digest is not None and digest.split()[0] == PVE_KEY_SHA256

    def execute(self):
        if not run(
            [
                "wget",
                PVE_KEY_URL,
                "-O",
                "/usr/share/keyrings/proxmox-archive-keyring.gpg",
            ]
        ):
            return False
        Path("/etc/apt/sources.list.d/pve-install-repo.sources").write_text(
            PVE_REPO,
            encoding="utf-8",
        )
        return run(["apt", "update"])


class InstallPveKernel(Task):
    name = "Install Proxmox VE kernel"

    def check(self):
        return package_installed("proxmox-default-kernel")

    def execute(self):
        return run(["apt", "install", "--yes", "proxmox-default-kernel"])


class InstallProxmoxVe(Task):
    name = "Install Proxmox VE packages"

    def check(self):
        required = ("proxmox-ve", "postfix", "open-iscsi", "chrony")
        return all(package_installed(pkg) for pkg in required)

    def execute(self):
        release = run_output(["uname", "-r"]) or ""
        if "pve" not in release:
            logger.error(
                "Reboot into proxmox-default-kernel, then run install.py --pxe-install again"
            )
            return False
        return run(
            [
                "apt",
                "install",
                "--yes",
                "proxmox-ve",
                "postfix",
                "open-iscsi",
                "chrony",
            ]
        )


class RemoveDebianKernel(Task):
    name = "Remove Debian default kernel"

    def check(self):
        return not package_installed("linux-image-amd64")

    def execute(self):
        return (
            run(
                [
                    "apt",
                    "remove",
                    "--yes",
                    "linux-image-amd64",
                    "linux-image-6.12*",
                ],
                check=False,
            )
            and run(["update-grub"])
        )


class RemoveOsProber(Task):
    name = "Remove os-prober"

    def check(self):
        return not package_installed("os-prober")

    def execute(self):
        return run(["apt", "remove", "--yes", "os-prober"], check=False)
