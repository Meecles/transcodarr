import datetime


def get_date_format() -> str:
    return "%Y-%m-%d %H-%M-%S"


def get_current_datetime_obj():
    return datetime.datetime.now()


def get_now(date_format=None) -> str:
    now = get_current_datetime_obj()
    return now.strftime(date_format if date_format is not None else get_date_format())

