from __future__ import annotations

from typing import TYPE_CHECKING

from randovania.games.dread.layout.dread_configuration import (
    DreadArtifactConfig,
    DreadConfiguration,
)
from randovania.layout.preset_describer import (
    GamePresetDescriber,
    fill_template_strings_from_tree,
    handle_progressive_expected_counts,
    has_shuffled_item,
    message_for_required_mains,
)

if TYPE_CHECKING:
    from randovania.game_description.pickup.standard_pickup import (
        StandardPickupDefinition,
    )
    from randovania.layout.base.base_configuration import BaseConfiguration


def describe_artifacts(artifacts: DreadArtifactConfig) -> list[dict[str, bool]]:
    has_artifacts = artifacts.required_artifacts > 0
    if has_artifacts:
        return [
            {
                f"{artifacts.required_artifacts} Metroid DNA": True,
            },
            {
                "Prefers E.M.M.I.": artifacts.prefer_emmi,
                "Prefers major bosses": artifacts.prefer_major_bosses,
            },
        ]
    else:
        return [
            {
                "Reach Itorash": True,
            }
        ]


def _format_environmental_damage(configuration: DreadConfiguration):
    def format_dmg(value: int | None):
        if value is None:
            return "Unmodified"
        elif value == 0:
            return "Removed"
        else:
            return f"Constant {value} dmg/s"

    return [
        {f"{name}: {format_dmg(dmg)}": True}
        for name, dmg in [
            ("Heat", configuration.constant_heat_damage),
            ("Cold", configuration.constant_cold_damage),
            ("Lava", configuration.constant_lava_damage),
        ]
    ]


class DreadPresetDescriber(GamePresetDescriber):
    def format_params(self, configuration: BaseConfiguration) -> dict[str, list[str]]:
        assert isinstance(configuration, DreadConfiguration)

        standard_pickups = configuration.standard_pickup_configuration
        template_strings = super().format_params(configuration)

        extra_message_tree = {
            "Logic Settings": [
                {
                    "Highly Dangerous Logic": configuration.allow_highly_dangerous_logic,
                }
            ],
            "Difficulty": [
                {
                    "Immediate Energy Part": configuration.immediate_energy_parts,
                },
                {f"{configuration.energy_per_tank} energy per Energy Tank": configuration.energy_per_tank != 100},
            ],
            "Item Pool": [
                {
                    "Progressive Beam": has_shuffled_item(standard_pickups, "Progressive Beam"),
                    "Progressive Charge Beam": has_shuffled_item(standard_pickups, "Progressive Charge Beam"),
                    "Progressive Missile": has_shuffled_item(standard_pickups, "Progressive Missile"),
                    "Progressive Bomb": has_shuffled_item(standard_pickups, "Progressive Bomb"),
                    "Progressive Suit": has_shuffled_item(standard_pickups, "Progressive Suit"),
                    "Progressive Spin": has_shuffled_item(standard_pickups, "Progressive Spin"),
                }
            ],
            "Gameplay": [
                {
                    f"Elevators/Shuttles: {configuration.teleporters.description('transporters')}": (
                        not configuration.teleporters.is_vanilla
                    )
                }
            ],
            "Goal": describe_artifacts(configuration.artifacts),
            "Game Changes": [
                message_for_required_mains(
                    configuration.ammo_pickup_configuration,
                    {
                        "Power Bomb needs Main": "Power Bomb Expansion",
                    },
                ),
                {
                    "Open Hanubia Shortcut": configuration.hanubia_shortcut_no_grapple,
                    "Easier Path to Itorash in Hanubia": configuration.hanubia_easier_path_to_itorash,
                },
                {
                    f"Raven Beak Damage: {configuration.raven_beak_damage_table_handling.long_name}": (
                        not configuration.raven_beak_damage_table_handling.is_default
                    ),
                },
                {
                    "X Starts Released": configuration.x_starts_released,
                },
                {
                    "Power Bomb Limitations": configuration.nerf_power_bombs,
                },
            ],
            "Environmental Damage": _format_environmental_damage(configuration),
        }
        fill_template_strings_from_tree(template_strings, extra_message_tree)

        return template_strings

    def expected_shuffled_pickup_count(self, configuration: BaseConfiguration) -> dict[StandardPickupDefinition, int]:
        count = super().expected_shuffled_pickup_count(configuration)
        majors = configuration.standard_pickup_configuration

        from randovania.games.dread.pickup_database import progressive_items

        for progressive_item_name, non_progressive_items in progressive_items.tuples():
            handle_progressive_expected_counts(count, majors, progressive_item_name, non_progressive_items)

        return count
