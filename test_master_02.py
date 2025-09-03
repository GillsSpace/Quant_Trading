import xarray as xr
import pandas as pd
import numpy as np
from scipy.stats import linregress
from datetime import time

def calculate_market_neutral_returns(ds, exchange='N'):
    """
    Calculates 5-minute market neutral returns for a given exchange.
    """
    fundamentals = ds['1d']
    all_idents = fundamentals.ident.values
    exchanges = fundamentals.sel(fVar='reference.exchange').values
    exchange_map = pd.Series(exchanges, index=all_idents)
    nyse_idents = exchange_map[exchange_map == 0].index.tolist()
    
    prices = ds['5m'].sel(ident=nyse_idents, qVar='quote.mark').squeeze()
    prices_df = prices.to_pandas()
    
    returns = prices_df.pct_change(fill_method=None)
    market_average_return = returns.mean(axis=1)
    market_neutral_returns = returns.subtract(market_average_return, axis=0)
    
    return market_neutral_returns

def run_cumulative_return_regression(x_returns, y_returns, period1_str, period2_str):
    """
    Runs a regression on two Series of cumulative returns and returns the results.
    """
    common_idents = x_returns.index.intersection(y_returns.index)
    x = x_returns.loc[common_idents].dropna()
    y = y_returns.loc[common_idents].dropna()
    
    common_idents = x.index.intersection(y.index)
    x = x.loc[common_idents]
    y = y.loc[common_idents]

    if len(x) < 2:
        print(f"Skipping regression for {period1_str} -> {period2_str} due to insufficient data.")
        print("-" * 40)
        return None

    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    r_squared = r_value**2
    
    print(f"Regression for cumulative returns:")
    print(f"  Period 1 (X-axis): {period1_str}")
    print(f"  Period 2 (Y-axis): {period2_str}")
    print(f"  R-squared: {r_squared:.6f}")
    print(f"  Slope (Beta): {slope:.6f}")
    print(f"  P-value: {p_value:.6f}")
    print(f"  Number of observations: {len(x)}")
    print("-" * 40)
    
    return {
        'period_1': period1_str,
        'period_2': period2_str,
        'r_squared': r_squared,
        'slope': slope,
        'p_value': p_value,
        'observations': len(x)
    }

def print_summary_statistics(results):
    """
    Calculates and prints summary statistics for all regression models.
    """
    if not results:
        print("No results to summarize.")
        return

    df = pd.DataFrame(results)
    
    avg_r_squared = df['r_squared'].mean()
    avg_slope = df['slope'].mean()
    significant_models = df[df['p_value'] < 0.05].shape[0]
    best_model = df.loc[df['r_squared'].idxmax()]

    print("\n" + "="*60)
    print("SUMMARY OF ALL REGRESSION MODELS")
    print("="*60)
    print(f"Total number of models run: {len(df)}")
    print(f"Average R-squared: {avg_r_squared:.6f}")
    print(f"Average Slope (Beta): {avg_slope:.6f}")
    print(f"Models with significant p-value (< 0.05): {significant_models} out of {len(df)}")
    print("\nBest Performing Model (by R-squared):")
    print(f"  Period: {best_model['period_1']} -> {best_model['period_2']}")
    print(f"  R-squared: {best_model['r_squared']:.6f}")
    print(f"  Slope (Beta): {best_model['slope']:.6f}")
    print(f"  P-value: {best_model['p_value']:.6f}")
    print("="*60 + "\n")

def print_explanation():
    """
    Prints an explanation of the statistical terms.
    """
    print("\n" + "-"*60)
    print("EXPLANATION OF STATISTICAL TERMS")
    print("-"*60)
    print("R-squared:")
    print("  - Represents the proportion of the variance in the next half-hour's returns (Y-axis) that is predictable from the previous half-hour's returns (X-axis).")
    print("  - A value of 0.01 means 1% of the movement in the next period is explained by the movement in the prior period. A higher value indicates a stronger predictive relationship.")
    
    print("\nSlope (Beta):")
    print("  - Measures the expected change in the next period's return for a one-unit change in the current period's return.")
    print("  - A slope of 0.5 means that for every 1% increase in a stock's market-neutral return in the current half-hour, its return is expected to increase by 0.5% in the next half-hour.")
    print("  - A negative slope indicates a reversal (momentum crash).")

    print("\nP-value:")
    print("  - Tests the null hypothesis that the slope is zero (i.e., there is no relationship between the two periods' returns).")
    print("  - A low p-value (typically < 0.05) indicates that you can reject the null hypothesis; there is a statistically significant relationship and the slope value is meaningful.")
    print("  - A high p-value suggests the observed relationship could be due to random chance.")
    print("-"*60 + "\n")

def main():
    db_path = 'data/hot/master_db.zarr'
    ds = xr.open_zarr(db_path, consolidated=True)
    target_day = '2025-09-02'
    ds_today = ds.sel(day=target_day)

    market_neutral_returns = calculate_market_neutral_returns(ds_today)
    
    time_boundaries = pd.to_datetime(
        [f"{target_day} {h:02d}:{m:02d}" for h in range(9, 17) for m in (0, 30)]
    )
    time_boundaries = time_boundaries[(time_boundaries.time >= time(9, 30)) & (time_boundaries.time <= time(16, 0))]

    all_results = []
    for i in range(len(time_boundaries) - 2):
        start_period_1 = time_boundaries[i]
        end_period_1 = time_boundaries[i+1]
        start_period_2 = time_boundaries[i+1]
        end_period_2 = time_boundaries[i+2]

        p1_mask = (pd.to_datetime(market_neutral_returns.index, format='%H:%M').time >= start_period_1.time()) & \
                  (pd.to_datetime(market_neutral_returns.index, format='%H:%M').time < end_period_1.time())
        
        p2_mask = (pd.to_datetime(market_neutral_returns.index, format='%H:%M').time >= start_period_2.time()) & \
                  (pd.to_datetime(market_neutral_returns.index, format='%H:%M').time < end_period_2.time())

        period1_returns = market_neutral_returns[p1_mask]
        period2_returns = market_neutral_returns[p2_mask]

        cumulative_p1 = period1_returns.sum(axis=0)
        cumulative_p2 = period2_returns.sum(axis=0)

        p1_str = f"{start_period_1.strftime('%H:%M')} to {end_period_1.strftime('%H:%M')}"
        p2_str = f"{start_period_2.strftime('%H:%M')} to {end_period_2.strftime('%H:%M')}"

        result = run_cumulative_return_regression(cumulative_p1, cumulative_p2, p1_str, p2_str)
        if result:
            all_results.append(result)

    # After all regressions are run, print the summary and explanation
    print_summary_statistics(all_results)
    print_explanation()

if __name__ == "__main__":
    main()