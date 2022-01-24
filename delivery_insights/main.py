import warnings
import pandas as pd
import os

from pipelines.extract.pipeline import extract
from pipelines.transform.pipeline import transform
from pipelines.load.pipeline import load
from pipelines.visualize.pipeline import visualize
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
    extract(
        repo="tsiaras/uk-road-safety-accidents-and-vehicles",
        files_list=["Accident_Information.csv", "Vehicle_Information.csv"],
        output_folder=OUTPUT_FOLDER,
    )

    print("Reading file Accident_Information.csv")
    accident_info = pd.read_csv(os.path.join(os.getcwd(), "Accident_Information.csv"))

    print("Reading file Vehicle_Information.csv")
    vehicle_info = pd.read_csv(
        os.path.join(os.getcwd(), "Vehicle_Information.csv"),
        encoding="ISO-8859-1",
    )

    # Transform
    data = accident_info.merge(
        vehicle_info, on=["Accident_Index", "Year"], how="inner"
    ).rename(columns={"Date": "Accident_date"})

    data = transform(
        data=data,
        output_folder=OUTPUT_FOLDER,
        columns=[
            "Accident_Index",
            "Year",
            "Age_Band_of_Driver",
            "Age_of_Vehicle",
            "Driver_Home_Area_Type",
            "Journey_Purpose_of_Driver",
            "Accident_Severity",
            "Accident_date",
            "Day_of_Week",
        ],
    )

    load(data=data, db_config_file=DB_CONFIG_FILE)
    visualize(data, output_folder=OUTPUT_FOLDER)


if __name__ == "__main__":
    main()
