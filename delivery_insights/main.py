import os
import warnings

import pandas as pd
from analysis.charts import Chart
from analysis.insights import visualize
from loader.db import Database
from loader.kaggle import kaggle
from models.accidents import Accidents
from utils.config import parse_arguments

warnings.filterwarnings("ignore")

config = parse_arguments()
OUTPUT_FOLDER = config.output_folder
DB_CONFIG_FILE = config.db_config_file


def main() -> None:
    """
    Main function
    :return:
    """
    # Create table in database
    db = Database(DB_CONFIG_FILE)
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

    # Load data
    kg = kaggle(
        repo="tsiaras/uk-road-safety-accidents-and-vehicles",
        files_list=["Accident_Information.csv", "Vehicle_Information.csv"],
    )
    kg.load_files()

    print("Reading file Accident_Information.csv")
    accident_info = pd.read_csv(os.path.join(os.getcwd(), "Accident_Information.csv"))

    print("Reading file Vehicle_Information.csv")
    vehicle_info = pd.read_csv(
        os.path.join(os.getcwd(), "Vehicle_Information.csv"),
        encoding="ISO-8859-1",
    )

    # Transform
    all_data = accident_info.merge(
        vehicle_info, on=["Accident_Index", "Year"], how="inner"
    ).rename(columns={"Date": "Accident_date"})

    new_data = all_data[
        [
            "Accident_Index",
            "Year",
            "Age_Band_of_Driver",
            "Age_of_Vehicle",
            "Driver_Home_Area_Type",
            "Journey_Purpose_of_Driver",
            "Accident_Severity",
            "Accident_date",
            "Day_of_Week",
        ]
    ]

    new_data.columns = [c.lower() for c in new_data.columns]

    # Load into database
    print("Insert data into database")
    db.insert_df_into_table(new_data.head(5), "accidents")

    # Visualize data
    accidents = Accidents()
    chart = Chart(OUTPUT_FOLDER)
    data = accidents.transform(all_data)

    visualize(data, accidents, chart)


if __name__ == "__main__":
    main()
