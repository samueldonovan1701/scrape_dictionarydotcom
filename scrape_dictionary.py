import json
import html
import codecs
import string
import requests
from bs4 import BeautifulSoup

dictionary = {}
counts = {}

for letter in string.ascii_lowercase:
    print("")
    counts[letter] = 0
    for n in range(1,1000000):
        print(f"\rGetting list of words that start with '{letter}' Page {n} "+\
              f"({counts[letter]}) ({len(dictionary)} total)        ", end="", flush=True)

        url = f"https://www.dictionary.com/list/{letter}/{n}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")

        ul = soup.main.find("ul")
        if ul is None:
            break
        else:
            for child in ul.children:
                key = child.a.get_text()
                dictionary[key] = {"url":child.a['href']}
                counts[letter] += 1
print(f"\rGetting list of words that start with '{letter}' Page {n} "+\
        f"({counts[letter]}) ({len(dictionary)} total)        ", end="", flush=True)
print("")

print("")
i = 0
j = 0
k = 0
letter = 'a'
count = counts[letter]
dictlen = len(dictionary)
for key in dictionary: #dictionary:
    i += 1
    j += 1
    if j > count:
        j = 0
        k += 1
        letter = list(counts.keys())[k]
        count = counts[letter]
    print_key = key   
    if len(print_key) > 20:
        print_key = print_key[0:17]+"..."
    print(f"\rGetting definition for "+f"{print_key: <20} ('{letter}' {j}/{count}) ({i}/{dictlen})    ", end="")
    
    url = dictionary[key]["url"]
    del dictionary[key]["url"]
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    for usage in soup.main.header.next_siblings:
        
        try:
            type = usage.find(class_="luna-pos").get_text()
            if type.endswith(','):
                type = type[:-1]

            inflections = []
            for inflection in usage.find_all(class_="luna-inflected-form"):
                inflection = inflection.get_text()
                if inflection.endswith((',', '.')):
                    inflections.append(inflection[:-1])
                else:
                    inflections.append(inflection)

            definitions = []
            examples = []
            for definition_list in usage.find_all("ol"):
                for definition in definition_list.find_all("li"):
                    text = definition.p.get_text()[:-1].split(": ")

                    definitions.append(text[0])

                    if len(text) < 2:
                        examples.append([])
                    else:
                        examples.append(text[1].split(';'))

            dictionary[key][type] = {
                "inflections": inflections,
                "definitions": definitions,
                "examples": examples
            }
        except:
            dictionary[key]["special"] = {
                "inflections": [],
                "definitions": [soup.main.header.get_text()],
                "examples": []
            }
print(f"\rGetting definition for "+f"{print_key: <20} ('{letter}' {j}/{count}) ({i}/{dictlen})    ", end="")
print("")

print("Saving to file")
with open("dictionary.json", "w") as file:
    json.dump(dictionary, file, indent=4)