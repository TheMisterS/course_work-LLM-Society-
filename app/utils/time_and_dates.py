from datetime import datetime

def date_stamp():
    return datetime.now().strftime("%Y.%m.%d")

def date_time_stamp():
    return datetime.now().strftime("%Y.%m.%d_%H.%M.%S")