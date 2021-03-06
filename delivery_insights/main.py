import warnings
import pandas as pd
import os
from delivery_insights.models.accidents import Accidents
from delivery_insights.pipelines.extract.pipeline import extract
from delivery_insights.pipelines.transform.pipeline import transform
from delivery_insights.pipelines.load.pipeline import load
from delivery_insights.pipelines.visualize.pipeline import visualize
from delivery_insights.utils.config import parse_arguments

warnings.filterwarnings("ignore")

config = parse_arguments()
print(config)
OUTPUT_FOLDER = config["output_folder"]
DB_CONFIG_FILE = config["db_config_file"]


def main() -> None:
    """
    Main function
    :return:
    """
    print(OUTPUT_FOLDER)
    extract(
        repo="tsiaras/uk-road-safety-accidents-and-vehicles",
        files_list=["Accident_Information.csv", "Vehicle_Information.csv"],
        output_folder=OUTPUT_FOLDER,
    )

    print("Reading file Accident_Information.csv")
    accident_info = pd.read_csv(os.path.join(OUTPUT_FOLDER, "Accident_Information.csv"))

    print("Reading file Vehicle_Information.csv")
    vehicle_info = pd.read_csv(
        os.path.join(OUTPUT_FOLDER, "Vehicle_Information.csv"),
        encoding="ISO-8859-1",
    )

    # Transform
    data = accident_info.merge(
        vehicle_info, on=["Accident_Index", "Year"], how="inner"
    ).rename(columns={"Date": "Accident_date"})

    data = Accidents().transform(data=data)
    new_data = transform(
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
    print(new_data.head())
    load(data=data, db_config_file=DB_CONFIG_FILE)
    visualize(data, output_folder=OUTPUT_FOLDER)


if __name__ == "__main__":
    main()
