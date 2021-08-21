
import requests
from bs4 import BeautifulSoup

url = "https://finance.yahoo.com/quote/AAPL"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "lxml")
stock_name = soup.find("div", {"class": "D(ib) Mt(-5px) Mend(20px) Maw(56%)--tab768 Maw(52%) Ov(h) smartphone_Maw(85%) smartphone_Mend(0px)"}).find_all("div")[0].find("h1").text
print(stock_name)
