class PartitionDisk(Task):

    def __init__(self, disk):
        self.disk = disk
        self.name = f"Partition {disk}"

    def check(self):
        return all(
            exists(["sgdisk", "-i", str(i), self.disk])
            for i in range(1, 4)
        )

    def execute(self):
       return (
            run([
                "sgdisk",
                "-n", "1:1M:+512M",
                "-t", "1:EF00",
                "-c", "1:EFI",
                self.disk,
            ])
            and
            run([
                "sgdisk",
                "-n", "2:0:+1G",
                "-t", "2:8300",
                "-c", "2:BOOT",
                self.disk,
            ])
            and
            run([
                "sgdisk",
                "-n", "3:0:0",
                "-t", "3:8309",
                "-c", "3:LUKS",
                self.disk,
            ])
            and
            run(["partprobe", self.disk])
        )
