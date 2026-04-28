from dataclasses import dataclass
from datetime import datetime, date
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import sys
import lxml.etree as ET
from io import StringIO


TIME_FORMAT = "%Y-%m-%d"

@dataclass
class Competition:
    name: str
    compDate: datetime.date
    club: str
    url: str

@dataclass
class Result:
    name: str
    club: str
    bw: float
    squat: float
    bench: float
    deadlift: float
    total: float
    points: float

parser = ET.HTMLParser()

def getCompetitions(contents, domain) -> list[Competition]:
    competitions = []
    html = ET.parse(StringIO(contents), parser)
    for text in html.xpath("//*[@id=\"root\"]/div/div[2]/div/div/section/div[2]/table/tbody/tr"):
        a_tag = list(text.iter("a"))
        div_tag = list(text.iter("div"))
        link = a_tag[0].attrib["href"]
        url = domain + link
        name = a_tag[0].text
        club = div_tag[2].text
        compDate = datetime.strptime(div_tag[7].text[0:10], TIME_FORMAT).date()
        competitions.append(Competition(name, compDate, club, url))
    return competitions

def getResultList(driver: webdriver.Chrome, url: str) -> list[Result]:
    contents = getUrlContents(driver, url, wait_for_tag="tbody")
    if contents == "":
        return []
    html = ET.parse(StringIO(contents), parser)
    results = []
    for text in html.xpath("//*[@id=\"root\"]/div/div[2]/div/div/section/div/table/tbody/tr"):
        info = list(text.iter("div"))
        if len(info) == 9:
            name = info[1].findtext("a")
            club = info[2].text
            bw = float(info[3].text)
            squat = float(info[4].text)
            bench = float(info[5].text)
            deadlift = float(info[6].text)
            total = float(info[7].text)
            points = float(info[8].text)
        else:
            name = info[1].findtext("a")
            club = info[2].text
            bw = float(info[3].text)
            squat = 0.0
            bench = float(info[4].text)
            deadlift = 0.0
            total = float(info[4].text)
            points = float(info[5].text)
        results.append(Result(name, club, bw, squat, bench, deadlift, total, points))
    return results

def getUrlContents(driver: webdriver.Chrome, url: str, wait_for_tag: str) -> str:
    driver.get(url)
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, wait_for_tag)))
    except TimeoutException:
        return ""
    return driver.page_source

pageIndex = 1
domain = "https://data.styrkelyft.se"
baseCompUrl = f"{domain}/competitions"
listingParameters = f"?group=COMPLETED&pageIndex="
listingBaseUrl = f"{baseCompUrl}{listingParameters}"

startDate = sys.argv[1]
endDate = sys.argv[2]
filteredClub = sys.argv[3]
output_file = sys.argv[4]
results = []
driver = webdriver.Chrome()

while True:
    contents = getUrlContents(driver, listingBaseUrl + str(pageIndex), wait_for_tag="span")
    competitions = getCompetitions(contents, domain)
    scanned_one = False
    for c in competitions:
        if c.compDate < datetime.strptime(startDate, TIME_FORMAT).date():
            break
        elif c.compDate > datetime.strptime(endDate, TIME_FORMAT).date():
            continue
        else:
            formattedDate = datetime.strftime(c.compDate, TIME_FORMAT)
            results.append({"name": c.name, "date": formattedDate, "arranging_club": c.club, "results": getResultList(driver, c.url)})
            scanned_one = True
    else:
        pageIndex += 1
        continue
    break
header = "name,bw,class,squat,bench,deadlift,total,points,benchpoints,date,compname\n"
lifter_rows = []
for comp in results:
    for r in comp["results"]:
        if r.club == filteredClub:
            lifter_rows.append(f"{r.name},{r.bw},,{r.squat},{r.bench},{r.deadlift},{r.total},{r.points},,{comp['date']},{comp['name']}\n")

if output_file:
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header)
        f.writelines(lifter_rows)
else:
    for row in lifter_rows:
        print(row)

driver.quit()