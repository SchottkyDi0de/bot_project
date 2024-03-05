import asyncio as asy
import os

res = {}
start_dirs = [
    "cogs",
    "lib",
    "workers",
    "api_server.py",
    "server.py",
    "main.py"
]
ignore_dirs = ["__pycache__"]


def get_dict_by_path(path: str) -> dict:
    global res

    node = res
    for i in path.split("/")[:-1]:
        node = node.setdefault(i, {})
    return node


def add_total_in_dicts(node):
    visible_length = 0
    blank = 0
    comment = 0
    for i in node:
        if not i.endswith(".py"):
            ret = add_total_in_dicts(node[i])
            visible_length += ret[0]
            blank += ret[1]
            comment += ret[2]
        else:
            visible_length += node[i]["code"]
            blank += node[i]["blank"]
            comment += node[i]["comment"]
    node["code"] = visible_length
    node["blank"] = blank
    node["comment"] = comment
    node["total"] = visible_length + blank + comment
    return visible_length, blank, comment


async def get_files(path):
    files = []
    for i in os.listdir(path):
        if i.endswith(".py"):
            files += [f"{path}/{i}"]
        elif os.path.isdir(f"{path}/{i}") and i not in ignore_dirs:
            files += await get_files(f"{path}/{i}")
    return files


async def add_files_length(files):
    for i in files:
        total_not_empy_line_in_file = 0
        total_empy_line_in_file = 0
        comment = 0
        with open(i) as f:
            for line in f:
                total_not_empy_line_in_file += not not line.strip()
                total_empy_line_in_file += not line.strip()
                comment += line.strip().startswith("#")
        dct = get_dict_by_path(i)
        key = i.split('/')[-1]
        dct[key] = {"code": dct.get(key, 0) + total_not_empy_line_in_file, "blank": total_empy_line_in_file, "comment": comment}



async def main():
    files = []

    for i in start_dirs:
        if i.endswith(".py"):
            files += [i]
        elif os.path.isdir(i) and i not in ignore_dirs:
            files += await get_files(i)

    chunked_files = [files[i:i + 20] for i in range(0, len(files), 20)]
    tasks = []

    async with asy.TaskGroup() as tg:
        for i in chunked_files:
            tasks += [tg.create_task(add_files_length(i))]
    await asy.wait(tasks)
    add_total_in_dicts(res)

    print(__import__("json").dumps(res, indent=2))

if __name__ == "__main__":
    asy.run(main())
