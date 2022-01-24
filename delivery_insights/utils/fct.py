def set_daytime_bands(hour: int):
    """

    :param hour:
    :return:
    """
    if 5 <= hour < 10:
        return "morning rush (5-10)"
    elif 10 <= hour < 15:
        return "office hours (10-15)"
    elif 15 <= hour < 19:
        return "afternoon rush (15-19)"
    elif 19 <= hour < 23:
        return "evening (19-23)"
    else:
        return "night (23-5)"


def set_vehicule_age_bands(age: int):
    """

    :param age:
    :return:
    """
    if age < 5:
        return "0-4"
    elif 5 <= age < 10:
        return "5-9"
    elif 10 <= age < 15:
        return "10-14"
    elif age >= 15:
        return ">=15"
    else:
        return "Data missing"
