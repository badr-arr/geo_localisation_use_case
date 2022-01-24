import os.path
from zipfile import ZipFile

from kaggle.api.kaggle_api_extended import KaggleApi


class kaggle:
    def __init__(self, repo: str, files_list: []):
        self.repo = repo
        self.files_list = files_list

    def load_files(self):
        """
        Using Kaggle API load csv files from Kaggle repo

        :return:
        """
        try:
            api = KaggleApi()
            api.authenticate()
            for f in self.files_list:
                if os.path.exists(os.path.join(os.getcwd(), f)):
                    print(f"{f} exists already.")
                elif os.path.exists(os.path.join(os.getcwd(), f"{f}.zip")):
                    print(f"{f}.zip file found. Unzipping...")
                    self.unzip_file(f)
                else:
                    print(f"Loading file : {f}")
                    api.dataset_download_file(self.repo, f)
                    self.unzip_file(f)

        except Exception as e:
            print(f"Error: {e}")

    def unzip_file(self, f):
        """
        Unzip csv files loaded from Kaggle

        :param f:
        :return:
        """
        print(f"Unzipping file : {f}")
        zf = ZipFile(f"{f}.zip")
        # extracted data is saved in the same directory as notebook
        zf.extractall()
        zf.close()
