import os

from pydantic import BaseModel

from pydatagen import main


class Args(BaseModel):
    schema_filename: str
    dry_run: bool = True
    set_headers: bool = False
    keyfield: str = None
    key_json: bool = False
    interval: int = 10
    iterations: int = 10


if __name__ == "__main__":
    schema_files = sorted(os.listdir("resources"))
    qty_files = len(schema_files)
    for n, file in enumerate(schema_files):
        print(f"\n\nSchema file #{n+1}/{qty_files}: {file}\n")
        args = Args(schema_filename=file)
        main(args)
