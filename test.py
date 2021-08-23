
import requests
from bs4 import BeautifulSoup



url = "https://finance.yahoo.com/quote/AAPL"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "lxml")
stock_daily_return = soup.find("span", {"class": "Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px) C($positiveColor)"}).text
print(stock_daily_return)
