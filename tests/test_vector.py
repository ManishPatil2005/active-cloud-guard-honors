from unittest.mock import patch, MagicMock
import pytest
from cloudguard.vector import retrieve_vector


def test_stale_vector_index_rejected():
    with (
        patch("cloudguard.vector.collection") as get_collection,
        patch("cloudguard.vector.embed") as embed,
    ):
        col = MagicMock()
        col.count.return_value = 0
        get_collection.return_value = (col, [{"id": "s1"}], "digest")
        with pytest.raises(ValueError):
            retrieve_vector("q", "kb", "index")
    embed.assert_not_called()
