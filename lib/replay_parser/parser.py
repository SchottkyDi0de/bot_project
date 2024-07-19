import os
import pathlib
import subprocess
import traceback

from lib.data_classes.replay_data import ReplayData
from lib.exceptions.replay_parser import PathNotExists, ReplayParserError
from lib.logger.logger import get_logger
from lib.utils.singleton_factory import singleton

_log = get_logger(__file__, 'ReplayParserLogger', 'logs/replay_parser.log')

_EXE = 'parser.exe' if os.name == 'nt' else 'parser'
_PATH = 'lib/replay_parser/bin/' + _EXE
_ARGUMENT = 'battle-results'

@singleton
class ReplayParser:

    @staticmethod
    def parse(replay_path: str, auto_clear: bool = True, save_json: bool = False) -> ReplayData:
        """
        Parse a replay file and return the parsed data.
        
        Args:
            replay_path (str): The path to the replay file.
            auto_clear (bool, optional): Whether to automatically delete the replay file after parsing. Defaults to True.
            save_json (bool, optional): Whether to save the parsed data as a JSON file. Defaults to False.
        
        Returns:
            ReplayData: The parsed replay data.
        
        Raises:
            PathNotExists: If the specified replay file does not exist.
            ReplayParserError: If an error occurs while parsing the replay file.
        
        """
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
        
        # print(b'"winner_team_number": null' in stdout) # DEBUG

        return ReplayData.model_validate_json(stdout)

    def test(self):
        self.parse('test.wotbreplay', False, True)