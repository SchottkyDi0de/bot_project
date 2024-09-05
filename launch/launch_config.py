import yaml

from lib.utils.singleton_factory import singleton
from lib.settings.settings import EnvConfig
from launch.launch_cfg_struct import LaunchConfigStruct

env_config = EnvConfig


@singleton
class LaunchConfig:
    def __init__(self):
        with open('launch/launch_config.yaml', 'r') as config_file:
            self.config = yaml.safe_load(config_file)

        self.config = LaunchConfigStruct.model_validate(self.config)

    def get(self) -> LaunchConfigStruct:
        return self.config
