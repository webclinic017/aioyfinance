import unittest
import aioyfinance as yf
import asyncio as asy
from aioyfinance.old_urls import *
from aioyfinance.tickers import strip_old_json

loop = asy.get_event_loop()

class MyTestCase(unittest.TestCase):

    def test_wrong(self):
        wrong_ticker = 'lalaboba'
        ticker = yf.Ticker(wrong_ticker)

        fails = []

        def try_block(callable):
            nonlocal fails

            try:
                loop.run_until_complete(callable)
            except NameError as e:
                fails.append(True)
            else:
                fails.append(False)

        try_block(ticker.get_timeseries('1d', '1mo'))
        try_block(ticker.get_statistics())
        try_block(ticker.get_profile())

        self.assertNotIn(False, fails)

    def test_mult_wrong(self):
        wrong_tickers = ['amd', 'lalaboba', 'nvda']
        tickers = yf.Tickers(wrong_tickers)


        right, wrong = loop.run_until_complete(tickers.get_statistics())

        self.assertEqual(len(right), 2)
        self.assertEqual(len(wrong), 1)

    def test_fund_strip(self):

        ticker = yf.Ticker('nvda')

        data = loop.run_until_complete(ticker._get_fundamentals(income_statement_annual))

        strip = strip_old_json(data)

        self.assertIsNotNone(strip)

    def test_income(self):
        #TODO probably better tests needed, these are shallow
        ticker = yf.Ticker('nvda')

        data = loop.run_until_complete(ticker.get_income())
        data_quarterly = loop.run_until_complete(ticker.get_income(False))

        self.assertIsNotNone(data)
        self.assertIsNotNone(data_quarterly)

if __name__ == '__main__':
    unittest.main()