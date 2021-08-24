import requests
from bs4 import BeautifulSoup



url = "https://finance.yahoo.com/quote/TSLA"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "lxml")
stock_daily_return = soup.find("div", {"class": "D(ib) Va(m) Maw(65%) Ov(h)"}).find("div").find_all("span")[1].text

print(stock_daily_return)
