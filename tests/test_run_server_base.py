import unittest
from zeppos_api.run_server_base import RunServerBase
from zeppos_logging.app_logger import AppLogger
import os


class TestTheProjectMethods(unittest.TestCase):
    def test_get_config_dict_methods(self):
        # AppLogger.set_debug_level()
        self.assertEqual("test_windows_service_app", RunServerBase.get_config_dict(__file__)["APPLICATION_NAME"].lower())
        self.assertEqual("true", RunServerBase.get_config_dict(__file__)["DEBUG_MODE"].lower())
        self.assertEqual("main", RunServerBase.get_config_dict(__file__)["ENVIRONMENT"].lower())

    def test___init__methods(self):
        self.assertEqual("test_windows_service_app", RunServerBase(__file__)._application_name)

    def test_start_app_methods(self):
        if os.path.exists(os.path.join(os.path.join(os.path.expanduser("~"), ".pidfile"),
                                       'test_windows_service_app.pid')):
            os.remove(os.path.join(os.path.join(os.path.expanduser("~"), ".pidfile"),
                                   'test_windows_service_app.pid'))
        RunServerBase(__file__).start_app()

        self.assertEqual(True, os.path.exists(os.path.join(os.path.join(os.path.expanduser("~"), ".pidfile"),
                                                           'test_windows_service_app.pid')))

        if os.path.exists(os.path.join(os.path.join(os.path.expanduser("~"), ".pidfile"),
                                       'test_windows_service_app.pid')):
            os.remove(os.path.join(os.path.join(os.path.expanduser("~"), ".pidfile"),
                                   'test_windows_service_app.pid'))


if __name__ == '__main__':
    unittest.main()
