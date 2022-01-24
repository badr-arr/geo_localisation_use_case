import os
import sys
from pathlib import Path
import argparse
from loader.kaggle import kaggle
import shutil


def extract(repo: str, files_list: list, output_folder: str):
    """

    :param repo:
    :param files_list:
    :param output_folder:
    :return:
    """
    kg = kaggle(
        repo=repo,
        files_list=files_list,
    )
    kg.load_files()

    for f in files_list:
        shutil.move(
            os.path.join(os.getcwd(), f),
            os.path.join(output_folder, f),
        )


def extract_pipeline():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="repo name", type=str)
    parser.add_argument("--files-list", nargs="*", help="files list", type=str)
    parser.add_argument("--output-folder", help="Output folder", type=str)
    args = parser.parse_args()
    output_folder = args.output_folder
    repo = args.repo
    files_list = args.files_list

    try:
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        extract(repo=repo, files_list=files_list, output_folder=output_folder)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit()
