
if __name__ == '__main__':
    import os
    import sys
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    sys.path.insert(0, path)

from lib.replay_parser.parser import ReplayParser

parser = ReplayParser()

test_replay = 'c:/VS Code Projects/Python/bot_project_git/tests/data/test.wotbreplay'
data = parser.parse(test_replay)
print(data)