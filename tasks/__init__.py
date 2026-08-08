from .task import Task
from .task_01_update_repo import UpdateRepo
from .task_02_openssh_server_install import OpenSSHServerInstall
from .task_03_disable_auto_mounting import DisableAutoMounting
from .task_04_zfs_prerequisites_install import ZfsPrerequisitesInstall
from .task_05_wipe_disk import WipeDisk
from .task_06_partition_disk import PartitionDisk
from .task_07_create_bpool import CreateBootPool
from .task_08_setup_luks import SetupLuks
from .task_09_create_rpool import CreateRootPool
from .task_10_create_datasets import CreateDatasets
from .task_11_mount_tmpfs import MountTmpfsRun
from .task_12_debootstrap import Debootstrap
from .task_13_copy_zpool_cache import CopyZpoolCache
from .task_14_configure_base import ConfigureBaseSystem
from .task_15_chroot_packages import ChrootPackages
from .task_16_crypttab import SetupCrypttab
from .task_17_dropbear import SetupDropbear
from .task_18_efi_partition import SetupEfiPartition
from .task_19_enable_bpool_import import EnableBpoolImport
from .task_20_configure_grub import ConfigureGrub
from .task_21_install_grub import InstallGrub
from .task_22_zfs_list_cache import ZfsListCache
from .task_23_unmount_export import UnmountAndExport
from .task_24_post_install import ConfigureProxmoxHosts, DistUpgrade, MirrorGrubEfi
from .task_25_pve_install import (
    AddPveRepository,
    AptFullUpgrade,
    InstallProxmoxVe,
    InstallPveKernel,
    RemoveDebianKernel,
    RemoveOsProber,
)

__all__ = [
    "Task",
    "UpdateRepo",
    "OpenSSHServerInstall",
    "DisableAutoMounting",
    "ZfsPrerequisitesInstall",
    "WipeDisk",
    "PartitionDisk",
    "CreateBootPool",
    "SetupLuks",
    "CreateRootPool",
    "CreateDatasets",
    "MountTmpfsRun",
    "Debootstrap",
    "CopyZpoolCache",
    "ConfigureBaseSystem",
    "ChrootPackages",
    "SetupCrypttab",
    "SetupDropbear",
    "SetupEfiPartition",
    "EnableBpoolImport",
    "ConfigureGrub",
    "InstallGrub",
    "ZfsListCache",
    "UnmountAndExport",
    "MirrorGrubEfi",
    "ConfigureProxmoxHosts",
    "DistUpgrade",
    "AptFullUpgrade",
    "AddPveRepository",
    "InstallPveKernel",
    "InstallProxmoxVe",
    "RemoveDebianKernel",
    "RemoveOsProber",
]
