import requests
from . import FeedSource, _request_headers


class Coinmarketcap(FeedSource):
    def _fetch(self):
        feed = {}
        try:
            url = 'https://api.coinmarketcap.com/v1/ticker/'
            response = requests.get(
                url=url, headers=_request_headers, timeout=self.timeout)
            result = response.json()
            for asset in result:
                for quote in self.quotes:
                    if asset["symbol"] == quote:
                        
                        self.add_rate(feed, 'BTC', quote, 
                            float(asset["price_btc"]), 
                            float(asset["24h_volume_usd"]) / float(asset["price_btc"]))

                        self.add_rate(feed, 'USD', quote, float(asset["price_usd"]), float(asset["24h_volume_usd"]))

        except Exception as e:
            raise Exception(
                "\nError fetching results from {1}! ({0})".format(
                    str(e), type(self).__name__))
        self._fetch_altcap(feed)

        return feed

    def _fetch_altcap(self, feed):
        if 'BTC' in self.bases and ('ALTCAP' in self.quotes or 'ALTCAP.X' in self.quotes):
            try:
                ticker = requests.get(
                    'https://api.coinmarketcap.com/v1/ticker/').json()
                global_data = requests.get(
                    'https://api.coinmarketcap.com/v1/global/').json()
                bitcoin_data = requests.get(
                    'https://api.coinmarketcap.com/v1/ticker/bitcoin/'
                ).json()[0]
                alt_caps_x = [float(coin['market_cap_usd'])
                              for coin in ticker if
                              float(coin['rank']) <= 11 and
                              coin['symbol'] != "BTC"
                              ]
                alt_cap = (
                    float(global_data['total_market_cap_usd']) -
                    float(bitcoin_data['market_cap_usd']))
                alt_cap_x = sum(alt_caps_x)
                btc_cap = next((
                    coin['market_cap_usd']
                    for coin in ticker if coin["symbol"] == "BTC"))

                btc_altcap_price = float(alt_cap) / float(btc_cap)
                btc_altcapx_price = float(alt_cap_x) / float(btc_cap)

                if 'ALTCAP' in self.quotes:
                    self.add_rate(feed, 'BTC', 'ALTCAP', btc_altcap_price, 1.0)
                if 'ALTCAP.X' in self.quotes:
                    self.add_rate(feed, 'BTC', 'ALTCAP.X', btc_altcapx_price, 1.0)
            except Exception as e:
                raise Exception(
                    "\nError fetching results from {1}! ({0})".format(
                        str(e), type(self).__name__))
        return feed
