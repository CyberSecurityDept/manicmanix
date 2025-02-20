import logging
from typing import Optional

from mvt.common.command import Command

from .modules.adb import ADB_MODULES

log = logging.getLogger(__name__)


class CmdAndroidCheckADB(Command):
    def __init__(
        self,
        target_path: Optional[str] = None,
        results_path: Optional[str] = None,
        ioc_files: Optional[list] = None,
        module_name: Optional[str] = None,
        serial: Optional[str] = None,
        module_options: Optional[dict] = None,
    ) -> None:
        super().__init__(
            target_path=target_path,
            results_path=results_path,
            ioc_files=ioc_files,
            module_name=module_name,
            serial=serial,
            module_options=module_options,
            log=log,
        )

        self.name = "check-adb"
        self.modules = ADB_MODULES
