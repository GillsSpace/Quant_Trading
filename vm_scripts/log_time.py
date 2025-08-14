from datetime import datetime

# File path (you can change this to your desired location)
file_path = "timestamp_log.txt"

# Get the current date and time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Open the file in append mode and add the time
with open(file_path, "a") as file:
    file.write(current_time + "\n")
