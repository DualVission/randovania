from __future__ import annotations

from typing import TYPE_CHECKING

import randovania.game.data
import randovania.game.development_state
import randovania.game.generator
import randovania.game.gui
import randovania.game.layout
from randovania.games.planets_zebeth import layout

if TYPE_CHECKING:
    from randovania.exporter.game_exporter import GameExporter
    from randovania.exporter.patch_data_factory import PatchDataFactory
    from randovania.interface_common.options import PerGameOptions


def _options() -> type[PerGameOptions]:
    from randovania.games.planets_zebeth.exporter.options import PlanetsZebethPerGameOptions

    return PlanetsZebethPerGameOptions


def _gui() -> randovania.game.gui.GameGui:
    from randovania.games.planets_zebeth import gui

    return randovania.game.gui.GameGui(
        game_tab=gui.PlanetsZebethGameTabWidget,
        tab_provider=gui.preset_tabs,
        cosmetic_dialog=gui.PlanetsZebethCosmeticPatchesDialog,
        export_dialog=gui.PlanetsZebethGameExportDialog,
        progressive_item_gui_tuples=(),
        spoiler_visualizer=(),
    )


def _generator() -> randovania.game.generator.GameGenerator:
    from randovania.games.planets_zebeth import generator
    from randovania.generator.filler.weights import ActionWeights

    return randovania.game.generator.GameGenerator(
        pickup_pool_creator=generator.pool_creator,
        bootstrap=generator.PlanetsZebethBootstrap(),
        base_patches_factory=generator.PlanetsZebethBasePatchesFactory(),
        action_weights=ActionWeights(),
    )


def _hints() -> randovania.game.hints.GameHints:
    from randovania.generator.hint_distributor import AllJokesHintDistributor

    return randovania.game.hints.GameHints(
        hint_distributor=AllJokesHintDistributor(),
        specific_pickup_hints={},
    )


def _patch_data_factory() -> type[PatchDataFactory]:
    from randovania.games.planets_zebeth.exporter.patch_data_factory import PlanetsZebethPatchDataFactory

    return PlanetsZebethPatchDataFactory


def _exporter() -> GameExporter:
    from randovania.games.planets_zebeth.exporter.game_exporter import PlanetsZebethGameExporter

    return PlanetsZebethGameExporter()


def _hash_words() -> list[str]:
    from randovania.games.planets_zebeth.hash_words import HASH_WORDS

    return HASH_WORDS


game_data: randovania.game.data.GameData = randovania.game.data.GameData(
    short_name="Planets Zebeth",
    long_name="Metroid Planets (Zebeth)",
    development_state=randovania.game.development_state.DevelopmentState.SOURCE_ONLY,
    presets=[
        {"path": "starter_preset.rdvpreset"},
        {"path": "starter_preset_shuffle_keys.rdvpreset"},
    ],
    faq=[
        (
            "Which versions of Metroid Planets are supported?",
            "Only version 1.27g is supported. Any other versions will fail to export. ",
        )
    ],
    hash_words=_hash_words(),
    layout=randovania.game.layout.GameLayout(
        configuration=layout.PlanetsZebethConfiguration,
        cosmetic_patches=layout.PlanetsZebethCosmeticPatches,
        preset_describer=layout.PlanetsZebethPresetDescriber(),
    ),
    options=_options,
    gui=_gui,
    generator=_generator,
    hints=_hints,
    patch_data_factory=_patch_data_factory,
    exporter=_exporter,
    multiple_start_nodes_per_area=False,
    defaults_available_in_game_sessions=False,
)
