from __future__ import annotations

import pytest

from randovania.game.game_enum import RandovaniaGame
from randovania.game_description.pickup.pickup_entry import PickupEntry, PickupModel
from randovania.game_description.resources.item_resource_info import ItemResourceInfo


def test_extra_resources_maximum(generic_pickup_category, default_generator_params):
    item = ItemResourceInfo(0, "Item", "Item", 2)
    msg = "Attempt to give 5 of Item, more than max capacity"

    with pytest.raises(ValueError, match=msg):
        PickupEntry(
            name="broken",
            model=PickupModel(RandovaniaGame.METROID_PRIME_ECHOES, "Nothing"),
            gui_category=generic_pickup_category,
            hint_features=frozenset((generic_pickup_category,)),
            progression=(),
            extra_resources=((item, 5),),
            generator_params=default_generator_params,
        )
