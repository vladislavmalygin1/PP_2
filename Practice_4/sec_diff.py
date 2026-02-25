from datetime import datetime
import time

start_time = datetime(2026, 2, 25, 12, 0, 0) 
end_time = datetime.now()

duration = end_time - start_time

seconds_diff = duration.total_seconds()

print(f"Difference: {seconds_diff:.2f} seconds")