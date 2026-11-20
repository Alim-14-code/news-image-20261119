import os
import shutil

SRC = "entry.png"
DST_NAME = "entry.png"


def main():
    out_dir = os.environ["MAKEFUN_OUTPUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(out_dir, DST_NAME))


if __name__ == "__main__":
    main()
