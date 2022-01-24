import pandas as pd
from analysis.charts import Chart
from utils.fct import set_daytime_bands, set_vehicule_age_bands


class Accidents:
    def __init__(self, output_folder: str):
        self.chart = Chart(output_folder)
        self.days = [
            "Sunday",
            "Saturday",
            "Friday",
            "Thursday",
            "Wednesday",
            "Tuesday",
            "Monday",
        ]
        self.daytime = [
            "night (23-5)",
            "evening (19-23)",
            "afternoon rush (15-19)",
            "office hours (10-15)",
            "morning rush (5-10)",
        ]
        self.vehicule_age = [">=15", "10-14", "5-9", "0-4"]

    def transform(self, data: pd.DataFrame):
        """

        :param data:
        :return:
        """
        data["Accident_date"] = pd.to_datetime(
            data["Accident_date"], format="%Y-%m-%d"
        )

        # slice first and second string from time column
        data["Hour"] = data["Time"].str[0:2]

        # convert new column to numeric datetype
        data["Hour"] = pd.to_numeric(data["Hour"])

        # drop null values in our new column
        data = data.dropna(subset=["Hour"])

        # cast to integer values
        data["Hour"] = data["Hour"].astype("int")

        # apply thus function to our temporary hour column
        data["Daytime"] = data["Hour"].apply(set_daytime_bands)

        data["Age_band_of_vehicule"] = data["Age_of_Vehicle"].apply(
            set_vehicule_age_bands
        )

        return data

    def draw_accidents_severity_share_chart(self, data: pd.DataFrame):
        """

        :param data:
        :return:
        """
        data = [
            data.Accident_Severity.value_counts()["Fatal"],
            data.Accident_Severity.value_counts()["Serious"],
            data.Accident_Severity.value_counts()["Slight"],
        ]

        self.chart.pie_share_chart(
            data_list=data,
            names_list=[
                "Fatal Accidents",
                "Serious Accidents",
                "Slight Accidents",
            ],
            chart_title="Accident Severity: Share in % (2005-2017)",
            filename="Accidents_severity_share.png",
        )

    def draw_total_count_per_date_line_chart(self, data: pd.DataFrame):
        """

        :param data:
        :return:
        """
        self.chart.total_count_per_date_line_chart(
            data=data,
            index_date_column="Accident_date",
            title="Accidents per Month",
            line_legend_title="Total per Month",
            xlabel_title="Date per Month",
            filename="Accidents_per_months.png",
            rule="M",
        )

    def draw_vehicules_age_bands_accidents_by_drivers_age(
        self, data: pd.DataFrame
    ):
        """

        :param data:
        :return:
        """
        counts = data.groupby(
            ["Age_band_of_vehicule", "Age_Band_of_Driver"]
        ).size()

        counts = counts.drop("Data missing", level="Age_band_of_vehicule")
        counts = counts.drop(
            "Data missing or out of range", level="Age_Band_of_Driver"
        )

        counts = counts.rename_axis(
            ["Age_band_of_vehicule", "Age_Band_of_Driver"]
        ).unstack(
            "Age_Band_of_Driver"
        )  # .rename({1: 'fatal', 2: 'serious', 3: 'slight'}, axis='columns')

        cols_to_drop = [*counts.columns, *["sum", "sum in %"]]

        # prepare dataframe with shares
        counts["sum"] = counts.sum(axis=1)
        counts = counts.join(
            counts.div(counts["sum"], axis=0), rsuffix=" in %"
        )

        counts_share = counts.drop(columns=cols_to_drop, axis=1)

        self.chart.stacked_bar_chart(
            data=counts_share,
            yaxis_values=self.vehicule_age,
            chart_title="Vehicule's age bands accidents by Driver's age",
            xlabel="Percentage",
            ylabel="Vehicule's age bands",
            legend_title="Driver's age bands",
            filename="vehicules_age_bands_accidents_by_drivers_age.png",
        )

    def draw_accidents_by_drivers_age_and_vehicles_age(
        self, data: pd.DataFrame
    ):
        """

        :param data:
        :return:
        """
        drivers = (
            data.groupby(["Age_Band_of_Driver", "Age_band_of_vehicule"])
            .size()
            .reset_index()
        )

        # drop the values that have no value
        drivers.drop(
            drivers[
                (
                    drivers["Age_Band_of_Driver"]
                    == "Data missing or out of range"
                )
                | (drivers["Age_band_of_vehicule"] == "Data missing")
            ].index,
            axis=0,
            inplace=True,
        )
        # rename the columns
        drivers.columns = [
            "Age_Band_of_Driver",
            "Age_band_of_vehicule",
            "Count",
        ]
        drivers["Percentage"] = drivers["Count"] / drivers["Count"].sum()

        drivers = drivers.sort_values(["Age_Band_of_Driver"], ascending=True)

        self.chart.grouped_bar_char(
            data=drivers,
            yaxis_variable="Age_Band_of_Driver",
            xaxis_variable="Percentage",
            hue_variable="Age_band_of_vehicule",
            chart_title="Accidents by driver's age and vehicle's age",
            xlabel="Percentage",
            ylabel="Age Band of Driver",
            filename="accidents_by_drivers_age_and_vehicles_age.png",
            data_labels_params={
                "fmt": "0.3f",
                "round_number": 3,
                "is_percentage": True,
            },
        )

    def draw_accidents_by_age_and_sex(self, data: pd.DataFrame):
        """

        :param data:
        :return:
        """
        drivers = (
            data.groupby(["Age_Band_of_Driver", "Sex_of_Driver"])
            .size()
            .reset_index()
        )

        # drop the values that have no value
        drivers.drop(
            drivers[
                (
                    drivers["Age_Band_of_Driver"]
                    == "Data missing or out of range"
                )
                | (drivers["Sex_of_Driver"] == "Not known")
                | (drivers["Sex_of_Driver"] == "Data missing or out of range")
            ].index,
            axis=0,
            inplace=True,
        )
        # rename the columns
        drivers.columns = ["Age_Band_of_Driver", "Sex_of_Driver", "Total"]

        self.chart.grouped_bar_char(
            data=drivers,
            yaxis_variable="Age_Band_of_Driver",
            xaxis_variable="Total",
            hue_variable="Sex_of_Driver",
            chart_title="Accidents by drivers age and sex",
            xlabel="Total",
            ylabel="Age Band of Driver",
            filename="accidents_by_age_and_sex.png",
            data_labels_params={"fmt": ".0f", "round_number": 0},
        )

    def draw_accidents_per_year(self, data: pd.DataFrame):
        """

        :param data:
        :return:
        """
        yearly_count = (
            data["Accident_date"]
            .dt.year.value_counts()
            .sort_index(ascending=False)
        )
        print(type(yearly_count))
        self.chart.bar_chart(
            data=yearly_count,
            graph_title="Accidents per Year",
            ylabel="Total values",
            filename="accidents_per_year.png",
        )
