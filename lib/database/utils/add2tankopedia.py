#На вход принимаются id название нация уроень is_premium(True/False or 1/0) тип(ст, тт т.д.)
import sys

import elara


class Main:
    def __init__(self) -> None:
        self.arg_parse_result: dict

        self.main()
    
    def _get_path2db(self) -> str:
        path = __file__.split('\\')
        return '\\'.join(path[:-4]) + "\\database\\custom_tankopedia.eldb"

    def _starts_with_key_word(self, arg: str, arg_names: list) -> str | None:
        for i in arg_names:
            if arg.startswith(i):
                return i

    def _get_kw_args(self, argv: list[str], data: dict, arg_names: list[str]) -> None:
        for i in argv:
            arg_name = self._starts_with_key_word(i, arg_names)
            print(f"{arg_name=}")
            if arg_name:
                data[arg_name] = i[len(arg_name) + 1:]
                arg_names.remove(arg_name)
        
        for i in data:
            for j in argv:
                if j.startswith(i) and j.endswith(data[i]):
                    argv.remove(j)
                

    def _argv_parse(self) -> None:
        argv = [i.strip('"') for i in sys.argv[1:]]
        dct = {}
        arg_names = ["tank_id", "name", "nation", "tier", "is_premium", "type"]
        self._get_kw_args(argv, dct, arg_names)

        for key, value in zip(arg_names, argv):
            arg_names.remove(key)
            dct[key] = value
        
        self.arg_parse_result = dct
        self.excepted_args = arg_names
    
    def _get_excepted_data(self) -> None:
        for i in self.excepted_args:
            data = input(f"{i}: ")
            self.arg_parse_result[i] = data
    
    def _normalized_data(self) -> None:
        if not self.arg_parse_result["tank_id"].isdigit():
            raise ValueError("ID must be an integer")
        if not (self.arg_parse_result["tier"].isdigit() and 1 <= int(self.arg_parse_result["tier"]) <= 10):
            raise ValueError("Invalid tier value")
        
        self.arg_parse_result["tank_id"] = int(self.arg_parse_result["tank_id"])
        self.arg_parse_result["is_premium"] = self.arg_parse_result["is_premium"].capitalize()
        self.arg_parse_result["tier"] = int(self.arg_parse_result["tier"])

        if self.arg_parse_result["type"] not in ["mediumTank", "lightTank", "heavyTank", "AT-SPG"]:
            raise ValueError("Invalid tank type")
        if self.arg_parse_result["is_premium"].isdigit():
            self.arg_parse_result["is_premium"] = self.arg_parse_result["is_premium"] != '0'
        elif self.arg_parse_result["is_premium"] in ['True', 'False']:
            self.arg_parse_result["is_premium"] = self.arg_parse_result["is_premium"] == "True"
        else:
            raise ValueError("Invalid premium value")

    def _write_to_db(self, data: dict) -> None:
        db = elara.exe(self._get_path2db())
        db.commit()
        if not db.hkeys("data"):
            db["data"] = {}

        db["data"][str(data["tank_id"])] = data
        db.commit()

    def main(self) -> None:
        self._argv_parse()
        self._get_excepted_data()
        self._normalized_data()
        self._write_to_db(self.arg_parse_result)
        print("done")


if __name__ == '__main__':
    Main()
