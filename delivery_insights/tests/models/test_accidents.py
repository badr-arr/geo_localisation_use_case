import pandas as pd
from pandas.testing import assert_frame_equal

from delivery_insights.models.accidents import Accidents


def test_transform():
    """
    Test Accidents tranform function

    :return:
    """
    data = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
        }
    )
    accidents = Accidents()

    expected = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
            "Hour": [17, 10],
            "Daytime": ["afternoon rush (15-19)", "office hours (10-15)"],
            "Age_band_of_vehicule": ["0-4", "5-9"],
        }
    )
    expected["Accident_date"] = pd.to_datetime(
        expected["Accident_date"], format="%Y-%m-%d"
    )
    result = accidents.transform(data)

    res = assert_frame_equal(
        expected.sort_values(by="Accident_date"),
        result.sort_values(by="Accident_date"),
        check_dtype=False,
    )
    assert res is None


def test_filter_data():
    """
    Test Accidents filter_data function

    :return:
    """
    data = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
        }
    )
    accidents = Accidents()

    expected = pd.DataFrame(
        {"Accident_date": ["2019-09-10"], "Time": ["10:00"], "Age_of_Vehicle": [6]}
    )

    result = accidents.filter_data(data, column="Time", filter_conditions="17:00")

    res = assert_frame_equal(
        expected.sort_values(by="Accident_date").reset_index(drop=True),
        result.sort_values(by="Accident_date").reset_index(drop=True),
        check_dtype=False,
    )
    assert res is None


def test_get_list_accidents_values_by_column():
    """
    Test Accidents get_list_accidents_values_by_column function

    :return:
    """
    data = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
        }
    )
    accidents = Accidents()

    expected, expected_cols = [1], ["10:00"]
    result, cols = accidents.get_list_accidents_values_by_column(
        data=data, column="Time", filter_conditions="17:00"
    )

    assert sorted(expected) == sorted(result)
    assert sorted(expected_cols) == sorted(cols)


def test_get_accidents_share_count():
    """
    Test Accidents get_accidents_share_count function

    :return:
    """
    data = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
        }
    )
    accidents = Accidents()

    expected = pd.DataFrame({"10:00 in %": [1]})
    expected.index.names = ["Time"]
    result = accidents.get_accidents_share_count(
        data=data, cols=["Accident_date", "Time"], filter_conditions={"Time": ["17:00"]}
    )

    assert expected.columns == result.columns
    assert len(expected) == len(result)


def test_get_accidents_counts_using_two_columns():
    """
    Test Accidents get_accidents_counts_using_two_columns function

    :return:
    """
    data = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
        }
    )
    accidents = Accidents()

    expected = pd.DataFrame(
        {
            "Accident_date": ["2019-09-10"],
            "Time": ["10:00"],
            "Count": [1],
        }
    )

    result = accidents.get_accidents_counts_using_two_columns(
        data=data,
        cols=["Accident_date", "Time"],
        filter_conditions={"Time": ["17:00"]},
        new_cols_name=["Accident_date", "Time", "Count"],
    )

    res = assert_frame_equal(
        expected.sort_values(by="Accident_date").reset_index(drop=True),
        result.sort_values(by="Accident_date").reset_index(drop=True),
        check_dtype=False,
    )
    assert res is None


def test_get_accidents_per_year():
    """
    Test Accidents get_accidents_per_year function

    :return:
    """
    data = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
        }
    )
    accidents = Accidents()

    expected = pd.Series([1, 1])
    transformed_data = accidents.transform(data)
    result = accidents.get_accidents_per_year(data=transformed_data)

    assert expected.equals(result.reset_index(drop=True))


def test_get_accidents_per_hour():
    """
    Test Accidents get_accidents_per_hour function

    :return:
    """
    data = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
        }
    )
    accidents = Accidents()

    expected = pd.Series([1, 1])
    transformed_data = accidents.transform(data)
    result = accidents.get_accidents_per_hour(data=transformed_data)

    assert expected.equals(result.reset_index(drop=True))


def test_get_accidents_per_daytime():
    """
    Test Accidents get_accidents_per_daytime function

    :return:
    """
    data = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
        }
    )
    accidents = Accidents()

    expected = pd.Series([1, 1])
    transformed_data = accidents.transform(data)
    result = accidents.get_accidents_per_daytime(transformed_data)

    assert expected.equals(result.reset_index(drop=True))


def test_get_accidents_per_weekday_and_year():
    """
    Test Accidents get_accidents_per_weekday_and_year function

    :return:
    """
    data = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
        }
    )
    accidents = Accidents()

    expected = pd.DataFrame({"Sunday": [None, 1], "Tuesday": [1, None]})
    transformed_data = accidents.transform(data)
    result = accidents.get_accidents_per_weekday_and_year(
        transformed_data, days=["Sunday", "Tuesday"]
    )

    assert sorted(expected.columns) == sorted(result.columns)
    assert len(expected) == len(result)


def test_get_accidents_count_by_column():
    """
    Test Accidents get_accidents_count_by_column function

    :return:
    """
    data = pd.DataFrame(
        {
            "Accident_date": ["2020-10-11", "2019-09-10"],
            "Time": ["17:00", "10:00"],
            "Age_of_Vehicle": [1, 6],
        }
    )
    accidents = Accidents()

    expected = pd.DataFrame({"Time": ["10:00", "17:00"], "counts": [1, 1]})
    expected_labels = pd.Series(["10:00\n (1)", "17:00\n (1)"])
    expected_sizes = [1, 1]
    result, result_labels, result_sizes = accidents.get_accidents_count_by_column(
        data=data, column="Time", filter_conditions="15:00"
    )

    res = assert_frame_equal(
        expected.reset_index(drop=True), result.reset_index(drop=True), check_dtype=False
    )

    assert res is None
    assert expected_labels.equals(result_labels)
    assert sorted(expected_sizes) == sorted(result_sizes)
