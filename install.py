#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import os
import sys

from config import InstallConfig
from logging_config import configure
from tasks import (
    AddPveRepository,
    AptFullUpgrade,
    ChrootPackages,
    ConfigureBaseSystem,
    ConfigureGrub,
    ConfigureProxmoxHosts,
    CopyZpoolCache,
    CreateBootPool,
    CreateDatasets,
    CreateRootPool,
    Debootstrap,
    DisableAutoMounting,
    DistUpgrade,
    EnableBpoolImport,
    InstallGrub,
    InstallProxmoxVe,
    InstallPveKernel,
    MirrorGrubEfi,
    MountTmpfsRun,
    OpenSSHServerInstall,
    PartitionDisk,
    RemoveDebianKernel,
    RemoveOsProber,
    SetupCrypttab,
    SetupDropbear,
    SetupEfiPartition,
    SetupLuks,
    UnmountAndExport,
    UpdateRepo,
    WipeDisk,
    ZfsListCache,
    ZfsPrerequisitesInstall,
)

logger = logging.getLogger(__name__)


def build_pre_install_tasks(config: InstallConfig, reboot: bool) -> list:
    return [
        UpdateRepo(),
        OpenSSHServerInstall(),
        DisableAutoMounting(),
        ZfsPrerequisitesInstall(),
        WipeDisk(config),
        PartitionDisk(config),
        CreateBootPool(config),
        SetupLuks(config),
        CreateRootPool(config),
        CreateDatasets(config),
        MountTmpfsRun(config),
        Debootstrap(config),
        CopyZpoolCache(config),
        ConfigureBaseSystem(config),
        ChrootPackages(config),
        SetupCrypttab(config),
        SetupDropbear(config),
        SetupEfiPartition(config),
        EnableBpoolImport(config),
        ConfigureGrub(config),
        InstallGrub(config),
        ZfsListCache(config),
        UnmountAndExport(config, reboot=reboot),
    ]


def build_post_install_tasks(config: InstallConfig) -> list:
    return [
        MirrorGrubEfi(config),
        ConfigureProxmoxHosts(config),
        DistUpgrade(),
    ]


def build_pxe_install_tasks(config: InstallConfig) -> list:
    return [
        ConfigureProxmoxHosts(config),
        AptFullUpgrade(),
        AddPveRepository(),
        InstallPveKernel(),
        InstallProxmoxVe(),
        RemoveDebianKernel(),
        RemoveOsProber(),
    ]


def run_tasks(tasks: list, dry_run: bool = False) -> int:
    for task in tasks:
        logger.info("[Task: %s]", task.name)
        if task.check():
            logger.info("[Task: %s] already complete", task.name)
            continue
        if dry_run:
            logger.info("[Task: %s] would run", task.name)
            continue
        if not task.execute():
            logger.error("[Task: %s] failed", task.name)
            return 1
        logger.info("[Task: %s] done", task.name)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Debian Trixie root-on-ZFS + LUKS installer with Proxmox VE support",
    )
    parser.add_argument("--config", default="config.yaml", help="YAML config file")
    parser.add_argument("--pre-install", action="store_true", help="Live ISO phase")
    parser.add_argument("--post-install", action="store_true", help="First-boot phase")
    parser.add_argument("--pxe-install", action="store_true", help="Install Proxmox VE")
    parser.add_argument("--dry-run", action="store_true", help="Only evaluate task checks")
    parser.add_argument("--no-reboot", action="store_true", help="Skip reboot after pre-install")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure(logging.DEBUG if args.verbose else logging.INFO)

    if os.geteuid() != 0:
        logger.error("Run as root.")
        return 1

    selected = sum(bool(flag) for flag in (args.pre_install, args.post_install, args.pxe_install))
    if selected != 1:
        logger.error("Choose exactly one of --pre-install, --post-install, or --pxe-install")
        return 1

    config = InstallConfig.from_file(args.config) if os.path.exists(args.config) else InstallConfig()
    if not config.disks and args.pre_install:
        logger.error("Configure at least two disks in %s for mirror install", args.config)
        return 1

    if args.pre_install:
        tasks = build_pre_install_tasks(config, reboot=not args.no_reboot)
    elif args.post_install:
        tasks = build_post_install_tasks(config)
    else:
        tasks = build_pxe_install_tasks(config)

    return run_tasks(tasks, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
