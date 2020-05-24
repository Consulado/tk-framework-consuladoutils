import unittest
import os
import sys


class ContextMock(object):
    project = {"type": "Project", "id": 375, "name": "dev1"}


class BaseClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.getenv("TK_FRAMEWORK_CONSULADOUTILS") not in sys.path:
            sys.path.insert(0, os.getenv("TK_FRAMEWORK_CONSULADOUTILS"))

        from python.shotgun_model import shotgun_model
        import python.shotgun_globals as shotgun_globals
        from shotgun_api3 import Shotgun  # pragma: no cover

        cls._context = ContextMock()
        cls._sg = Shotgun(
            os.getenv("SG_HOST"),
            script_name=os.getenv("SG_SCRIPT_NAME"),
            api_key=os.getenv("SG_API_KEY"),
        )
        cls.shotgun_model = shotgun_model
        cls.shotgun_globals = shotgun_globals

    @classmethod
    def tearDownClass(cls):
        cls._sg.close()
