import pandas as pd
import argparse
import os
import sys
from delivery_insights.models.accidents import Accidents
from delivery_insights.analysis.charts import Chart


def visualize_pipeline():
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-folder", help="input folder", type=str)
    parser.add_argument("--filename", help="filename", type=str)
    parser.add_argument("--output-folder", help="Output folder", type=str)
    args = parser.parse_args()
    input_folder = args.input_folder
    filename = args.filename
    output_folder = args.output_folder

    try:
        if not os.path.exists(os.path.join(input_folder, filename)):
            raise Exception(f"{filename} does not exist.")
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        data = pd.read_csv(os.path.join(input_folder, filename))
        visualize(data=data, output_folder=output_folder)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit()


def visualize(data: pd.DataFrame, output_folder: str):
    """

    :param data:
    :param output_folder:
    :return:
    """
    accidents = Accidents()
    chart = Chart(output_folder=output_folder)
    # draw accidents values by severity
    (
        list_accidents_values_by_severity,
        severity_order_list,
    ) = accidents.get_list_accidents_values_by_column(
        data=data, column="Accident_Severity"
    )
    chart.pie_share_chart(
        data_list=list_accidents_values_by_severity,
        names_list=[f"{val} Accidents" for val in severity_order_list],
        chart_title="Accident Severity: Share in % (2005-2017)",
        filename="Accidents_severity_share.png",
    )

    # draw accidents values by weather conditions
    (
        list_accidents_values_by_weather,
        weather_order_list,
    ) = accidents.get_list_accidents_values_by_column(
        data=data,
        column="Weather_Conditions",
        filter_conditions=["Unknown", "Data missing or out of range"],
    )
    chart.pie_share_chart(
        data_list=list_accidents_values_by_weather,
        names_list=[f"{val} weather" for val in weather_order_list],
        chart_title="Accidents weather conditions: Share in % (2005-2017)",
        filename="Accidents_weather_conditions_share.png",
    )

    # draw total count per date line chart
    chart.total_count_per_date_line_chart(
        data=data,
        index_date_column="Accident_date",
        title="Accidents per Month",
        line_legend_title="Total per Month",
        xlabel_title="Date per Month",
        filename="Accidents_per_months.png",
        rule="M",
    )

    # draw accidents by age and sex
    accidents_by_age_and_sex = accidents.get_accidents_counts_using_two_columns(
        data=data,
        cols=["Age_Band_of_Driver", "Sex_of_Driver"],
        filter_conditions={
            "Age_Band_of_Driver": ["Data missing or out of range"],
            "Sex_of_Driver": ["Not known", "Data missing or out of range"],
        },
        new_cols_name=["Age_Band_of_Driver", "Sex_of_Driver", "Total"],
    )

    chart.grouped_bar_char(
        data=accidents_by_age_and_sex,
        yaxis_variable="Age_Band_of_Driver",
        xaxis_variable="Total",
        hue_variable="Sex_of_Driver",
        chart_title="Accidents by drivers age and sex",
        xlabel="Total",
        ylabel="Age Band of Driver",
        filename="accidents_by_age_and_sex.png",
        data_labels_params={"fmt": ".0f", "round_number": 0},
    )

    # draw accidents per year
    yearly_count = accidents.get_accidents_per_year(data)
    chart.bar_chart(
        data=yearly_count,
        graph_title="Accidents per Year",
        ylabel="Total values",
        filename="accidents_per_year.png",
    )

    # draw vehicules age band accidents by drivers age
    vehicule_age = [">=15", "10-14", "5-9", "0-4"]

    accidents_share = accidents.get_accidents_share_count(
        data=data,
        cols=["Age_band_of_vehicule", "Age_Band_of_Driver"],
        filter_conditions={
            "Age_band_of_vehicule": ["Data missing"],
            "Age_Band_of_Driver": ["Data missing or out of range"],
        },
    )
    chart.stacked_bar_chart(
        data=accidents_share,
        yaxis_values=vehicule_age,
        chart_title="Vehicule's age bands accidents by Driver's age",
        xlabel="Percentage",
        ylabel="Vehicule's age bands",
        legend_title="Driver's age bands",
        filename="vehicules_age_bands_accidents_by_drivers_age.png",
    )

    # draw accidents by drivers age and vehicle age
    accidents_by_drivers_age_and_vehicules_age = (
        accidents.get_accidents_counts_using_two_columns(
            data=data,
            cols=["Age_Band_of_Driver", "Age_band_of_vehicule"],
            filter_conditions={
                "Age_Band_of_Driver": ["Data missing or out of range"],
                "Age_band_of_vehicule": ["Data missing"],
            },
            new_cols_name=["Age_Band_of_Driver", "Age_band_of_vehicule", "Count"],
        )
    )
    accidents_by_drivers_age_and_vehicules_age["Percentage"] = (
        accidents_by_drivers_age_and_vehicules_age["Count"]
        / accidents_by_drivers_age_and_vehicules_age["Count"].sum()
    )

    chart.grouped_bar_char(
        data=accidents_by_drivers_age_and_vehicules_age,
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

    # draw accidents per weekday and year
    days = [
        "Sunday",
        "Saturday",
        "Friday",
        "Thursday",
        "Wednesday",
        "Tuesday",
        "Monday",
    ]
    accidents_per_weekday_and_year = accidents.get_accidents_per_weekday_and_year(
        data=data, days=days
    )
    chart.heatmap_chart(
        data=accidents_per_weekday_and_year,
        graph_title="Accidents by weekdays and years",
        filename="accidents_per_weekday_and_year.png",
    )

    # draw fatalities over weeks
    fatalities = data[data["Accident_Severity"] == "Fatal"]
    chart.total_count_per_date_line_chart(
        data=fatalities,
        index_date_column="Accident_date",
        title="Fatalities",
        line_legend_title="Total fatalities per week",
        filename="fatalities_over_weeks.png",
        rule="W",
    )

    # draw accidents by hours
    hourly_count = accidents.get_accidents_per_hour(data)
    chart.bar_chart(
        data=hourly_count,
        graph_title="Accidents per Hour",
        ylabel="Total values",
        filename="accidents_per_Hour.png",
    )

    # draw accidents by daytime
    daytime_count = accidents.get_accidents_per_daytime(data)
    chart.bar_chart(
        data=daytime_count,
        graph_title="Accidents per daytime",
        ylabel="Total values",
        filename="accidents_per_daytime.png",
    )

    # draw severity by daytime
    daytime = [
        "night (23-5)",
        "evening (19-23)",
        "afternoon rush (15-19)",
        "office hours (10-15)",
        "morning rush (5-10)",
    ]

    severity_daytime_share = accidents.get_accidents_share_count(
        data=data, cols=["Daytime", "Accident_Severity"]
    )
    chart.stacked_bar_chart(
        data=severity_daytime_share,
        yaxis_values=daytime,
        chart_title="Daytime accidents by severity",
        xlabel="Percentage",
        ylabel="Vehicule's age bands",
        legend_title="Driver's age bands",
        filename="daytime_accidents_by_severity.png",
    )

    # draw accidents by home area
    (
        accidents_by_home_area,
        accidents_by_home_area_labels,
        accidents_by_home_area_sizes,
    ) = accidents.get_accidents_count_by_column(data=data, column="Driver_Home_Area_Type")
    chart.treemap_chart(
        labels=accidents_by_home_area_labels,
        sizes=accidents_by_home_area_sizes,
        filename="accidents_by_home_area.png",
    )

    # draw accidents by journey purpose
    (
        accidents_by_journey_purpose,
        accidents_by_journey_purpose_labels,
        accidents_by_journey_purpose_sizes,
    ) = accidents.get_accidents_count_by_column(
        data=data, column="Journey_Purpose_of_Driver"
    )
    chart.treemap_chart(
        labels=accidents_by_journey_purpose_labels,
        sizes=accidents_by_journey_purpose_sizes,
        filename="accidents_by_journey_purpose.png",
    )

    # draw accidents by manoeuver
    (
        accidents_by_manoeuver,
        accidents_by_manoeuver_labels,
        accidents_by_manoeuver_sizes,
    ) = accidents.get_accidents_count_by_column(
        data=data, column="Vehicle_Manoeuvre", min_value=80000
    )
    chart.treemap_chart(
        labels=accidents_by_manoeuver_labels,
        sizes=accidents_by_manoeuver_sizes,
        filename="accidents_by_manoeuver.png",
    )
