import demjson
import os
import pathlib

# only for INTERNAL use...

ROOTDIR = pathlib.Path(os.environ['HOME'])
BASEDIR = ROOTDIR / "assettocorsa" / "content" / "cars"
TARGETDIR = ROOTDIR / "acracers" / "djapp" / "all_cars"
TARGETDIR.mkdir(parents=True, exist_ok=True)


def create_jsons():
    for directory in BASEDIR.glob('**'):
        for item in directory.iterdir():
            if item.name == 'ui_car.json':
                itemfile = TARGETDIR / item.parent.parent.name
                with itemfile.open('w', encoding="utf-8") as f:
                    with item.open(encoding="utf-8", errors=None) as inp:
                        try:
                            f.write(inp.read())
                        except Exception:
                            print("ERROR READING {0}".format(inp.name))


def parse_jsons():
    for files in TARGETDIR.glob('**'):
        for item in files.iterdir():
            with item.open() as f:
                raw = f.read()
                try:
                    content = demjson.decode(raw, return_errors=True)
                    print(item.name, content.object['name'])
                except Exception:
                    print("ERROR LOADING {0}".format(item.name))


parse_jsons()
