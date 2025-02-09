from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from randovania.game_description.db.hint_node import HintNode
from randovania.game_description.db.node import NodeContext
from randovania.game_description.db.node_identifier import NodeIdentifier
from randovania.game_description.resources.resource_collection import ResourceCollection

if TYPE_CHECKING:
    from randovania.game_description.resources.resource_info import ResourceInfo


@pytest.fixture(params=[False, True])
def logbook_node(request, blank_game_description):
    has_translator = request.param
    translator = blank_game_description.resource_database.get_item("BlueKey")

    node = blank_game_description.region_list.node_by_identifier(
        NodeIdentifier.create(
            "Intro",
            "Hint Room",
            "Hint with Translator" if has_translator else "Hint no Translator",
        )
    )
    assert isinstance(node, HintNode)

    return has_translator, translator, node


def test_logbook_node_requirements_to_leave(logbook_node, empty_patches):
    # Setup
    has_translator, translator, node = logbook_node
    db = empty_patches.game.resource_database

    def ctx(resources):
        return NodeContext(empty_patches, resources, db, empty_patches.game.region_list)

    # Run
    to_leave = node.requirement_to_leave(ctx({}))

    # Assert
    rc2 = ResourceCollection.from_resource_gain(db, [])
    rc3 = ResourceCollection.from_resource_gain(db, [(translator, 1)])

    assert to_leave.satisfied(rc2, 99, None) != has_translator
    assert to_leave.satisfied(rc3, 99, None)


def test_logbook_node_can_collect(logbook_node, empty_patches):
    # Setup
    db = empty_patches.game.resource_database
    has_translator, translator, node = logbook_node
    node_provider = MagicMock()

    def ctx(*args: ResourceInfo):
        resources = ResourceCollection.from_dict(db, {r: 1 for r in args})
        return NodeContext(empty_patches, resources, db, node_provider)

    assert node.can_collect(ctx()) != has_translator
    assert node.can_collect(ctx(translator))

    resource = node.resource(ctx())
    assert not node.can_collect(ctx(resource))
    assert not node.can_collect(ctx(resource, translator))


def test_logbook_node_resource_gain_on_collect(logbook_node, empty_patches):
    # Setup
    db = empty_patches.game.resource_database
    node = logbook_node[-1]
    context = NodeContext(empty_patches, ResourceCollection(), db, MagicMock())

    # Run
    gain = node.resource_gain_on_collect(context)

    # Assert
    assert dict(gain) == {node.resource(context): 1}
