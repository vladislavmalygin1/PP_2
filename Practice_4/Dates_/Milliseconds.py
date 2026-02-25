from datetime import datetime

now = datetime.now()

clean_time = now.replace(microsecond=0)

print(f"Original: {now}")
print(f"Cleaned:  {clean_time}")