from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import json


my_file = open("out/itemUrlList.txt", "r")
data = my_file.read()
itemLinks = data.split("\n")

itemDataList = []


def getItemData(url):
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    infoBoxTable = soup.find("table", "infoboxtable").tbody

    itemData = {"wikiLink": url}

    baseUrl = "https://riskofrain2.fandom.com"

    imageEl = infoBoxTable.contents[2].td.img
    if "data-src" in imageEl:
        imageUrl = imageEl["data-src"]
    else:
        imageUrl = imageEl["src"]
    itemData["image"] = imageUrl

    for tr in infoBoxTable.children:
        if tr == "\n":
            continue

        infoBoxNameEl = tr.find("th", "infoboxname")
        if infoBoxNameEl and tr.text.strip() != "Stats":
            # Skip first element thumbnail pic, then get the Item Text from contents
            nameEl = infoBoxNameEl.contents[1]

            if len(nameEl.contents) > 1:
                name = nameEl.contents[1].text.strip()
                dlc = nameEl.contents[0].a["title"]
                itemData["dlc"] = dlc
            else:
                name = nameEl.text.strip()

            itemData["name"] = name
            continue

        infoBoxCaptionEl = tr.find("td", "infoboxcaption")
        if infoBoxCaptionEl:
            shortDescription = infoBoxCaptionEl.contents[0].strip()
            itemData["shortDescription"] = shortDescription
            continue

        infoBoxDescEl = tr.find("td", "infoboxdesc")
        if infoBoxDescEl:
            description = infoBoxDescEl.text.strip()
            itemData["description"] = description
            continue

        isCorruptedEl = tr.find("td", string=re.compile("Corrupted"))
        if isCorruptedEl:
            corrupted = tr.contents[3].contents[1].contents[2].text.strip()
            itemData["corrupted"] = corrupted
            continue

        isCooldownEl = tr.find("td", string=re.compile("Cooldown"))
        if isCooldownEl:
            cooldown = tr.contents[3].text.strip()
            itemData["cooldown"] = cooldown
            continue

        isRarityEl = tr.find("td", string=re.compile("Rarity"))
        if isRarityEl:
            rarity = tr.contents[3].contents[0].text.strip()

            # Has boss name
            if len(tr.contents[3].contents) > 2:
                boss = tr.contents[3].contents[2]
                itemData["dropsFrom"] = {
                    "source": boss.text.strip(),
                    "url": baseUrl + boss["href"],
                }

            itemData["itemRarity"] = rarity
            continue

        isCategoryEl = tr.find("td", string=re.compile("Category"))
        if isCategoryEl:
            categoryList = tr.contents[3].findAll("a")
            categoryList = list(
                map(lambda category: category.text.strip(), categoryList)
            )
            itemData["category"] = categoryList
            continue

        isUnlockEl = tr.find("td", string=re.compile("Unlock"))
        if isUnlockEl:
            unlockName = tr.contents[3].text.strip()
            unlockWikiLink = baseUrl + tr.contents[3].a["href"]

            unlockPage = urlopen(unlockWikiLink)
            unlockHtml = page.read().decode("utf-8")
            unlockSoup = BeautifulSoup(html, "html.parser")
            unlockDesc = unlockSoup.find("td", "infoboxdesc").text.strip()

            unlockInfo = {
                "name": unlockName,
                "link": unlockWikiLink,
                "description": unlockDesc,
            }

            itemData["unlock"] = unlockInfo
            continue

        isIdEl = tr.find("td", string=re.compile("ID"))
        if isIdEl:
            itemId = tr.contents[3].text.strip()
            itemData["id"] = itemId
            continue

        if tr.text.strip() == "Stats":
            stats = []
            for statRow in tr.next_siblings:
                if statRow.text in [
                    "\n",
                    "Stats\n",
                    "\nStat\n\nValue\n\nStack\n\nAdd\n",
                ]:
                    continue

                stat = {
                    "stat": statRow.contents[1].text.strip(),
                    "value": statRow.contents[3].text.strip(),
                    "stackType": statRow.contents[5].text.strip(),
                    "stackValue": statRow.contents[7].text.strip(),
                }
                stats.append(stat)

            itemData["stats"] = stats
            break
    return itemData


for i in range(0, len(itemLinks)):
    itemLink = itemLinks[i]
    print(f"{i+1}/{len(itemLinks)} - {itemLink}")
    itemDataList.append(getItemData(itemLink))

jsonItemData = json.dumps(itemDataList)

with open("out/itemData.json", "w") as f:
    f.write(jsonItemData)
