import pickle
from types import SimpleNamespace

import yaml


class Parser:
    def __init__(self):
        pass
    
    def parse_file(self, fp: str) -> SimpleNamespace:
        with open(fp, encoding='utf-8') as f:
            d = yaml.safe_load(f)
        return self._parse(d)
    
    @staticmethod
    def object_to_file(obj: object, fp) -> None:
        with open(fp, 'wb') as f:
            pickle.dump(obj, f)

    @staticmethod
    def object_from_file(fp: str) -> SimpleNamespace:
        with open(fp, 'rb') as f:
            return pickle.load(f)
    
    def parse_dict(self, data: dict) -> SimpleNamespace:
        return self._parse(data)
        
    def _parse(self, d):
        x: SimpleNamespace = SimpleNamespace()
        _ = [setattr(x, k, self._parse(v)) if isinstance(v, dict) else setattr(x, k, v) for k, v in d.items()]    
        return x
