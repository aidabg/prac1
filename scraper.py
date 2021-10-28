import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd


# Creació del dataframe amb 8 columnes
df = pd.DataFrame(columns=["Category", "Business Name", "Opinions", 
                           "TrustPilot Score", "Subcategories", 
                           "Adress", "City", "ZipCode"])

# Lloc web d'on obtenir les diferents categories en que està organitzat
site = "https://es.trustpilot.com/categories"

# Es fa la request i es converteix a un objecte de BeautifulSoup
page = requests.get(site)
soup = BeautifulSoup(page.content)

# Iteració per totes les categories principals del lloc web
for category in soup.find_all(class_="categories_categoryListObject__3WjQQ"):
  
  # S'afegeixen 5 segons de pausa entre requests
  time.sleep(5)
  
  # Obtenció del nom de la categoria
  category_name = category.find(class_="categories_categoryListItem__1dO4P").string
  
  # Obtenció de l'enllaç de la categoria
  link = category.a.get("href")
  full_link = "https://es.trustpilot.com" + link

  # Es fa la request i es converteix a un objecte de BeautifulSoup
  page = requests.get(full_link)
  soup = BeautifulSoup(page.content)

  # Missatge que es mostra per pantalla per informar del progrés
  print(f"Extracting data from '{category_name}' category...")

  # Iteració per totes les "targetes" de negocis de la pàgina
  for card in soup.find_all(class_="styles_businessUnitCard__contentContainer__12iZd"):
    
    # Obtenció del nom del negoci
    name = card.find(class_="styles_businessTitle__1IANo").string

    # Obtenció del nombre d'opinions i la puntuació de TrustPilot
    rating = card.find(class_="styles_textRating__19_fv")
    match = re.search(r"\d*\.?\d*", str(rating)[38:])
    opinions = match.group()
    score = str(rating)[-9:-6].strip("->")

    # Obtenció de les subcategories
    categories = card.find(class_="styles_categories__c4nU-")
    subcategory = ""
    for span in categories.findChildren("span"):
      if span.string != "·" and span.string != None:
        subcategory = (subcategory + "\n" + span.string).strip("\n")

    # Obtenció de la localització (adreça, ciutat i codi postal)
    location = card.find(class_="styles_location__3JATO")
    if location:
      adress = location.span.string
      zipcode = location.find(class_="styles_locationZipcodeAndCity__2RbYT").span.string
      city = location.find(class_="styles_locationZipcodeAndCity__2RbYT").select('span')[1].string
    # Si no s'inclou la informació de la localització es posa el valor None
    else:
      adress = None
      zipcode = None
      city = None

    # Creació de la fila amb totes les dades obtingudes
    row = {'Category':category_name, 'Business Name':name, 'Opinions':opinions,
          'TrustPilot Score':score, 'Subcategories':subcategory, 
          'Adress':adress, 'City':city, 'ZipCode':zipcode}

    # Afegeix la fila al dataframe
    df = df.append(row, ignore_index=True)

# Conversió del dataframe a format csv
df.to_csv("data.csv", sep=';', index=False, encoding="utf-8")

