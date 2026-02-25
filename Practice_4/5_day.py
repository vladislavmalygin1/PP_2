from datetime import datetime, timedelta

current_date = datetime.now()

days_to_subtract = 5
time_difference = timedelta(days=days_to_subtract)

new_date = current_date - time_difference

print(f"Current Date: {current_date.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Date 5 Days Ago: {new_date.strftime('%Y-%m-%d %H:%M:%S')}")
