import argparse
import os.path
import sys


def parse_arguments():
    """
    Parse arguments from command line

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-folder", help="Path to output folder where to store charts", type=str
    )
    parser.add_argument("--db-config-file", help="Path to database.ini file", type=str)
    args = parser.parse_args()
    output_folder = args.output_folder
    db_config_file = args.db_config_file

    try:
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        if db_config_file and not os.path.exists(db_config_file):
            if not os.path.exists(os.path.join(os.getcwd(), "../../conf/database.ini")):
                raise Exception("Please set a correct path to database ini file")
            else:
                db_config_file = os.path.join(os.getcwd(), "../../conf/database.ini")
        return {"output_folder": output_folder, "db_config_file": db_config_file}
    except Exception as e:
        print(f"Error: {e}")
        sys.exit()
