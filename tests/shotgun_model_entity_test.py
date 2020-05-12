import unittest
from tests.base_test_class import BaseClass, ContextMock


class EntityTests(BaseClass):
    @classmethod
    def setUpClass(cls):
        super(EntityTests, cls).setUpClass()
        cls.asset_id = 2370

    @classmethod
    def tearDownClass(cls):
        cls._sg.update("Asset", cls.asset_id, {"code": "Asset1", "description": ""})
        super(EntityTests, cls).tearDownClass()

    def test_shotgun_entity_metadata(self):
        self.asset = self.shotgun_model.Entity(
            "Asset", ["code", "id"], self._context, self._sg
        )
        self.asset.id = 1
        self.assertEqual(self.asset.shotgun_entity_data, {"type": "Asset", "id": 1})

    def test_load_data_into_entity(self):
        sg_asset = self._sg.find_one(
            "Asset",
            [["project", "is", ContextMock.project], ["id", "is", self.asset_id]],
            ["code", "id", "project", "description"],
        )
        self.asset = self.shotgun_model.Entity(
            "Asset", ["code", "id", "project", "description"], self._context, self._sg
        )
        self.asset.id = self.asset_id
        self.asset.load([["id", "is", self.asset.id]])

        self.assertEqual(self.asset.id, self.asset_id)
        self.assertEqual(
            self.asset.project, self._context.project,
        )
        self.assertEqual(self.asset.code, sg_asset.get("code"))
        self.assertEqual(self.asset.description, sg_asset.get("description"))

    def test_can_change_data_entity(self):
        self.asset = self.shotgun_model.Entity(
            "Asset", ["code", "id", "project", "description"], self._context, self._sg
        )
        self.asset.id = self.asset_id
        self.asset.description = "new description"
        self.asset.code = "Asset2"
        self.asset.update()

        sg_asset = self._sg.find_one(
            "Asset",
            [["project", "is", ContextMock.project], ["id", "is", self.asset_id]],
            ["code", "id", "project", "description"],
        )

        self.assertEqual(self.asset.description, sg_asset.get("description"))
        self.assertEqual(self.asset.code, sg_asset.get("code"))

    def test_can_create_new_entity(self):
        self.asset = self.shotgun_model.Entity(
            "Asset",
            ["code", "id", "project", "description", "sg_asset_type"],
            self._context,
            self._sg,
        )
        self.asset.code = "NewAsset1"
        self.asset.description = "Hey, this is a new asset!"
        self.asset.sg_asset_type = "Character"
        self.asset.create()

        asset_created = self._sg.find_one(
            "Asset",
            [["project", "is", ContextMock.project], ["code", "is", "NewAsset1"]],
            ["code", "id", "project", "description", "sg_asset_type"],
        )

        self.assertEqual(self.asset.code, asset_created.get("code"))
        self.assertEqual(self.asset.id, asset_created.get("id"))
        self.assertEqual(self.asset.project, asset_created.get("project"))
        self.assertEqual(self.asset.description, asset_created.get("description"))
        self.assertEqual(self.asset.sg_asset_type, asset_created.get("sg_asset_type"))

        # tears down of this test
        self._sg.delete("Asset", asset_created.get("id"))


if __name__ == "__main__":
    unittest.main()
