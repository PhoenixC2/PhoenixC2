import datetime


def convert_to_unix_timestamp(date: datetime.datetime):
    """
    Convert a datetime object to a unix timestamp.
    """
    if date is None:
        return None
    return int(date.timestamp())


def convert_from_unix_timestamp(timestamp: int):
    """
    Convert a unix timestamp to a datetime object.
    """
    if timestamp is None:
        return None
    return datetime.datetime.fromtimestamp(timestamp)
