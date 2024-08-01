from datetime import datetime
#import numpy
from pytz import timezone
import time
from random import choices

# https://www.postgresql.org/docs/9.0/functions-datetime.html
# 'n' seconds input for pg_sleep, but actual sleep time ends up being much longer
times = [0.0125, 0.0625, 0.125, 0.1875, 0.25, 0.3125]

# weight distribution that favors faster times
weights1 = [0.16, 0.5, 0.14, 0.1, 0.06, 0.04]
# weight distribution that favors the slower times
weights2 = [0.04, 0.06, 0.1, 0.14, 0.5, 0.16]

# The hour is either '14' or '12' which allows for a nice overlap to show a high-to-low or low-to-high change
# the 'condition' is either "greater than or equal to" or "less than or equal to"
# The delay value in seconds is according to a logarithmic distribution of 1 to 10"
def weighter(condition, hour):
    current_hour = datetime.now(timezone('America/Los_Angeles')).hour
    time_to_sleep = choices(times, weights1) if condition(current_hour, hour)  else choices(times, weights2)
    return time_to_sleep[0]

def parseHeaders(keys, headers):
    parsedHeaders = {}
    for key in keys:
        value = headers.get(key) if headers.get(key) != "undefined" else None
        parsedHeaders[key] = value
    return parsedHeaders

def get_subscription_plan(type):
    return 'monthly' if type == 'monthly' else 'annual'

def get_if_else_result():
    if True:
        return True
    else:
        return False

def get_iterator(n):
    #fibonacci
    if n < 0:
        print("Incorrect input")
    elif n == 0:
        return 0
    elif n == 1 or n == 2:
        return 1
    else:
        return get_iterator(n-1) + get_iterator(n-2)

def yuval(text):
    return ""

def chris():
    return ""
