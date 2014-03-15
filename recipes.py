import json
import nltk
from nltk.stem.lancaster import LancasterStemmer
st = LancasterStemmer()
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

# Food Preparation Methods
def getTechniques():
  i = 0
  technique_response = urllib2.urlopen('http://chasingdelicious.com/kitchen-101-cooking-methods/')
  technique_html = technique_response.read()
  technique_soup = Soup(technique_html)
  techniques = []
  for item in technique_soup.findAll('h3'):
    if i<18:
      method = item.getText()
      if '/' in method:
        method2 = method[method.index('/')+1:]
        method = method[:method.index('/')]
        method = st.stem(method)
        techniques.append(method)
        method2 = st.stem(method2)
        techniques.append(method2)
      else:
        method = st.stem(method)
        techniques.append(method)
    i+= 1

  return techniques


#-------------------------------------------------------------------------------
# Class related to the specific recipe.
#   -Requests URL for recipe
#   -Retrieves page in HTML
#   -Parses HTML for specific information (i.e. Title, Cook Time, Ingredients, etc)
#-------------------------------------------------------------------------------
class Recipe:
  def __init__(self):
    self.pageurl = ""
    self.recipe_html = ""
    self.recipe_soup = ""
    self.title = ""
    self.ingredients = []
    self.time = []
    self.directions = []
    self.method = ""
    self.RetrieveInfo()

  def RetrieveInfo(self):
    self.ParsePage()
    #====retrieve specific items from the page====
    self.ExtractTitle()
    self.ExtractIngredients()
    self.ExtractTime()
    self.ExtractDirections()
    self.ExtractMethod(getTechniques())
    return

  def ParsePage(self):
    #====request page URL====
    print('\n')
    self.pageurl = raw_input("Please input the URL of a recipe from ALLRecipes.com: ")
    print('\n')
    #====convert the page to HTML that can be handled by Beautiful Soup====
    page = urllib2.urlopen(self.pageurl)
    self.recipe_html = page.read()
    self.recipe_soup = Soup(self.recipe_html)
    return

  def ExtractTitle(self):
    listing = self.recipe_soup.find('span', id="lblTitle")
    self.title = listing.getText()
    return

  def ExtractIngredients(self):
    for listing in self.recipe_soup.findAll('p', itemprop="ingredients"):
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
      self.ingredients.append([amounttext, ingredtext])
    return

  def ExtractTime(self):
    #get the prep time minutes and hours
    listingM = self.recipe_soup.find('span', id="prepMinsSpan")
    listingH = self.recipe_soup.find('span', id="prepHoursSpan")
    if listingM and listingH:
      preptimeM = listingM.getText()
      preptimeH = listingH.getText()
      preptime = preptimeH+","+preptimeM
      self.time.append(preptime)
    elif listingM:
      preptimeM = listingM.getText()
      self.time.append(preptimeM)
    elif listingH:
      preptimeH = listingH.getText()
      self.time.append(preptimeH)
    #get the cook time minutes and hours
    listingM = self.recipe_soup.find('span', id="cookMinsSpan")
    listingH = self.recipe_soup.find('span', id="cookHoursSpan")
    if listingM and listingH:
      cooktimeM = listingM.getText()
      cooktimeH = listingH.getText()
      cooktime = cooktimeH+","+cooktimeM
      self.time.append(cooktime)
    elif listingM:
      cooktimeM = listingM.getText()
      self.time.append(cooktimeM)
    elif listingH:
      cooktimeH = listingH.getText()
      self.time.append(cooktimeH)
    #get the total time minutes and hours
    listingM = self.recipe_soup.find('span', id="totalMinsSpan")
    listingH = self.recipe_soup.find('span', id="totalHoursSpan")
    if listingM and listingH:
      totaltimeM = listingM.getText()
      totaltimeH = listingH.getText()
      totaltime = totaltimeH+","+totaltimeM
      self.time.append(totaltime)
    elif listingM:
      totaltimeM = listingM.getText()
      self.time.append(totaltimeM)
    elif listingH:
      totaltimeH = listingH.getText()
      self.time.append(totaltimeH)
    return

  def ExtractDirections(self):
    desc = self.recipe_soup.find('ol')
    directions = desc.getText()
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    self.directions = sent_detector.tokenize(directions)
    return

  def ExtractMethod(self, methodlist):
    for sentence in self.directions:
      sentence = sentence.split()
      for token in sentence:
        if '.' in token:
          index = token.index('.')
          token2 = token[index+1:]
          temptoken2 = st.stem(token2)
          token = token[:index]
          temptoken = st.stem(token)
          if unicode(temptoken2) in methodlist:
            self.method = token2
            return
        else:
          temptoken = st.stem(token)
        if unicode(temptoken) in methodlist:
          self.method = token
          return

  def __str__(self):
    dir = ("\n####" + self.title + "####" + '\n\n'
    + "\n#==========================================#\n"
    + "#  Recipe Time\n"
    + "#==========================================#\n"
    + "-->Prep Time:  " + self.time[0] + '\n'
    + "-->Cook Time:  " + self.time[1] + '\n'
    + "-->Total Time: " + self.time[2] + '\n\n'
    + '\n#==========================================#\n'
    + "#  Ingredients\n"
    + "#==========================================#\n")

    for item in self.ingredients:
        dir = dir + "-->" + item[1] + " (" + item[0] + ")\n"

    dir = (dir + "\n#==========================================#\n"
    + "#  Directions\n"
    + "#==========================================#\n")

    for i in range(1, len(self.directions)+1):
        dir = dir + " " + str(i) + ".) " + self.directions[i-1] + '\n'

    dir = (dir + "\n#==========================================#\n"
    + "#  Preparation Technique\n"
    + "#==========================================#\n"
    + "-->" + self.method + '\n\n')

    return dir

##  def Print(self):
##    print("\n####" + self.title + "####" + '\n')
##    print("\n#==========================================#")
##    print("#  Recipe Time")
##    print("#==========================================#")
##    print("-->Prep Time:  " + self.time[0])
##    print("-->Cook Time:  " + self.time[1])
##    print("-->Total Time: " + self.time[2] + '\n')
##    print("\n#==========================================#")
##    print("#  Ingredients")
##    print("#==========================================#")
##    for item in self.ingredients:
##      print("-->" + item[1] + " (" + item[0] + ")")
##    print("\n#==========================================#")
##    print("#  Directions")
##    print("#==========================================#")
##    i = 1
##    for sentence in self.directions:
##      print("  "+str(i) + ".) " + sentence)
##      i+= 1
##    print("\n#==========================================#")
##    print("#  Preparation Technique")
##    print("#==========================================#")
##    print("-->" + self.method + '\n')
##    return


#-------------------------------------------------------------------------------
# Calling the functions defined about
#-------------------------------------------------------------------------------
utensils = getUtensils()
cookware = getCookware()
recipe = Recipe()
#recipe.RetrieveInfo()
print recipe

print("Utensils:")
print utensils
print('\nCookware:')
print cookware



