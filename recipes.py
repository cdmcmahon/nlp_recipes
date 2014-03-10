import json
import nltk
import re, string
import urllib2
from BeautifulSoup import BeautifulSoup as Soup
import BeautifulSoup

# response = urllib2.urlopen('http://allrecipes.com/Recipe/Lentils-and-Rice-with-Fried-Onions-Mujadarrah/Detail.aspx?soid=carousel_0_rotd&prop24=rotd')

#-------------------------------------------------------------------------------
# Constants and Variables
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
# This part gets a list of kitchen tools by parsing the following wikipedia pages:
# List of food preparation utensils
# Cookware and bakeware
#-------------------------------------------------------------------------------


# Utensils
def getUtensils():
  utensils_response = urllib2.urlopen('http://en.wikipedia.org/wiki/List_of_food_preparation_utensils')
  utensils_html = utensils_response.read()
  utensils_soup = Soup(utensils_html)
  utensils = []
  i=1
  for table in utensils_soup.findAll('table'):
    if(i==1):
      for a in table.findAll('tr'):
        link = a.find('th').find('a')
        if(link):
          utensils.append(link.string)
    i = i+1
  return utensils

# Cookware and bakeware
def getCookware():
  i = 0
  cookware_response = urllib2.urlopen('http://en.wikipedia.org/wiki/Cookware_and_bakeware')
  cookware_html = cookware_response.read()
  cookware_soup = Soup(cookware_html)
  cookware = []
  # relevant_section_head = cookware_soup.find(id="List_of_cookware_and_bakeware")
  # relevant_section_h2 = relevant_section_head.parent
  # relevant_section = relevant_section_h2.previous_sibling
  for ul in cookware_soup.findAll('ul'):
    if(i==22):
      for li in ul.findAll('li'):
        if(li.string):
          item = re.sub(r'\([^)]*\)', '', li.string)
          cookware.append(item)
        else:
          link = li.find('a')
          cookware.append(link.string)
    i = i+1
  return cookware

# Open the page from AllRecipes.com given a URL
def RetrieveInfo():
  recipe_code = RequestURL()
  recipe_soup = Soup(recipe_code)
  recipe_title = ExtractTitle(recipe_soup)
  recipe_ingred = ExtractIngredients(recipe_soup)
  recipe_time = ExtractTime(recipe_soup)
  recipe_dir = ExtractDirections(recipe_soup)

  recipe_info = [recipe_title, recipe_time, recipe_ingred, recipe_dir]
  return recipe_info

def RequestURL():
  print("\n")
  pageurl = raw_input("Please input the URL of a recipe from AllRecipes.com: ")
  print("\n")
  return RetrievePage(pageurl)

def RetrievePage(pageurl):
  recipes_page = urllib2.urlopen(pageurl)
  recipes_html = recipes_page.read()
  return recipes_html

def ExtractTitle(recipe_soup):
  listing = recipe_soup.find('span', id="lblTitle")
  title = listing.getText()
  return title

def ExtractIngredients(recipe_soup):
  recipe_items = []
  for listing in recipe_soup.findAll('p', itemprop="ingredients"):
    amount = listing.find('span', id="lblIngAmount")
    if amount:
      amounttext = amount.getText()
    else:
      amounttext = ''
    ingred = listing.find('span', id="lblIngName")
    if ingred:
      ingredtext = ingred.getText()
    else:
      amounttext = ''
    recipe_items.append([amounttext, ingredtext])
  return recipe_items

def ExtractTime(recipe_soup):
  listing = recipe_soup.find('span', id="prepMinsSpan")
  preptime = listing.getText()
  listing = recipe_soup.find('span', id="cookMinsSpan")
  cooktime = listing.getText()
  listing = recipe_soup.find('span', id="totalMinsSpan")
  totaltime = listing.getText()
  return [preptime, cooktime, totaltime]

def ExtractDirections(recipe_soup):
  desc = recipe_soup.find('ol')
  directions = desc.getText()

  sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
  directions = sent_detector.tokenize(directions)
  return directions

def PrintInfo(recipe_info):
  print("\n####" + recipe_info[0] + "####" + '\n')
  print("==Recipe Time==")
  print("  Prep Time:  " + recipe_info[1][0])
  print("  Cook Time:  " + recipe_info[1][1])
  print("  Total Time: " + recipe_info[1][2] + '\n')

  print("==Ingredients==")
  for item in recipe_info[2]:
    print("  " + item[1] + " (" + item[0] +")")
  print("\n==Directions==")
  for sentence in recipe_info[3]:
    print("-" + sentence)
  print('\n')
  return

utensils = getUtensils()
cookware = getCookware()
recipe = RetrieveInfo()

print("Utensils:")
print utensils
print('\nCookware:')
print cookware
PrintInfo(recipe)



