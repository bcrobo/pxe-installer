from pathlib import Path

from config import InstallConfig
from shell import chroot_run
from tasks.task import Task


class ConfigureGrub(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Configure GRUB for ZFS root"

    def check(self):
        grub = Path(self.config.root_mount, "etc/default/grub")
        if not grub.is_file():
            return False
        text = grub.read_text(encoding="utf-8")
        return f'root=ZFS={self.config.root_dataset}' in text

    def execute(self):
        grub_path = Path(self.config.root_mount, "etc/default/grub")
        text = grub_path.read_text(encoding="utf-8") if grub_path.is_file() else ""
        target = f'GRUB_CMDLINE_LINUX="root=ZFS={self.config.root_dataset}"'
        if "GRUB_CMDLINE_LINUX=" in text:
            lines = []
            for line in text.splitlines():
                if line.startswith("GRUB_CMDLINE_LINUX="):
                    lines.append(target)
                else:
                    lines.append(line)
            text = "\n".join(lines) + "\n"
        else:
            text += f"\n{target}\n"
        grub_path.write_text(text, encoding="utf-8")

        sshd = Path(self.config.root_mount, "etc/ssh/sshd_config")
        if sshd.is_file():
            ssh_text = sshd.read_text(encoding="utf-8")
            if "PermitRootLogin yes" not in ssh_text:
                sshd.write_text(ssh_text.rstrip() + "\nPermitRootLogin yes\n", encoding="utf-8")

        return chroot_run(self.config.root_mount, "update-initramfs", "-c", "-k", "all")
