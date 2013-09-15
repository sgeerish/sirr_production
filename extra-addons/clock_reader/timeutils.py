import datetime as _dt

_dbdtf = '%Y-%m-%d %H:%M:%S'
_dbdf = '%Y-%m-%d'

date = _dt.date
datetime = _dt.datetime
timedelta = _dt.timedelta
time = _dt.time
total_seconds = lambda td: (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
total_hours = lambda td: _total_seconds(td) / 3600.

dt = lambda sd: _dt.datetime.strptime(sd, _dbdtf)
d = lambda sd: _dt.datetime.strptime(sd, _dbdf)
dt2s = lambda sd: sd.strftime(_dbdtf)
d2s = lambda sd: sd.strftime(_dbdf)

def in_range(date_from, date_to, date):
    if isinstance(date_from, str):
        date_from = dt(date_from)
    if isinstance(date_to, str):
        date_to = dt(date_to)
    if isinstance(date, str):
        date = dt(date)

    return date_from <= date and date <= date_to

