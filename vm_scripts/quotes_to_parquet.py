import sys
import time as tm
from datetime import datetime, date, time, timedelta

from universes.universe_config import Universe_Config as uc
from utility.lib_timeFunctions import round_to_nearest_5

if __name__ == "__main__":
    st = tm.time()

    args = sys.argv
    print(f"Saving {args[1]} quotes to Parquet file...")

    date = datetime.now()
    date_str = date.strftime("%Y-%m-%d")
    time_str = round_to_nearest_5(date).strftime("%H:%M")

    # Fetch quotes from the API
    quotes_df = uc.return_universe_quotes_df(args[1])

    t01_a_cols = [
        'ident',
        'reference.htbRate',
        'reference.htbQuantity',
        'extended.askPrice',
        'extended.askSize',
        'extended.bidPrice',
        'extended.bidSize',
        'extended.lastPrice',
        'extended.lastSize',
        'extended.tradeTime',
        'extended.totalVolume',
        'extended.quoteTime',
        'extended.mark',
        'quote.askPrice',
        'quote.askSize',
        'quote.askTime',
        'quote.bidPrice',
        'quote.bidSize',
        'quote.bidTime',
        'quote.lastPrice',
        'quote.lastSize',
        'quote.tradeTime',
        'quote.totalVolume',
        'quote.quoteTime',
        'quote.mark',
        'quote.52WeekHigh',
        'quote.52WeekLow',
        'quote.highPrice',
        'quote.lowPrice',
        'quote.markChange',
        'quote.markPercentChange',
        'quote.openPrice',
        'quote.netChange',
        'quote.netPercentChange',
        'quote.securityStatus',
        'quote.postMarketChange',
        'quote.postMarketPercentChange',
    ]

    t01_b_cols = [
        'ident',
        'assetSubType',
        'ssid',
        'reference.cusip',
        'reference.exchange',
        'fundamental.avg10DaysVolume',
        'fundamental.avg1YearVolume',
        'fundamental.declarationDate',
        'fundamental.divAmmount',
        'fundamental.divYield',
        'fundamental.divExDate',
        'fundamental.divFreq',
        'fundamental.divPayDate',
        'fundamental.divPayAmmount',
        'fundamental.eps',
        'fundamental.lastEarningsDate',
        'fundamental.nextDivExDate',
        'fundamental.nextDivPayDate',
        'fundamental.peRatio',
        'quote.closePrice',
    ]

    cols_to_drop = [
        'assetMainType',
        'symbol',
        'quoteType',
        'realtime',
        'reference.description',
        'reference.isHardToBorrow',
        'reference.isShortable',
        'reference.otcMarketTier',
        'reference.fsiDesc',
        'reference.exchangeName',
        'reference.cusip',
        'quote.askMICId',
        'quote.bidMICId',
        'quote.lastMICId',
    ]

    # Save to Parquet file
    quotes_df.to_parquet(f"live_data/{args[1]}_{date_str}_{time_str}.parquet", index=False)

    et = tm.time()
    print(f"Saved to 'live_data/{args[1]}_{date_str}_{time_str}.parquet' in {et - st:.2f} seconds.")
