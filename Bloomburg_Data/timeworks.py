from datetime import datetime, timedelta, time

def generate_time_intervals(start_date, end_date):
    """
    Generate a list of datetime objects at 5-minute intervals from 3:55 to 19:55
    each weekday (Monday to Friday) within the given date range.
    
    Parameters:
    start_date (datetime): The starting date and time
    end_date (datetime): The ending date and time
    
    Returns:
    list: A list of datetime objects representing the 5-minute intervals
    """
    
    # First time of the day is 3:55
    first_time = time(3, 55)
    # Last time of the day is 19:55
    last_time = time(19, 55)
    
    # Initialize the result list
    intervals = []
    
    # Set current date to start date
    current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Continue until we reach or exceed the end date
    while current_date <= end_date:
        # Check if the current day is a weekday (0 = Monday, 6 = Sunday)
        if current_date.weekday() < 5:  # Monday to Friday
            # Start with the first time of the day
            current_time = datetime.combine(current_date.date(), first_time)
            
            # If the start_date is later on the first day, adjust the starting time
            if current_date.date() == start_date.date() and start_date.time() > first_time:
                # Find the next 5-minute interval after start_date
                minutes_since_midnight = start_date.hour * 60 + start_date.minute
                # Round up to the next 5-minute interval
                rounded_minutes = ((minutes_since_midnight + 4) // 5) * 5
                adjusted_hour = rounded_minutes // 60
                adjusted_minute = rounded_minutes % 60
                current_time = datetime.combine(start_date.date(), time(adjusted_hour, adjusted_minute))
            
            # Generate intervals for the day
            while current_time.time() <= last_time:
                # Only add the time if it's within our date range
                if current_time >= start_date and current_time <= end_date:
                    intervals.append(current_time)
                
                # Move to the next 5-minute interval
                current_time += timedelta(minutes=5)
        
        # Move to the next day
        current_date += timedelta(days=1)
    
    return intervals

