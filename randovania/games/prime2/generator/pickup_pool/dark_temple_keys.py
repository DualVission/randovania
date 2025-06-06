from __future__ import annotations

from typing import TYPE_CHECKING

from randovania.generator.pickup_pool import PoolResults
from randovania.generator.pickup_pool.pickup_creator import create_generated_pickup

if TYPE_CHECKING:
    from randovania.game_description.game_database_view import ResourceDatabaseView
    from randovania.game_description.pickup.pickup_database import PickupDatabase
    from randovania.game_description.pickup.pickup_entry import PickupEntry


def add_dark_temple_keys(
    resource_database: ResourceDatabaseView,
    pickup_database: PickupDatabase,
) -> PoolResults:
    """
    :param resource_database:
    :param pickup_database:
    :return:
    """
    item_pool: list[PickupEntry] = []

    for temple_key in ("Dark Agon Key", "Dark Torvus Key", "Ing Hive Key"):
        for i in range(3):
            item_pool.append(create_generated_pickup(temple_key, resource_database, pickup_database, i=i + 1))

    return PoolResults(item_pool, {}, [])
