import multiprocessing
import requests
from datetime import datetime
from settings import headers  #Your headers
from bs4 import BeautifulSoup
import csv

# Список ссылок на сайты
urls = [
    'https://www.astro.com/wiki/astro-databank/index.php?title=Special:AllPages&from=Camossi%2C+Paolo',
    'https://www.astro.com/wiki/astro-databank/index.php?title=Special:AllPages&from=Cardenas%2C+Enrique',
    'https://www.astro.com/wiki/astro-databank/index.php?title=Special:AllPages&from=Carraway%2C+Nancy',
]


def get_categories(soup_href):
    categories = []
    all_ul = soup_href.find_all("ul")
    flg = False
    try:
        for i in all_ul:
            text = (i.find_previous().text)
            if text == "Categories":
                flg = True
            if flg:
                if str(i.find("a")) == "None":
                    categories.append(i.text.replace("\xa0", ""))
                else:
                    break
    except:
        categories.append("not found")
    return categories


def get_full_info(url):
    src = download(url)
    soup = BeautifulSoup(src, "lxml")
    all_names = soup.find_all("li")
    all_names = (all_names[:len(all_names) - 18])
    hrefs = []
    for item in all_names:
        href = "https://www.astro.com" + str(item.find("a").get("href"))
        hrefs.append(href)
    for j in range(len(hrefs)):
        try:
            src = download(hrefs[j])
            soup_href = BeautifulSoup(src, "lxml")
            tbody = soup_href.find("tbody").find_all("tr")
            if len(tbody) != 11:
                tbody.insert(2, "absent")
            ln = len(tbody)
            name = tbody[0].find_all("td")[1].find("tbody").find_all("td")[0].text
            gender = tbody[0].find_all("td")[1].find("tbody").find_all("td")[1].text[-2]
            try:
                birthname = tbody[2].find_all("td")[1].text.rstrip()
            except:
                birthname = "absent"
            born_on = tbody[3].find_all("td")[1].text.rstrip()
            place = tbody[4].find_all("td")[1].text.rstrip()
            timezone = tbody[5].find_all("td")[1].text.rstrip()
            data_source = tbody[6].find_all("td")[2].text.rstrip()
            rodden_rating = tbody[7].find_all("td")[2].text[-3:-1].rstrip()
            collector = tbody[7].find_all("td")[3].text.split(":")[1].replace(" ", "").rstrip()
            astrology_date = tbody[10].find_all("td")[1].text.rstrip()
            categories = get_categories(soup_href)
            list = [name, gender, birthname, born_on, place, timezone, data_source, rodden_rating, collector,
                    astrology_date]
            list = list + categories
            with open("database.csv", "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(list)
        except:
            pass



def download(url):
    response = requests.get(url, headers=headers)
    return response.text


if __name__ == '__main__':
    start_time = datetime.now()
    with multiprocessing.Pool(len(urls)) as pool:
        pool.map(get_full_info, urls)
    print(datetime.now() - start_time)