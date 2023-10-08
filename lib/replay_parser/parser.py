import json
import pathlib
import subprocess
import traceback

from lib.utils.singleton_factory import singleton
from lib.logger.logger import get_logger

_log = get_logger(__name__, 'ReplayParserLogger', 'logs/replay_parser.log')

if __name__ == '__main__':
    import os
    import sys
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    sys.path.insert(0, path)

from lib.exceptions.replay_parser import ReplayParserError, PathNotExists

_EXE = 'parser.exe'
_PATH = 'lib/replay_parser/bin/' + _EXE
_ARGUMENT = 'battle-results'

@singleton
class ReplayParser:
    def __init__(self) -> None:
        self.exe_path = _PATH

    def parse(self, replay_path: str) -> str:
        path = pathlib.PurePath(replay_path)
        if not pathlib.Path(replay_path).exists():
            _log.error(f'Path {replay_path} does not exist')
            raise PathNotExists(replay_path)

        replay_parser = subprocess.Popen([self.exe_path, _ARGUMENT, str(path)], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            stdout, stderr = replay_parser.communicate(timeout=5)
        except subprocess.TimeoutExpired():
            _log.error(f'Failed to parse replay {replay_path}, TIMEOUT EXCEEDED')
            raise ReplayParserError(f'Failed to parse replay {replay_path}, TIMEOUT EXCEEDED')
        except Exception():
            _log.error(f'Failed to parse replay {replay_path}, unknown error')
            _log.error(traceback.format_exc())
            raise ReplayParserError(f'Failed to parse replay {replay_path}, unknown error')

        if replay_parser.returncode != 0:
            raise ReplayParserError(stderr.decode('utf-8'))
        
        return stdout.decode('utf-8')

