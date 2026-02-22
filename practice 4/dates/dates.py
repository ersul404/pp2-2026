from datetime import datetime, timedelta

now = datetime.now()
result = now - timedelta(days=5)

print(now)
print(result)