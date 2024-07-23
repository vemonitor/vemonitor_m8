"""Vemonitor main runner."""
import logging
from ve_utils.utype import UType as Ut

from vemonitor_m8.core.async_app_run import AppBlockRun
from vemonitor_m8.conf_manager.config_loader import ConfigLoader

logging.basicConfig()
logger = logging.getLogger("vemonitor")


class AppRun:
    """Run App Helper"""
    def __init__(self, block: str, app: str):
        self.conf = None
        self.app = None
        self.params = {
            "block": block,
            "app": app,
        }
        if self.load_conf():
            self.run()

    def has_params(self) -> bool:
        """Test if instance has params"""
        return Ut.is_dict(self.params)

    def load_conf(self):
        """Load configuration."""
        result = False
        if self.has_params():
            loader = ConfigLoader()
            self.conf = loader.get_settings_from_schema(
                block_name=self.params.get("block"),
                app_name=self.params.get("app"),
            )
            result = True
        return result

    def run(self) -> bool:
        """Test if instance has params"""
        if self.conf.is_valid():
            logger.info(
                "Starting app blocks workers"
            )
            self.app = AppBlockRun(self.conf)
            self.app.run_block()
