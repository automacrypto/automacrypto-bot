import time

def formatted_date(format = '%Y-%m-%d %H:%M:%S'):
    datetime = time.localtime()
    formatted = time.strftime(format, datetime)
    return formatted