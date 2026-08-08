from pathlib import Path

from config import InstallConfig
from shell import chroot_run, exists
from tasks.task import Task


class SetupDropbear(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Configure Dropbear for remote LUKS unlock"

    def check(self):
        keys = Path(self.config.root_mount, "etc/dropbear/initramfs/authorized_keys")
        return keys.is_file() and keys.read_text(encoding="utf-8").strip()

    def execute(self):
        root = self.config.root_mount
        initramfs_conf = Path(root, "etc/initramfs-tools/initramfs.conf")
        ip_line = self.config.network.initramfs_ip_line(self.config.hostname)
        if ip_line:
            text = initramfs_conf.read_text(encoding="utf-8") if initramfs_conf.is_file() else ""
            if ip_line not in text:
                initramfs_conf.parent.mkdir(parents=True, exist_ok=True)
                initramfs_conf.write_text(text + f"\n{ip_line}\n", encoding="utf-8")

        ok = chroot_run(
            root,
            "apt",
            "install",
            "--yes",
            "--no-install-recommends",
            "dropbear-initramfs",
        )
        dropbear_dir = Path(root, "etc/dropbear/initramfs")
        dropbear_dir.mkdir(parents=True, exist_ok=True)

        if self.config.dropbear.authorized_keys:
            source = Path(self.config.dropbear.authorized_keys).expanduser()
            if source.is_file():
                dropbear_dir.joinpath("authorized_keys").write_text(
                    source.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )

        if self.config.dropbear.convert_openssh_keys:
            for key_type in ("ecdsa", "ed25519", "rsa"):
                script = f"""
if [ -f /etc/ssh/ssh_host_{key_type}_key ]; then
  cp /etc/ssh/ssh_host_{key_type}_key /tmp/openssh.key
  ssh-keygen -p -N '' -m PEM -f /tmp/openssh.key
  dropbearconvert openssh dropbear /tmp/openssh.key /etc/dropbear/initramfs/dropbear_{key_type}_host_key
  rm -f /tmp/openssh.key
fi
"""
                ok = chroot_run(root, "bash", "-c", script) and ok

        return ok and chroot_run(root, "update-initramfs", "-u", "-k", "all")
