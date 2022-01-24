import pandas as pd

from utils.fct import set_daytime_bands, set_vehicule_age_bands


class Accidents:
    def get_accidents_count_by_column(
        self, data: pd.DataFrame, column: str, min_value: int = 0, filter_conditions=None
    ):
        filtered_data = self.filter_data(
            data=data, column=column, filter_conditions=filter_conditions
        )

        grouped_data = (
            filtered_data.groupby(column)
            .size()
            .reset_index(name="counts")
            .sort_values(by="counts", ascending=False)
        )
        grouped_data = grouped_data[grouped_data.counts > min_value]
        labels = grouped_data.apply(
            lambda x: str(x[0]) + "\n (" + str(x[1]) + ")", axis=1
        )
        sizes = grouped_data["counts"].values.tolist()
        return grouped_data, labels, sizes

    def get_list_accidents_values_by_column(
        self, data: pd.DataFrame, column: str, filter_conditions=None
    ):
        """
        Count values of accidents data by selected column

        :param data:
        :param column:
        :param filter_conditions:
        :return:
        """
        filtered_data = self.filter_data(
            data=data, column=column, filter_conditions=filter_conditions
        )

        cols = filtered_data[column].value_counts().index.values

        filtered_data = [filtered_data[column].value_counts()[c] for c in cols]

        return filtered_data, cols

    @staticmethod
    def transform(data: pd.DataFrame):
        """
        Transform accidents data

        :param data:
        :return:
        """
        data["Accident_date"] = pd.to_datetime(data["Accident_date"], format="%Y-%m-%d")

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

    @staticmethod
    def filter_data(data, column: str, filter_conditions=None):
        """
        Filter accidents data by dropping unused values

        :param data:
        :param column:
        :param filter_conditions:
        :return:
        """
        if filter_conditions:
            if isinstance(filter_conditions, list):
                data.drop(
                    data[data[column].isin(filter_conditions)].index,
                    axis=0,
                    inplace=True,
                )
            elif isinstance(filter_conditions, str):
                data.drop(
                    data[data[column] == filter_conditions].index,
                    axis=0,
                    inplace=True,
                )

        return data

    @staticmethod
    def get_accidents_share_count(
        data: pd.DataFrame, cols: [], filter_conditions: {} = None
    ):
        """
        Get accident share count by columns

        :param data:
        :param cols:
        :param filter_conditions:
        :return:
        """
        counts = data.groupby(cols).size()

        if filter_conditions and len(filter_conditions.keys()) > 0:
            for key in filter_conditions.keys():
                if key in counts.reset_index().columns and isinstance(
                    filter_conditions[key], list
                ):
                    counts = counts.drop(filter_conditions[key], level=key)

        counts = counts.rename_axis(cols).unstack(cols[1])

        cols_to_drop = [*counts.columns, *["sum", "sum in %"]]

        # prepare dataframe with shares
        counts["sum"] = counts.sum(axis=1)
        counts = counts.join(counts.div(counts["sum"], axis=0), rsuffix=" in %")

        counts_share = counts.drop(columns=cols_to_drop, axis=1)

        return counts_share

    @staticmethod
    def get_accidents_counts_using_two_columns(
        data: pd.DataFrame, cols: [], filter_conditions: {}, new_cols_name: []
    ):
        """
        Aggregate accidents data counts using two columns

        :param data:
        :param cols:
        :param filter_conditions:
        :param new_cols_name:
        :return:
        """
        counts = data.groupby(cols).size().reset_index()

        # drop the values that have no value
        if len(filter_conditions.keys()) > 0:
            for col in filter_conditions.keys():
                if col in counts.columns:
                    counts.drop(
                        counts[counts[col].isin(filter_conditions[col])].index,
                        axis=0,
                        inplace=True,
                    )
        # rename the columns
        counts.columns = new_cols_name

        return counts

    @staticmethod
    def get_accidents_per_year(data: pd.DataFrame):
        """
        Get accidents counts per year

        :param data:
        :return:
        """
        yearly_count = (
            data["Accident_date"].dt.year.value_counts().sort_index(ascending=False)
        )
        return yearly_count

    @staticmethod
    def get_accidents_per_hour(data: pd.DataFrame):
        """
        Get accidents count per hour

        :param data:
        :return:
        """
        hourly_count = data["Hour"].value_counts().sort_index(ascending=False)
        return hourly_count

    @staticmethod
    def get_accidents_per_daytime(data: pd.DataFrame):
        """
        Get accidents count per daytime

        :param data:
        :return:
        """
        daytime_count = data["Daytime"].value_counts().sort_index(ascending=False)
        return daytime_count

    @staticmethod
    def get_accidents_per_weekday_and_year(data: pd.DataFrame, days: []):
        """
        Aggregate accidents by weekday and year

        :param data:
        :param days:
        :return:
        """
        weekday = data["Accident_date"].dt.day_name()
        year = data["Accident_date"].dt.year

        accidents_per_weekday_and_year = data.groupby([year, weekday]).size()
        accidents_per_weekday_and_year = (
            accidents_per_weekday_and_year.rename_axis(["Year", "Weekday"])
            .unstack("Weekday")
            .reindex(columns=days)
        )
        return accidents_per_weekday_and_year
