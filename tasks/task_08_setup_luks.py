from config import InstallConfig
from shell import exists, run
from tasks.task import Task


class SetupLuks(Task):
    def __init__(self, config: InstallConfig):
        self.config = config
        self.name = "Create and open LUKS volumes"

    def check(self):
        for index in range(1, len(self.config.disks) + 1):
            if not exists(["test", "-e", self.config.luks_mapper_path(index)]):
                return False
        return True

    def execute(self):
        from pathlib import Path

        passphrase = self.config.luks_passphrase()
        ok = True
        for index, disk in enumerate(self.config.disks, start=1):
            partition = self.config.luks_partition(disk)
            mapper = self.config.luks_mapper(index)
            mapper_path = self.config.luks_mapper_path(index)
            if not exists(["cryptsetup", "isLuks", partition]):
                ok = run(
                    [
                        "cryptsetup",
                        "luksFormat",
                        "--batch-mode",
                        "--type",
                        "luks2",
                        "-c",
                        self.config.luks.cipher,
                        "-s",
                        str(self.config.luks.key_size),
                        "-h",
                        self.config.luks.hash,
                        partition,
                    ],
                    input_text=passphrase,
                ) and ok
            if not Path(mapper_path).exists():
                ok = run(
                    ["cryptsetup", "luksOpen", partition, mapper],
                    input_text=passphrase,
                ) and ok
        return ok
