from datetime import datetime, timedelta


def format_date(date: datetime):
    current_date = datetime.now()
    time_difference = current_date - date

    if time_difference.seconds < 60:
        return f"{time_difference.seconds} second{'s' if time_difference.seconds > 1 else ''} ago"
    elif time_difference.seconds < 3600:
        return f"{time_difference.seconds // 60} minute{'s' if time_difference.seconds // 60 > 1 else ''} ago"
    elif time_difference.days == 0:
        return f"{time_difference.seconds // 3600} hour{'s' if time_difference.seconds // 3600 > 1 else ''} ago"
    elif time_difference.days == 1:
        return "yesterday"
    elif time_difference.days < 7:
        return f"{time_difference.days} day{'s' if time_difference.days > 1 else ''} ago"
    else:
        return date.strftime("%d/%m/%Y")
    
print(format_date(datetime(2022, 12, 19, 10, 59, 59)))