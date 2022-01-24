import os
import warnings

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import squarify
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
    accident_info = pd.read_csv(
        os.path.join(os.getcwd(), "Accident_Information.csv")
    )

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

    # Analysis
    if not os.path.exists(ANALYSIS_FOLDER):
        os.mkdir(ANALYSIS_FOLDER)

    accidents = Accidents(ANALYSIS_FOLDER)
    data = accidents.transform(all_data)

    accidents.draw_accidents_severity_share_chart(data)
    accidents.draw_total_count_per_date_line_chart(data)
    accidents.draw_accidents_by_age_and_sex(data)
    accidents.draw_accidents_per_year(data)

    # accidents_per_year(all_data)
    # accidents_per_weekdays(all_data, days)
    # accidents_per_weekday_and_year(all_data, days)
    # fatalities_over_years(all_data)
    # fatalities_variation_over_years(all_data)
    # accidents_by_time(all_data)
    # accidents_by_daytime(all_data, daytime)
    # accidents_severity_by_daytime(all_data, daytime)
    # accidents_by_age_and_sex(all_data)
    # accidents_by_manoeuver(all_data)

    # Q3:
    accidents.draw_vehicules_age_bands_accidents_by_drivers_age(data)

    ###################################
    accidents.draw_accidents_by_drivers_age_and_vehicles_age(data)


"""
# Has the number of accidents increased or decreased over the last few years?
def accidents_per_month(data: pd.DataFrame):
    # prepare plot
    sns.set_style("white")
    fig, ax = plt.subplots(figsize=(15, 6))

    # plot
    # Downsampling series to 1 month data and get size
    data.set_index("Date").resample("M").size().plot(
        label="Total per Month", color="grey", ax=ax
    )

    ax.set_title("Accidents per Month", fontsize=14, fontweight="bold")
    ax.set(ylabel="Total Count\n", xlabel="Date per Month")
    ax.legend(bbox_to_anchor=(1.1, 1.1), frameon=False)

    # remove all spines
    sns.despine(ax=ax, top=True, right=True, left=False, bottom=False)

    plt.savefig(os.path.join(ANALYSIS_FOLDER, "Accidents_per_months.png"))


def accidents_per_year(data: pd.DataFrame):
    yearly_count = (
        data["Date"].dt.year.value_counts().sort_index(ascending=False)
    )
    colors = [
        "red" if c == max(yearly_count.values) else "grey"
        for c in yearly_count.values
    ]

    # prepare plot
    sns.set_style("white")
    fig, ax = plt.subplots(figsize=(12, 5))
    # plot
    ax.bar(yearly_count.index, yearly_count.values, color=colors)
    ax.plot(yearly_count, linestyle="dashed", color="black")
    ax.set_title("\nAccidents per Year\n", fontsize=14, fontweight="bold")
    ax.set(ylabel="\nTotal Counts")

    # remove all spines
    sns.despine(ax=ax, top=True, right=True, left=True, bottom=True)
    plt.savefig(os.path.join(ANALYSIS_FOLDER, "Accidents_per_year.png"))


# A revoir
def accidents_per_weekdays(data: pd.DataFrame, days: []):
    weekday_counts = pd.DataFrame(
        data.set_index("Date")
        .resample("1d")["Accident_Index"]
        .size()
        .reset_index()
    )
    weekday_counts.columns = ["Date", "Count"]
    # weekday_counts

    weekday = weekday_counts["Date"].dt.day_name()
    # weekday

    weekday_averages = pd.DataFrame(
        weekday_counts.groupby(weekday)["Count"].mean().reset_index()
    )
    weekday_averages.columns = ["Weekday", "Average_Accidents"]
    weekday_averages.set_index("Weekday", inplace=True)

    # prepare plot
    sns.set_style("white")
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [
        "lightsteelblue",
        "lightsteelblue",
        "navy",
        "lightsteelblue",
        "lightsteelblue",
        "lightsteelblue",
        "lightsteelblue",
    ]

    # plot
    weekday_averages.reindex(days).plot(kind="barh", ax=ax, color=colors)
    ax.set_title(
        "\nAverage Accidents per Weekday\n", fontsize=14, fontweight="bold"
    )
    ax.set(xlabel="\nAverage Number", ylabel="")
    ax.legend("")

    # remove all spines
    sns.despine(ax=ax, top=True, right=True, left=False, bottom=True)
    plt.savefig(os.path.join(ANALYSIS_FOLDER, "Accidents_per_weekdays.png"))


def accidents_per_weekday_and_year(data: pd.DataFrame, days: []):
    weekday = data["Date"].dt.day_name()
    year = data["Date"].dt.year

    accident_table = data.groupby([year, weekday]).size()
    accident_table = (
        accident_table.rename_axis(["Year", "Weekday"])
        .unstack("Weekday")
        .reindex(columns=days)
    )

    plt.figure(figsize=(10, 6))
    sns.heatmap(accident_table, cmap="Greys")
    plt.title(
        "\nAccidents by Years and Weekdays\n", fontsize=14, fontweight="bold"
    )
    plt.xlabel("")
    plt.ylabel("")
    plt.savefig(
        os.path.join(ANALYSIS_FOLDER, "accidents_per_weekday_and_year.png")
    )


# Weather related accidents


def accident_severity(data: pd.DataFrame):
    # assign the data
    fatal = data.Accident_Severity.value_counts()["Fatal"]
    serious = data.Accident_Severity.value_counts()["Serious"]
    slight = data.Accident_Severity.value_counts()["Slight"]

    names = ["Fatal Accidents", "Serious Accidents", "Slight Accidents"]
    size = [fatal, serious, slight]
    # explode = (0.2, 0, 0)
    theme = plt.get_cmap("Set3")
    colors = [theme(1.0 * i / 3) for i in range(3)]
    # create a pie chart
    plt.pie(
        x=size,
        labels=names,
        colors=colors,
        autopct="%1.2f%%",
        pctdistance=0.6,
        textprops=dict(fontweight="bold"),
        wedgeprops={"linewidth": 7, "edgecolor": "white"},
    )

    # create circle for the center of the plot to make the pie look like a donut
    # my_circle = plt.Circle((0, 0), 0.6, color='white')

    # plot the donut chart
    fig = plt.gcf()
    fig.set_size_inches(8, 8)
    plt.title(
        "\nAccident Severity: Share in % (2005-2017)",
        fontsize=14,
        fontweight="bold",
    )
    plt.savefig(os.path.join(ANALYSIS_FOLDER, "accident_severity.png"))


def fatalities_over_years(data: pd.DataFrame):
    # set the criterium to slice the fatalaties
    criteria = data["Accident_Severity"] == "Fatal"
    # create a new dataframe
    weekly_fatalities = (
        data.loc[criteria].set_index("Date").sort_index().resample("W").size()
    )

    # prepare plot
    sns.set_style("white")
    fig, ax = plt.subplots(figsize=(14, 6))

    # plot
    weekly_fatalities.plot(
        label="Total Fatalities per Month", color="grey", ax=ax
    )
    plt.fill_between(
        x=weekly_fatalities.index,
        y1=weekly_fatalities.values,
        color="lightgrey",
        alpha=0.3,
    )

    ax.set_title("\nFatalities", fontsize=14, fontweight="bold")
    ax.set(ylabel="\nTotal Count", xlabel="")
    ax.legend(bbox_to_anchor=(1.2, 1.1), frameon=False)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])

    # remove all spines
    sns.despine(ax=ax, top=True, right=True, left=True, bottom=True)
    plt.savefig(os.path.join(ANALYSIS_FOLDER, "fatalities_over_years.png"))


def fatalities_variation_over_years(data: pd.DataFrame):
    sub_df = data[["Date", "Accident_Index", "Accident_Severity"]]

    # pull out the year
    year = sub_df["Date"].dt.year
    week = sub_df["Date"].dt.week

    # groupby year and severities
    count_of_fatalities = (
        sub_df.set_index("Date")
        .groupby([pd.Grouper(freq="W"), "Accident_Severity"])
        .size()
    )

    # build a nice table
    fatalities_table = (
        count_of_fatalities.rename_axis(["Week", "Accident_Severity"])
        .unstack("Accident_Severity")
        .rename({1: "fatal", 2: "serious", 3: "slight"}, axis="columns")
    )

    fatalities_table["sum"] = fatalities_table.sum(axis=1)
    fatalities_table = fatalities_table.join(
        fatalities_table.div(fatalities_table["sum"], axis=0),
        rsuffix="_percentage",
    )

    # prepare data
    sub_df = fatalities_table[
        ["Fatal_percentage", "Serious_percentage", "Slight_percentage"]
    ]

    # prepare plot
    sns.set_style("white")
    fig, ax = plt.subplots(figsize=(14, 6))
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])

    colors = ["red", "orange", "green"]

    # plot
    sub_df.plot(color=colors, ax=ax)
    ax.set_title(
        "\nProportion of Accidents Severity\n", fontsize=14, fontweight="bold"
    )
    ax.set(ylabel="Share on all Accidents\n", xlabel="")
    ax.legend(
        labels=["Fatal Accidents", "Serious Accidents", "Slight Accidents"],
        bbox_to_anchor=(1, 1.1),
        frameon=False,
    )

    # remove all spines
    sns.despine(top=True, right=True, left=True, bottom=False)
    plt.savefig(
        os.path.join(ANALYSIS_FOLDER, "fatalities_variation_over_years.png")
    )


def accidents_by_time(data: pd.DataFrame):
    # prepare plot
    sns.set_style("white")
    fig, ax = plt.subplots(figsize=(10, 6))

    # plot
    data.Hour.hist(bins=24, ax=ax, color="lightgrey", grid=False)
    ax.set_title(
        "\nAccidents depending by Time\n", fontsize=14, fontweight="bold"
    )
    ax.set(xlabel="Hour of the Day", ylabel="Total Count of Accidents")

    # remove all spines
    sns.despine(top=True, right=True, left=True, bottom=True)
    plt.savefig(os.path.join(ANALYSIS_FOLDER, "accidents_by_time.png"))


def accidents_by_daytime(data: pd.DataFrame, daytime: []):
    # prepare dataframe
    df_sub = data.groupby("Daytime").size().reindex(daytime)

    # prepare barplot
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [
        "lightsteelblue",
        "lightsteelblue",
        "navy",
        "lightsteelblue",
        "lightsteelblue",
    ]

    # plot
    df_sub.plot(kind="barh", ax=ax, color=colors)
    ax.set_title(
        "\nAccidents depending by Daytime\n", fontsize=14, fontweight="bold"
    )
    ax.set(xlabel="\nTotal Count of Accidents", ylabel="")

    # remove all spines
    sns.despine(top=True, right=True, left=True, bottom=True)
    plt.savefig(os.path.join(ANALYSIS_FOLDER, "accidents_by_daytime.png"))


def accidents_severity_by_daytime(data: pd.DataFrame, daytime: []):
    # prepare dataframe with simple counts
    counts = data.groupby(["Daytime", "Accident_Severity"]).size()

    counts = (
        counts.rename_axis(["Daytime", "Accident_Severity"])
        .unstack("Accident_Severity")
        .rename({1: "fatal", 2: "serious", 3: "slight"}, axis="columns")
    )

    # prepare dataframe with shares
    counts["sum"] = counts.sum(axis=1)
    counts = counts.join(counts.div(counts["sum"], axis=0), rsuffix=" in %")

    counts_share = counts.drop(
        columns=["Fatal", "Serious", "Slight", "sum", "sum in %"], axis=1
    )

    # prepare barplot
    fig, ax = plt.subplots(figsize=(10, 5))

    # plot
    counts_share.reindex(daytime).plot(
        kind="barh", ax=ax, stacked=True, cmap="cividis"
    )
    ax.set_title(
        "\nAccident Severity by Daytime\n", fontsize=14, fontweight="bold"
    )
    ax.set(xlabel="Percentage", ylabel="")
    ax.legend(bbox_to_anchor=(1.25, 0.98), frameon=False)

    for p in ax.containers:
        labels = [
            f"{round((h*100), 2)}%"
            if round(h := v.get_width(), 3) != 0
            else ""
            for v in p
        ]
        ax.bar_label(
            p, labels=labels, label_type="center", size=7, color="white"
        )

    # remove all spines
    sns.despine(top=True, right=True, left=True, bottom=True)
    plt.savefig(
        os.path.join(ANALYSIS_FOLDER, "accidents_severity_by_daytime.png")
    )


def accidents_by_age_bands_and_vehicule_age_v1(
    data: pd.DataFrame, vehicule_age: []
):
    # prepare dataframe with simple counts
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
    counts = counts.join(counts.div(counts["sum"], axis=0), rsuffix=" in %")

    counts_share = counts.drop(columns=cols_to_drop, axis=1)

    # prepare barplot
    fig, ax = plt.subplots(figsize=(20, 10))

    # plot
    counts_share.reindex(vehicule_age).plot(
        kind="barh", ax=ax, stacked=True, cmap="Set3"
    )
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.9, box.height])
    ax.set_title("\nAccident \n", fontsize=14, fontweight="bold")
    ax.set(xlabel="Percentage", ylabel="Vehicule age band")
    ax.legend(
        loc="center left", bbox_to_anchor=(1, 0.5), title="Driver's age band"
    )

    for i, p in enumerate(ax.containers):
        labels = [
            f"{round((h * 100), 2)}%"
            if round(h := v.get_width(), 3) != 0
            else ""
            for v in p
        ]
        ax.bar_label(
            p,
            labels=labels,
            label_type="center",
            color="black",
            size=12,
            rotation="vertical",
        )

    # remove all spines
    sns.despine(top=True, right=True, left=True, bottom=True)
    plt.savefig(
        os.path.join(
            ANALYSIS_FOLDER, "accidents_by_age_bands_and_vehicule_age_v1.png"
        )
    )


def accidents_by_age_and_sex(data: pd.DataFrame):
    # create a new dataframe
    drivers = (
        data.groupby(["Age_Band_of_Driver", "Sex_of_Driver"])
        .size()
        .reset_index()
    )

    # drop the values that have no value
    drivers.drop(
        drivers[
            (drivers["Age_Band_of_Driver"] == "Data missing or out of range")
            | (drivers["Sex_of_Driver"] == "Not known")
            | (drivers["Sex_of_Driver"] == "Data missing or out of range")
        ].index,
        axis=0,
        inplace=True,
    )
    # rename the columns
    drivers.columns = ["Age_Band_of_Driver", "Sex_of_Driver", "Count"]

    # seaborn barplot
    fig, ax = plt.subplots(figsize=(14, 7))
    sns.barplot(
        y="Age_Band_of_Driver",
        x="Count",
        hue="Sex_of_Driver",
        data=drivers,
        palette="Set3",
    )
    ax.set_title(
        "\nAccidents Cars' Drivers by Age and Sex\n",
        fontsize=14,
        fontweight="bold",
    )
    ax.set(xlabel="Count", ylabel="Age Band of Driver")
    ax.legend(bbox_to_anchor=(1.1, 1.0), borderaxespad=0.0, frameon=False)

    # remove all spines
    sns.despine(top=True, right=True, left=True, bottom=True)
    plt.savefig(os.path.join(ANALYSIS_FOLDER, "accidents_by_age_and_sex.png"))


def accidents_by_age_bands_and_vehicule_age_v2(data: pd.DataFrame):
    # create a new dataframe
    drivers = (
        data.groupby(["Age_Band_of_Driver", "Age_band_of_vehicule"])
        .size()
        .reset_index()
    )

    # drop the values that have no value
    drivers.drop(
        drivers[
            (drivers["Age_Band_of_Driver"] == "Data missing or out of range")
            | (drivers["Age_band_of_vehicule"] == "Data missing")
        ].index,
        axis=0,
        inplace=True,
    )
    # rename the columns
    drivers.columns = ["Age_Band_of_Driver", "Age_band_of_vehicule", "Count"]
    drivers["Percentage"] = drivers["Count"] / drivers["Count"].sum()

    drivers = drivers.sort_values(["Age_Band_of_Driver"], ascending=True)

    # seaborn barplot
    fig, ax = plt.subplots(figsize=(16, 9))
    sns.barplot(
        y="Age_Band_of_Driver",
        x="Percentage",
        hue="Age_band_of_vehicule",
        data=drivers,
        palette="Set3",
    )
    ax.set_title(
        "\nAccidents' by driver's age and vehicule's age\n",
        fontsize=13,
        fontweight="bold",
    )
    ax.set(xlabel="Percentage", ylabel="Age Band of Driver")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(
        bbox_to_anchor=(1.1, 0.9),
        borderaxespad=0.0,
        frameon=False,
        fontsize=10,
    )

    for p in ax.containers:
        labels = [
            f"{h:0.3f}%" if round((h := v.get_width()), 3) != 0.000 else ""
            for v in p
        ]
        ax.bar_label(p, labels=labels, label_type="edge", size=9)

    # remove all spines
    sns.despine(top=True, right=True, left=True, bottom=True)
    plt.savefig(
        os.path.join(ANALYSIS_FOLDER, "accidents_by_age_and_sex_v2.png")
    )


def accidents_by_manoeuver(data: pd.DataFrame):
    # prepare dataframe
    df_plot = (
        data.groupby("Vehicle_Manoeuvre")
        .size()
        .reset_index(name="counts")
        .sort_values(by="counts", ascending=False)
    )

    df_plot = df_plot[df_plot.counts > 80000]

    # prepare plot
    labels = df_plot.apply(
        lambda x: str(x[0]) + "\n (" + str(x[1]) + ")", axis=1
    )
    sizes = df_plot["counts"].values.tolist()
    colors = [
        plt.cm.Pastel1(i / float(len(labels))) for i in range(len(labels))
    ]

    # plot
    plt.figure(figsize=(8, 6), dpi=80)
    squarify.plot(sizes=sizes, label=labels, color=colors, alpha=0.8)

    # Decorate
    plt.title(
        "\nTreemap of Vehicle Manoeuvre\n", fontsize=14, fontweight="bold"
    )
    plt.axis("off")
    plt.savefig(os.path.join(ANALYSIS_FOLDER, "accidents_by_manoeuver.png"))
"""

if __name__ == "__main__":
    main()
