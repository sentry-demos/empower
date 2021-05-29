from datetime import datetime
import numpy
from pytz import timezone
import time

def release():
    d=datetime.today()
    week=str((d.day-1)//7+1)
    date_given = datetime.today().date()
    month = str(date_given.month)
    return month + "." + week
