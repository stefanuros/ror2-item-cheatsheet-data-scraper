from bs4 import BeautifulSoup
from urllib.request import urlopen

url = "https://riskofrain2.fandom.com/wiki/Items"
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html, "html.parser")

itemPageLinks = []

tableRows = soup.find("div", "thumb tright thumbinner")[0].table.tbody

for tableRow in tableRows:
  if(tableRow == '\n'):
    continue
  for tableData in tableRow.children:
    if(tableData == '\n'):
      continue
    link = tableData.contents[0].contents[0]['href']
    itemPageLinks.append(link)

itemPageLinks = list(map(lambda link: f"https://riskofrain2.fandom.com{link}", itemPageLinks))
linkString = "\n".join(itemPageLinks)

with open('out/itemUrlList.txt', 'w') as f:
  f.write(linkString)


