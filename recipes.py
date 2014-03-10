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
def RequestURL():
  print("\n")
  pageurl = raw_input("Please input the URL of a recipe from AllRecipes.com: ")
  print("\n")
  return RetrievePage(pageurl)

def RetrievePage(pageurl):
  recipes_page = urllib2.urlopen(pageurl)
  recipes_html = recipes_page.read()
  return recipes_html
  #return ExtractIngredients(recipes_html)

# Extract the ingredients and quantities from the HTML and store them as tuples in an array
def ExtractIngredients(pagehtml):
  recipe_soup = Soup(pagehtml)
  recipe_amounts = []
  recipe_ingred = []
  for listing in recipe_soup.findAll('span', id="lblIngAmount"):
    recipe_amounts.append(listing.getText())
  for listing in recipe_soup.findAll('span', id="lblIngName"):
    recipe_ingred.append(listing.getText())
  recipe_items = zip(recipe_amounts, recipe_ingred)
  return recipe_items

def GetIngredients():
    return ExtractIngredients(RequestURL())

utensils = getUtensils()
cookware = getCookware()
recipe = GetIngredients()

print("Utensils:")
print utensils
print('\nCookware:')
print cookware
print('\nIngredients')
print recipe