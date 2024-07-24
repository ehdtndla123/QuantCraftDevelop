import asyncio
import pandas as pd
import numpy as np
from backtesting import Strategy
from typing import Dict, Any

from backtesting.backtesting import _Broker
from backtesting.backtesting import Strategy
import ccxt.pro as ccxt



class TradingBot:
    def __init__(self,exchange_name: str, symbol: str, timeframe: str, strategy_class: type, initial_cash: float,
                 commission: float = 0.001):
        self.symbol = symbol
        self.timeframe = timeframe
        self.strategy_class = strategy_class
        self.initial_cash = initial_cash
        self.commission = commission
        self.data = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        self.is_running = False

        self.broker = _Broker(data=self.data, cash=initial_cash, commission=commission,margin=1.,
                 trade_on_close=False,
                 hedging=False,
                 exclusive_orders=False,
                index=self.data.index)

        self.strategy = None
        self.exchange = getattr(ccxt, exchange_name)()

    async def simulate_ohlcv(self):
        print(f"Starting to simulate OHLCV data for {self.symbol} on {self.exchange.name}")
        last_timestamp = None
        while self.is_running:
            if self.exchange.has['watchOHLCV']:
                try:
                    candles = await self.exchange.watch_ohlcv(self.symbol, self.timeframe, None, 1)
                    print(self.exchange.iso8601(self.exchange.milliseconds()), candles)
                    for candle in candles:
                        timestamp, open_price, high, low, close, volume = candle
                        if last_timestamp is None or timestamp >= last_timestamp + self.timeframe_to_seconds() * 1000:
                            new_row = pd.DataFrame({
                                'Open': [open_price],
                                'High': [high],
                                'Low': [low],
                                'Close': [close],
                                'Volume': [volume]
                            }, index=[timestamp])

                            if not new_row.empty:
                                self.data = pd.concat([self.data, new_row])
                                self.data = self.data.sort_index()
                                self.data = self.data.tail(100)

                            if len(self.data) >= 2:
                                self.execute_strategy()

                            last_timestamp = timestamp

                except Exception as e:
                    print(f"An error occurred: {e}")
                    await asyncio.sleep(1)

    def timeframe_to_seconds(self):
        # '1m' -> 60, '5m' -> 300, '1h' -> 3600 등의 변환 함수
        unit = self.timeframe[-1]
        amount = int(self.timeframe[:-1])
        if unit == 'm':
            return amount * 60
        elif unit == 'h':
            return amount * 3600
        elif unit == 'd':
            return amount * 86400
        else:
            raise ValueError("Unsupported timeframe unit")

    def execute_strategy(self):
        if self.strategy is None:
            self.strategy = self.strategy_class
            self.strategy = self.strategy(data=self.data, broker=self.broker)
            self.strategy.init()

        # 새 데이터에 대해 전략 실행
        self.strategy.next()

        # 주문 처리
        self.broker.next()

        # 현재 상태 출력
        print(f"Timestamp: {self.data.index[-1]}")
        print(f"Price: {self.data['Close'].iloc[-1]}")
        print(f"Cash: {self.broker._cash}")
        print(f"Position: {self.broker.position.size}")
        print(f"Equity: {self.broker.equity}")
        print("---")

    async def run(self):
        self.is_running = True
        print("Starting the bot...")
        await self.simulate_ohlcv()

    async def stop(self):
        self.is_running = False
        print("\nFinal Results:")
        print(f"Total Return: {(self.broker.equity / self.initial_cash - 1) * 100:.2f}%")
        print(f"Number of Trades: {len(self.broker.closed_trades)}")
