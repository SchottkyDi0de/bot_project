from pydantic import BaseModel


class Dev(BaseModel):
    host: str
    port: str
    protocol: str


class Prod(BaseModel):
    host: str
    port: str
    protocol: str


class BotLaunchConfig(BaseModel):
    dev: Dev
    prod: Prod


class ServerLaunchConfig(BaseModel):
    dev: str
    prod: str


class LaunchConfigStruct(BaseModel):
    bot_launch_config: BotLaunchConfig
    server_launch_config: ServerLaunchConfig
