import pandas as pd
import os
import argparse
import sys


def transform_pipeline():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-folder", help="Input folder", type=str)
    parser.add_argument("--filename", help="file to transform", type=str)
    parser.add_argument("--output-folder", help="Output folder", type=str)
    parser.add_argument("--columns", nargs="*", help="columns to keep", type=str)
    args = parser.parse_args()
    input_folder = args.input_folder
    output_folder = args.output_folder
    columns = args.columns
    filename = args.filename

    try:
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        if not os.path.exists(os.path.join(input_folder, filename)):
            raise Exception(f"{filename} does not exist.")
        sample = pd.read_csv(os.path.join(input_folder, filename), nrows=1)
        wrong_cols = [c for c in columns if c not in list(sample.colums)]
        if len(wrong_cols) > 0:
            raise Exception(f"Columns {wrong_cols} are not in dataframe.")
        data = pd.read_csv(os.path.join(input_folder, filename))
        transform(data=data, output_folder=output_folder, columns=columns)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit()


def transform(data: pd.DataFrame, output_folder: str, columns: list):
    """

    :param data:
    :param output_folder:
    :param columns:
    :return:
    """
    new_data = data[columns]

    new_data.columns = [c.lower() for c in new_data.columns]

    new_data.to_csv(os.path.join(output_folder, "transformed_data"), index=False, sep=";")

    return new_data
