from flask import Blueprint, render_template, url_for
from universes.universe_config import Universe_Config
import json
import xarray as xr
from datetime import datetime, timedelta
import numpy as np

data_bp = Blueprint('data', __name__,
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='/data/static')

@data_bp.route('/')
def page_index():
    """Render the index page."""

    json_data = Universe_Config.universe_dict

    return render_template('data/data.html', content=json_data)

def get_completeness_stats():
    """
    Analyzes the last 90 days of data in the master Zarr database
    to calculate data completeness for each day using xarray.
    """
    try:
        ds = xr.open_zarr('/home/willse/W_Projects/Quant_Trading/data/hot/master_db.zarr', consolidated=True)
    except Exception as e:
        return [{"date": (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                 "tooltip": f"Error: Could not open Zarr store. {e}",
                 "color": "hsl(0, 100%, 50%)", "completeness": 0} for i in range(90)]

    try:
        # Use .item() to get the scalar value from the 0-d array
        close_price_idx = np.where(ds.fVar.values == 'quote.closePrice')[0].item()
    except (ValueError, IndexError):
        ds.close()
        return [{"date": (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                 "tooltip": "Error: 'quote.closePrice' not found in fVar coordinates.",
                 "color": "hsl(0, 100%, 50%)", "completeness": 0} for i in range(90)]

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=89)
    
    daily_stats = []

    for i in range(90):
        current_date = start_date + timedelta(days=i)
        day_str = current_date.strftime('%Y-%m-%d')
        
        stats = {}
        
        if day_str not in ds.day.values:
            stats = {
                "date": current_date.strftime('%Y-%m-%d'),
                "tooltip": f"Date: {current_date.strftime('%Y-%m-%d')}\nNo data available.",
                "color": "hsl(0, 100%, 50%)",
                "completeness": 0
            }
        else:
            # Metric 1: Time completeness from '5m' data
            day_slice_5m = ds['5m'].sel(day=day_str)
            non_nan_times = (~np.isnan(day_slice_5m)).any(dim=['ident', 'qVar']).sum().compute().item()
            time_completeness = non_nan_times / len(ds.time)

            # Metric 2: Price completeness from '1d' data
            day_slice_1d = ds['1d'].sel(day=day_str)
            close_price_data = day_slice_1d[:, close_price_idx]
            valid_prices = (~np.isnan(close_price_data)).sum().compute().item()
            price_completeness = valid_prices / len(ds.ident) if len(ds.ident) > 0 else 0

            total_completeness = (time_completeness + price_completeness) / 2.0
            total_completeness = min(total_completeness, 1.0)

            hue = total_completeness * 120
            color = f"hsl({hue}, 100%, 50%)"

            stats = {
                "date": current_date.strftime('%Y-%m-%d'),
                "tooltip": (
                    f"Date: {current_date.strftime('%Y-%m-%d')}\n"
                    f"Completeness: {total_completeness:.1%}\n"
                    f"Time Points: {non_nan_times}/{len(ds.time)} ({time_completeness:.1%})\n"
                    f"Valid Prices: {valid_prices}/{len(ds.ident)} ({price_completeness:.1%})"
                ),
                "color": color,
                "completeness": total_completeness * 100
            }
        daily_stats.append(stats)
        
    ds.close()
    return daily_stats

@data_bp.route('/coverage')
def page_coverage():
    """Render the data coverage page."""
    stats = get_completeness_stats()
    return render_template('data/coverage.html', completeness_stats=stats)
