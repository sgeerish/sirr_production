import datetime as _dt

_dbdtf = '%Y-%m-%d %H:%M:%S'
_dbdf = '%Y-%m-%d'

date = _dt.date 
datetime = _dt.datetime
timedelta = _dt.timedelta
time = _dt.time
total_seconds = lambda td: (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
total_hours = lambda td: total_seconds(td) / 3600.

dt = lambda sd: _dt.datetime.strptime(sd, _dbdtf)
d = lambda sd: _dt.datetime.strptime(sd, _dbdf)
dt2s = lambda sd: sd.strftime(_dbdtf)
d2s = lambda sd: sd.strftime(_dbdf)

def daterange(start_date, end_date=_dt.datetime.today()):
    print start_date, end_date
    for n in range(0,(end_date - start_date).days):
        print start_date + _dt.timedelta(n)
        yield start_date + _dt.timedelta(n)

