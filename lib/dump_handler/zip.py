import os

from io import BytesIO
from os import path, walk, listdir, remove
from re import compile as _compile
from sys import argv
from typing import Callable
from zipfile import ZipFile, ZIP_DEFLATED
from filesplit.split import Split

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
    output_dir = "dumpZip"

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
    
    def split_7zip(
            self,
            filename: str, outputdir: str, size: int,
            newline: bool = False, includeheader: bool = False,
            callback: Callable = None
        ):
        splitObj = Split(inputfile=filename, outputdir=outputdir)
        splitObj.bysize(
            size=size,
            newline=newline,
            includeheader=includeheader,
            callback=callback
        )

        os.remove(path=f"{outputdir}/{splitObj.manfilename}")

        return self.get_7zip_files(splitObj)
    
    @staticmethod
    def get_7zip_files(splitObj: Split) -> tuple[list[Buffer], list[str]]:
        file_names = os.listdir(splitObj.outputdir)
        require_files = {".gitignore"}
        
        for req_file in require_files:
            file_names.remove(req_file)

        def get_buffer(filename: str) -> Buffer:
            buf = BytesIO()
            with open(f"{splitObj.outputdir}/{filename}", 'rb') as _f:
                buf.write(_f.read())
            
            return Buffer(buf)
        
        return [get_buffer(filename) for filename in file_names], file_names

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
        
        # buffer = BytesIO()
        # with open(self.zip_name, 'rb') as file:
        #     buffer.write(file.read())

        # if len(buffer.getvalue()) < _config.dump.chunk_size:
        #     files = [Buffer(buffer)]
        #     obj.files = files
        #     return files

        files, filenames = self.split_7zip(self.zip_name, self.output_dir, _config.dump.chunk_size)

        remove(self.zip_name)

        for filename in filenames:
            remove(f"{self.output_dir}/{filename}")

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
