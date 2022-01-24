import os
import sys
import pandas as pd
from delivery_insights.loader.db import Database
import argparse


def load(data: pd.DataFrame, db_config_file: str):
    """

    :param data:
    :param db_config_file:
    :return:
    """
    db = Database(db_config_file)
    create_table_query = """
                CREATE TABLE IF NOT EXISTS accidents (
                    accident_index TEXT PRIMARY KEY,
                    year INT,
                    age_band_of_briver TEXT,
                    age_of_vehicle INT,
                    driver_home_area_type TEXT,
                    journey_purpose_of_driver TEXT,
                    accident_Severity TEXT,
                    accident_date DATE,
                    day_of_Week TEXT
                )"""

    db.execute_query(query=create_table_query)

    print("Insert data into database")
    db.insert_df_into_table(data.head(5), "accidents")


def load_pipeline():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-folder", help="input folder", type=str)
    parser.add_argument("--filename", help="filename", type=str)
    parser.add_argument("--db-config-file", help="Path to db config file", type=str)
    args = parser.parse_args()
    input_folder = args.input_folder
    filename = args.filename
    db_config_file = args.db_config_file

    try:
        if not os.path.exists(os.path.join(input_folder, filename)):
            raise Exception(f"{filename} does not exist.")
        if not os.path.exists(db_config_file):
            raise Exception("Wrong path for database.ini file")
        data = pd.read_csv(os.path.join(input_folder, filename))
        load(data=data, db_config_file=db_config_file)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit()
