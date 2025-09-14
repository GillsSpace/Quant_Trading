from utility.lib_timeFunctions import round_to_nearest_5
from main_classes.UniverseManager import UniverseManager as UM
from main_classes.DataManager import DataManager as DM

from datetime import datetime, timedelta

def main():
    datetime_raw = datetime.now()
    datetime_rounded = round_to_nearest_5(datetime_raw)
    date_str = datetime_rounded.strftime("%Y-%m-%d")
    time_str = datetime_rounded.strftime("%H:%M")

    # Always Run;
    dm = DM()
    dm.save_qVar_data(date_str, time_str)

    if time_str == "23:40":
        next_day = (datetime_rounded + timedelta(days=1)).strftime("%Y-%m-%d")
        UM.regen_csv('gill_01')
        dm.add_day_shell(next_day)

    if time_str == "04:00":
        dm.save_fVar_data(date_str)

if __name__ == "__main__":
    main()
