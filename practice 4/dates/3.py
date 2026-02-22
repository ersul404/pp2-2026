from datetime import datetime

now = datetime.now()

new_time = now.replace(microsecond=0)

print("Before:", now)
print("After:", new_time)