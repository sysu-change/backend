import datetime

t = "2019-06-06"
t = datetime.datetime.strptime(t, "%Y-%m-%d") + datetime.timedelta(days=1)
n = datetime.datetime.now()
print(t < n)