import unittest
from tests.base_test_class import BaseClass


class EntityIterTests(BaseClass):
    @classmethod
    def setUpClass(cls):
        super(EntityIterTests, cls).setUpClass()
        cls.asset_id = 2370

    @classmethod
    def tearDownClass(cls):
        super(EntityIterTests, cls).tearDownClass()

    def setUp(self):
        self.return_fields = ["code", "id", "project", "description", "sg_asset_type"]
        self.assets = self.shotgun_model.EntityIter(
            "Asset", self.return_fields, self._context, self._sg
        )

    def test_load_data(self):
        self.assets.entity_filter = [
            ["code", "in", ["AssetIter1", "AssetIter2", "AssetIter3"]]
        ]
        self.assets.load()

        sg_data = self._sg.find("Asset", self.assets.entity_filter, self.return_fields)
        for asset in self.assets:
            for sg_asset in sg_data:
                if asset.code != sg_asset.get("code"):
                    continue

                for field in self.return_fields:
                    attr = getattr(asset, field)
                    self.assertEqual(attr, sg_asset.get(field))

    def test_len_entities(self):
        self.assets.entity_filter = [
            ["code", "in", ["AssetIter1", "AssetIter2", "AssetIter3"]]
        ]
        self.assets.load()
        sg_data = self._sg.find("Asset", self.assets.entity_filter, self.return_fields)
        self.assertEqual(len(self.assets), len(sg_data))


if __name__ == "__main__":
    unittest.main()
