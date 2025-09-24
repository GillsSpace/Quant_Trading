from utility.lib_timeFunctions import round_to_nearest_5
from utility.lib_notifications import send_token_update_email
from main_classes.UniverseManager import UniverseManager as UM
from main_classes.DataManager import DataManager as DM

from datetime import datetime, timedelta

def main():
    datetime_raw = datetime.now()
    datetime_rounded = round_to_nearest_5(datetime_raw)
    date_str = datetime_rounded.strftime("%Y-%m-%d")
    time_str = datetime_rounded.strftime("%H:%M")
    print(time_str)

    # Always Run;
    dm = DM()
    dm.save_qVar_data(date_str, time_str)

    if time_str == "23:40":
        next_day = (datetime_rounded + timedelta(days=1)).strftime("%Y-%m-%d")
        UM.regen_csv('u00')
        dm.add_day_shell(next_day)
        send_token_update_email("werda@middlebury.edu")

    if time_str == "04:00":
        dm.save_fVar_data(date_str)

if __name__ == "__main__":
    main()
