import datetime
import time

t = datetime.datetime.now()
print(t)
t = datetime.datetime.now()
print(t)
t2 = time.time()
print(t2)
t2 = datetime.datetime.fromtimestamp(t2)
print(t2)
print(t.year)
print(t.month)
print(t.day)
print(t.hour)
print(t.minute)
print(t.second)
print(t.microsecond)
print(datetime.datetime.fromtimestamp(0))
print(min([[1,2],[3,4]]))