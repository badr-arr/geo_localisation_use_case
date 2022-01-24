import os
import warnings

import pandas as pd
from analysis.charts import Chart
from analysis.insights import visualize
from loader.db import Database
from loader.kaggle import kaggle
from models.accidents import Accidents

warnings.filterwarnings("ignore")

ANALYSIS_FOLDER = os.path.join(os.getcwd(), "plots")
DB_CONFIG_FILE = os.path.join(os.getcwd(), "../conf/database.ini")


def main():
    """

    :return:
    """
    kg = kaggle(
        repo="tsiaras/uk-road-safety-accidents-and-vehicles",
        files_list=["Accident_Information.csv", "Vehicle_Information.csv"],
    )
    kg.load_files()

    db = Database(DB_CONFIG_FILE)
    chart = Chart(ANALYSIS_FOLDER)

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

    print("Reading file Accident_Information.csv")
    accident_info = pd.read_csv(os.path.join(os.getcwd(), "Accident_Information.csv"))

    print("Reading file Vehicle_Information.csv")
    vehicle_info = pd.read_csv(
        os.path.join(os.getcwd(), "Vehicle_Information.csv"),
        encoding="ISO-8859-1",
    )

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

    print("Insert data into database")
    db.insert_df_into_table(new_data.head(5), "accidents")

    query = """
    select * from accidents;
    """

    db.select_query(query=query)

    accidents = Accidents()
    data = accidents.transform(all_data)

    if not os.path.exists(ANALYSIS_FOLDER):
        os.mkdir(ANALYSIS_FOLDER)

    visualize(data, accidents, chart)


if __name__ == "__main__":
    main()
