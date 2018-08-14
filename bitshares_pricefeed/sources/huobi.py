import csv
import json
import requests
from . import FeedSource, _request_headers


class Huobi(FeedSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _fetch(self):
        feed = {}
        try:
            for base in self.bases:
                for quote in self.quotes:
                    if quote == base:
                        continue
                    url = "http://api.huobi.com/staticmarket/ticker_%s_json.js" % (quote.lower())
                    response = requests.get(url=url, headers=_request_headers, timeout=self.timeout)
                    result = response.json()
                    feed[self.alias(base)]["response"] = result
                    self.add_rate(feed, base, quote, float(result["ticker"]["last"]), float(result["ticker"]["vol"]))
        except Exception as e:
            raise Exception("\nError fetching results from {1}! ({0})".format(str(e), type(self).__name__))
        return feed
