# Make sure we have the correct relative path
from sys import path, exc_info, stdout

path.insert(0, '..')  # chang to the root directory of the project
#########################################################################
import sys
import traceback
import os
import psutil
import git
from zeppos_logging.app_logger import AppLogger
from zeppos_application.app_config import AppConfig
from zeppos_logging.app_logger_json_conifg_name import AppLoggerJsonConfigName
from zeppos_root.root import Root


class RunServerBase:
    def __init__(self, current_module_filename):
        AppLogger.logger.debug("******* STARTING APP *******")
        AppLogger.logger.debug("Initializing application.")
        self._application_name = RunServerBase._get_config_values(current_module_filename)

    @staticmethod
    def _get_config_values(current_module_filename):
        AppLogger.logger.debug("Get config values.")
        config_dict = RunServerBase.get_config_dict(current_module_filename)
        AppLogger.logger.debug(f"Application Name: {config_dict['APPLICATION_NAME']}")
        return config_dict['APPLICATION_NAME']

    @staticmethod
    def get_config_dict(current_module_filename):
        branch = RunServerBase._get_current_branch()
        AppLogger.logger.debug(f"Get config dictionary: config.{branch}.json")
        AppLogger.logger.debug(f"current_module_filename: {current_module_filename}")
        return AppConfig.get_json_config_dict(
            current_module_filename=current_module_filename,
            config_file_name=f"config.{branch}.json"
        )

    def start_app(self):
        AppLogger.logger.debug('Entering start_app')
        result = False
        try:
            if not self._is_app_running():
                AppLogger.logger.debug(f"The app [{self._application_name}] is not running! Let's start it")
                self._create_pid_file()
                AppLogger.logger.debug('Exiting start_app')
                result = True
            else:
                AppLogger.logger.debug('Application is already started')

        except Exception as e:
            AppLogger.logger.error(
                f'Error start_app: [{e}] - LineNo: [{sys.exc_info()[-1].tb_lineno}] \n\r '
                f'{traceback.print_exc(file=sys.stdout)}')

        return result
        AppLogger.logger.debug('Exiting start_app')

    def __del__(self):
        AppLogger.logger.debug("__del__")
        AppLogger.logger.debug("******* ENDING APP *******")

    def _is_app_running(self):
        proc_object = self._get_proc_object()
        if proc_object:
            return proc_object.status().upper() == "RUNNING"
        return False

    def _get_pid_full_file_name(self):
        current_user_directory = os.path.expanduser("~")
        directory = os.path.join(current_user_directory, ".pidfile")
        pid_file_name = f'{self._application_name}.pid'
        full_file_name = os.path.join(directory, pid_file_name)
        os.makedirs(os.path.dirname(full_file_name), exist_ok=True)
        return full_file_name

    def _create_pid_file(self):
        pid_id = os.getpid()
        pid_full_file_name = self._get_pid_full_file_name()
        AppLogger.logger.debug(f"creating pid_file [{pid_full_file_name}] with pid_id [{pid_id}]")
        with open(pid_full_file_name, 'w') as fl:
            fl.writelines(str(pid_id))

    def _get_proc_object(self):
        proc_object = None
        pid_full_file_name = self._get_pid_full_file_name()
        if os.path.exists(pid_full_file_name):
            try:
                with open(pid_full_file_name, 'r') as fl:
                    pid_str = fl.readline()  # separate lines for easier debugging thru logs
                    pid = int(pid_str)

                for proc in psutil.process_iter():
                    if proc.pid == pid:
                        proc_object = proc
            except Exception as error:
                AppLogger.logger.error(f"Application | {self._application_name} | {error}")
        return proc_object

    @staticmethod
    def main_aws_logging(logger_name):
        config_dict = RunServerBase.get_config_dict()
        AppLogger.configure_and_get_logger(
            logger_name,
            AppLoggerJsonConfigName.default_with_watchtower_format_1(),
            watchtower_log_group=config_dict["APPLICATION_NAME"],
            watchtower_stream_name=config_dict["ENVIRONMENT"]
        )
        if config_dict["DEBUG_MODE"].upper() == "TRUE":
            AppLogger.set_debug_level()

    @staticmethod
    def main_basic_logging(logger_name):
        config_dict = RunServerBase.get_config_dict()
        AppLogger.configure_and_get_logger(
            logger_name,
            AppLoggerJsonConfigName.default_format_1()
        )
        if config_dict["DEBUG_MODE"].upper() == "TRUE":
            AppLogger.set_debug_level()

    @staticmethod
    def _get_current_branch():
        g = git.cmd.Git(Root.find_root_of_project(__file__))
        for line in g.branch().split('\n'):
            if line.startswith("*"):
                AppLogger.logger.debug(f"Current Git Branch: {line[1:].strip()}")
                return line[1:].strip()
        return None
