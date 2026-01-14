import datetime

MANIFEST = {
    "get_time": {
        "description": "Get the current clock time."
    },
    "get_date": {
        "description": "Get today's date including the day of the week."
    }
}

def get_time():
    return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."

def get_date():
    return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."
