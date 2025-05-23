from __future__ import annotations

import dataclasses
import shutil
from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

import randovania
from randovania import monitoring
from randovania.exporter.game_exporter import GameExporter, GameExportParams, input_hash_for_directory
from randovania.lib import json_lib, status_update_lib

if TYPE_CHECKING:
    from randovania.exporter.patch_data_factory import PatcherDataMeta


class DreadModPlatform(Enum):
    RYUJINX = "ryujinx"
    ATMOSPHERE = "atmosphere"


class LinuxRyujinxPath(Enum):
    NATIVE = "native"
    FLATPAK = "flatpak"


@dataclasses.dataclass(frozen=True)
class DreadGameExportParams(GameExportParams):
    input_path: Path
    output_path: Path
    target_platform: DreadModPlatform
    use_exlaunch: bool
    clean_output_path: bool
    post_export: Callable[[status_update_lib.ProgressUpdateCallable], None] | None

    def calculate_input_hash(self) -> dict[str, str | None]:
        return {
            "input_path": input_hash_for_directory(self.input_path),
        }


class DreadGameExporter(GameExporter[DreadGameExportParams]):
    _busy: bool = False

    @property
    def can_start_new_export(self) -> bool:
        """
        Checks if the exporter is busy right now
        """
        return self._busy

    @property
    def export_can_be_aborted(self) -> bool:
        """
        Checks if export_game can be aborted
        """
        return True

    def export_params_type(self) -> type[DreadGameExportParams]:
        """
        Returns the type of the GameExportParams expected by this exporter.
        """
        return DreadGameExportParams

    def _before_export(self):
        assert not self._busy
        self._busy = True

    def _after_export(self):
        self._busy = False

    def _do_export_game(
        self,
        patch_data: dict,
        export_params: DreadGameExportParams,
        progress_update: status_update_lib.ProgressUpdateCallable,
        randovania_meta: PatcherDataMeta,
    ):
        export_params.output_path.mkdir(parents=True, exist_ok=True)

        patch_data["mod_compatibility"] = export_params.target_platform.value
        patch_data["mod_category"] = "romfs" if export_params.use_exlaunch else "pkg"
        monitoring.set_tag("dread_mod_category", patch_data["mod_category"])
        monitoring.set_tag("dread_target_platform", patch_data["mod_compatibility"])

        from open_dread_rando.version import version as open_dread_rando_version

        text_patches = patch_data["text_patches"]
        text_patches["GUI_COMPANY_TITLE_SCREEN"] = text_patches["GUI_COMPANY_TITLE_SCREEN"].replace(
            "<versions>",
            f"Randovania {randovania.VERSION} - open-dread-rando {open_dread_rando_version}",
        )

        if not randovania_meta["in_race_setting"]:
            json_lib.write_path(export_params.output_path.joinpath("patcher.json"), patch_data)

        patcher_update: status_update_lib.ProgressUpdateCallable
        if export_params.post_export is not None:
            patcher_update = status_update_lib.OffsetProgressUpdate(progress_update, 0, 0.75)
        else:
            patcher_update = progress_update

        if export_params.clean_output_path:
            progress_update(f"Deleting {export_params.output_path}", -1)
            shutil.rmtree(export_params.output_path, ignore_errors=True)
            progress_update(f"Finished deleting {export_params.output_path}", -1)

        with monitoring.trace_block("open_dread_rando.patch_with_status_update"):
            import open_dread_rando

            open_dread_rando.patch_with_status_update(
                export_params.input_path,
                export_params.output_path,
                patch_data,
                lambda progress, msg: patcher_update(msg, progress),
            )

        if export_params.post_export is not None:
            export_params.post_export(status_update_lib.OffsetProgressUpdate(progress_update, 0.75, 0.25))
