from io import BytesIO
from os import path, walk, listdir, remove
from re import compile as _compile
from sys import argv
from zipfile import ZipFile, ZIP_DEFLATED

try:
    from lib.settings.settings import Config
    
    _config = Config().get()
except ImportError:
    ...


class CompiledRegex:
    file = _compile(r"dump\.zip_part(\d+)")


class Buffer:
    def __init__(self, buffer: BytesIO, num: int | None = None) -> None:
        buffer.seek(0)
        self.buffer = buffer
        self.file_num = num
    
    def __str__(self):
        return f"dump.zip_part{self.file_num}"


class Zip:
    zip_name = "dump.zip"

    def _split_zip(self, buffer: BytesIO):
        chunk_size = _config.dump.chunk_size
        zips = []

        chunk_num = 1
        while True:
            chunk = buffer.read(chunk_size)
            if not chunk:
                break
            zips += [Buffer(BytesIO(chunk), chunk_num)]
            chunk_num += 1
        
        return zips

    def _create_zip(self):
        with ZipFile(self.zip_name, 'w', compression=ZIP_DEFLATED) as zip_file:
            for root, _, files in walk(_config.dump.directory):
                for file in files:
                    file_path = path.join(root, file)
                    zip_file.write(file_path, path.relpath(file_path, _config.dump.directory))
    
    def _join_archive(self, base_dir: str):
        parts = []

        for file in listdir(base_dir):
            search = CompiledRegex.file.search(file)
            if search:
                parts += [(path.join(base_dir, file), int(search.group(1)))]
        
        parts = sorted(parts, key=lambda x: x[1])

        with open("dump.zip", "wb") as output_file:
            for part in parts:
                with open(part[0], 'rb') as input_file:
                    output_file.write(input_file.read())

    def get_archive(self, obj) -> list[Buffer]:
        self._create_zip()
        
        buffer = BytesIO()
        with open(self.zip_name, 'rb') as file:
            buffer.write(file.read())

        remove(self.zip_name)

        if len(buffer.getvalue()) < _config.dump.chunk_size:
            files = [Buffer(buffer)]
            obj.files = files
            return files

        files = self._split_zip(buffer)

        obj.files = files
        return files


if __name__ == "__main__":
    try:
        base_dir = argv[1]
    except IndexError:
        raise type("ExceptedArgumentError", (Exception,), {})
    try:
        unpack_archive = not (argv[2] == "0" or argv[2].lower() == "false")
    except IndexError:
        unpack_archive = True
    
    Zip()._join_archive(base_dir)

    if unpack_archive:
        with ZipFile("dump.zip", 'r') as zip_ref:
            zip_ref.extractall("dump")
        remove("dump.zip")
