import unittest
from tests import model


class ShotgunGlobalsTest(model.BaseClass):
    @classmethod
    def setUpClass(cls):
        super(ShotgunGlobalsTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(ShotgunGlobalsTest, cls).tearDownClass()

    def test_get_entity_by_alias(self):
        self.assertEqual(
            self.shotgun_globals.get_custom_entity_by_alias("Scene"), "CustomEntity04"
        )
        self.assertEqual(
            self.shotgun_globals.get_custom_entity_by_alias("node_type"),
            "CustomNonProjectEntity01",
        )
        self.assertEqual(
            self.shotgun_globals.get_custom_entity_by_alias("pre_production"),
            "CustomEntity01",
        )
        self.assertIsNone(
            self.shotgun_globals.get_custom_entity_by_alias("UnknownLabel")
        )


if __name__ == "__main__":
    unittest.main()
