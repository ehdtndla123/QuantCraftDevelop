# from fastapi import FastAPI
# from app.controller import trading_controller
#
# app = FastAPI()
#
# app.include_router(trading_controller.router, prefix="/trading", tags=["trading"])
#
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from app.service.backtest import BacktestManager
from app.service.strategy import MyStrategy
from app.service.TradingBot import TradingBot
import ccxt.pro as ccxtpro
import asyncio

async def main():
    # exchange = ccxtpro.binance()
    #
    #
    # if exchange.has['watchOHLCV']:
    #     print('Watching OHLCV...')
    #     while True:
    #         try:
    #             candles = await exchange.watch_ohlcv("BTC/USDT", "1m")
    #             print(exchange.iso8601(exchange.milliseconds()), candles)
    #         except Exception as e:
    #             print(e)
    #             # stop the loop on exception or leave it commented to retry
    #             # raise e

    bot = TradingBot('binance','BTC/USDT', '1m', MyStrategy, initial_cash=10000)

    try:
        await bot.run()
    except KeyboardInterrupt:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())


# BacktestManager.run_backtest(
#     exchange_name="binance",
#     symbol="BTC/USDT",
#     timeframe="1d",
#     start_time="2019-01-01",
#     end_time="2024-06-21",
#     timezone="Asia/Seoul",
#     strategy_name="MyStrategy",
#     commission=0.002,
#     cash=100000,
#     exclusive_orders=True
# )

# bt.plot(
#     plot_width=None,  # 기본값 유지
#     plot_equity=True,
#     plot_return=True,
#     plot_pl=True,
#     plot_volume=True,
#     plot_drawdown=True,
#     smooth_equity=True,
#     relative_equity=True,
#     superimpose=True,
#     resample=True,
#     reverse_indicators=True,
#     show_legend=True,
# )