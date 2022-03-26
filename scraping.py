from retry import retry
import requests
from bs4 import BeautifulSoup
import pandas as pd 
import datetine

def url_generater():
    print("URL generater start")

# 県が　ta に関係している
    prefecture = {1:"北海道" , }








# 東京23区
base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13101&sc=13102&sc=13103&sc=13104&sc=13105&sc=13113&sc=13106&sc=13107&sc=13108&sc=13118&sc=13121&sc=13122&sc=13123&sc=13109&sc=13110&sc=13111&sc=13112&sc=13114&sc=13115&sc=13120&sc=13116&sc=13117&sc=13119&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=25&pc=50&page={}"

@retry(tries=3, delay=10, backoff=2)
def get_html(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

all_data = []
max_page = 2

for page in range(1, max_page+1):
    # define url 
    url = base_url.format(page)
    
    # get html
    soup = get_html(url)
    
    # extract all items
    items = soup.findAll("div", {"class": "cassetteitem"})
    print("page", page, "items", len(items))
    
    # process each item
    for item in items:
        stations = item.findAll("div", {"class": "cassetteitem_detail-text"})
        
        # process each station 
        for station in stations:
            # define variable 
            base_data = {}

            # collect base information    
            base_data["名称"] = item.find("div", {"class": "cassetteitem_content-title"}).getText().strip()
            base_data["カテゴリー"] = item.find("div", {"class": "cassetteitem_content-label"}).getText().strip()
            base_data["アドレス"] = item.find("li", {"class": "cassetteitem_detail-col1"}).getText().strip()
            base_data["アクセス"] = station.getText().strip()
            base_data["築年数"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[0].getText().strip()
            base_data["構造"] = item.find("li", {"class": "cassetteitem_detail-col3"}).findAll("div")[1].getText().strip()
            
            # process for each room
            tbodys = item.find("table", {"class": "cassetteitem_other"}).findAll("tbody")
            
            for tbody in tbodys:
                data = base_data.copy()

                data["階数"] = tbody.findAll("td")[2].getText().strip()

                data["家賃"] = tbody.findAll("td")[3].findAll("li")[0].getText().strip()
                data["管理費"] = tbody.findAll("td")[3].findAll("li")[1].getText().strip()

                data["敷金"] = tbody.findAll("td")[4].findAll("li")[0].getText().strip()
                data["礼金"] = tbody.findAll("td")[4].findAll("li")[1].getText().strip()

                data["間取り"] = tbody.findAll("td")[5].findAll("li")[0].getText().strip()
                data["面積"] = tbody.findAll("td")[5].findAll("li")[1].getText().strip()
                
                data["URL"] = "https://suumo.jp" + tbody.findAll("td")[8].find("a").get("href")
                
                all_data.append(data)    

# convert to dataframe
df = pd.DataFrame(all_data)

#date generate for file output
fname = str(datetime.datetime.today())
fname = fname[0:16]

# output to csv
fname = 'web_out.csv' + fname
df.to_csv(fname)
