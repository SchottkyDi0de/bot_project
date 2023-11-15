import os, sys
import json
import pathlib
import subprocess
import traceback

if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, path)

from lib.data_classes.replay_data import ReplayData
from lib.utils.singleton_factory import singleton
from lib.logger.logger import get_logger

_log = get_logger(__name__, 'ReplayParserLogger', 'logs/replay_parser.log')

from lib.exceptions.replay_parser import ReplayParserError, PathNotExists

_EXE = 'parser.exe'
_PATH = 'lib/replay_parser/bin/' + _EXE
_ARGUMENT = 'battle-results'

@singleton
class ReplayParser:

    @staticmethod
    def parse(replay_path: str, auto_clear: bool = True, save_json: bool = False) -> ReplayData:
        path = pathlib.PurePath(replay_path)
        if not pathlib.Path(replay_path).exists():
            _log.error(f'Path {replay_path} does not exist')
            raise PathNotExists(replay_path)

        replay_parser = subprocess.Popen([_PATH, _ARGUMENT, str(path)], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            stdout, stderr = replay_parser.communicate(timeout=5)
        except subprocess.TimeoutExpired():
            _log.error(f'Failed to parse replay {replay_path}, TIMEOUT EXCEEDED')
            raise ReplayParserError(f'Failed to parse replay {replay_path}, TIMEOUT EXCEEDED')
        except Exception():
            _log.error(f'Failed to parse replay {replay_path}, unknown error')
            _log.error(traceback.format_exc())
            raise ReplayParserError(f'Failed to parse replay {replay_path}, unknown error')
        finally:
            replay_parser.terminate()

        if replay_parser.returncode != 0:
            raise ReplayParserError(stderr.decode('utf-8'))
        
        if save_json:
            with open(f'{replay_path}.json', 'w') as f:
                f.write(stdout.decode('utf-8'))
        
        if auto_clear:
            os.remove(replay_path)

        return ReplayData.model_validate_json(stdout)

    def test(self):
        self.parse('test.wotbreplay', False, True)

print(ReplayParser().test())