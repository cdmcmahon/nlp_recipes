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

MEAT = ["bacon", "beef", "buffalo", "bison", "breast", "chick", "chuck", 
        "duck", "filet", "gizzard", "goos", "ground", "grous", "ham", "hen", "lamb", "liv", 
        "lobst", "mignon", "mutton", "pheas", "pork", "rib", "ribeye", "chop", "quail", "roast", 
        "skinless", "steak", "strips", "turkey", "fish", "scallop", "shrimp", "veal", "venison"]

WEIGHT = dict(bacon = .66, breast = 6, chicken = 64, chop = 4, duck = 64, turkey = 160) #in ounces
NONVEGAN = ["butter", "cheese"]

VEGANCHANGE = dict(beefbouillon = "vegetable bouillon", beefbroth = "french onion soup", beefstock = "vegetable stock", 
                    chickenbouillon = "vegetable bouillon", chickenbroth = "french onion soup", chickenstock = "vegetable stock", 
                    hamstock = "vegetable stock", fishstock = "vegetable stock",
                    vealstock = "vegetable stock", vealbouillon = "vegetable bouillon", shrimpbouillon = "shrimp bouillon")

DESCRIPTORS = ["fat-free", "thick", "half", "halves", "boneless", "skinless", ",", "strip", "flank", "cut", "thin", "long",
              "into", "in", "on", "with"]

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
    self.removePunct()
    self.removeDescriptors()
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
    else:
      self.time.append("")
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
    else:
      self.time.append("")
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
    else:
      self.time.append("")
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

  def veganize(self):
    #if already vegan, do nothing
    if "vegan" in self.title or "Vegan" in self.title:
      return
    #else, make it vegan
    self.title = "Vegetarian " + self.title
    counter = 0
    for ingredient in self.ingredients:
      #remove information in parentheses
      ingredient[1] = self.removeParen(ingredient[1])
      ingred_list = ingredient[1].split()
      checker = 0
      new_weight = 0
      #change butter, cheese, etc into vegan options
      for item in NONVEGAN:
        if item in ingredient[1]:
          ingredient[1] = "vegan " + ingredient[1]
      #change broths, stocks, etc. into vegan options
      if ingredient[1].replace(" ", "") in VEGANCHANGE.keys():
        for entry in range(0,len(self.directions)):
          self.directions[entry] = self.directions[entry].replace(ingredient[1], VEGANCHANGE[ingredient[1].replace(" ", "")])
        ingredient[1] = VEGANCHANGE[ingredient[1].replace(" ", "")]
      #replace meat with tofu
      for item in ingred_list:
        item = st.stem(item)
        if item in MEAT:
          if item in WEIGHT.keys():
            print(ingredient[1])
            new_weight = int(ingredient[0])*WEIGHT[item]
          else:
            new_weight = 0
          checker+=1
      if checker==len(ingred_list):
        self.updateDirections(ingredient[1], ingred_list)
        if new_weight>0:
          ingredient[1] = "tofu"
          ingredient[0] = str(new_weight) + " ounces"
      checker+= 1
    return

  def updateDirections(self, fullingred, ingred):
    if fullingred[-1]=='s':
      ingred.insert(0, fullingred[:len(fullingred)-1])
    ingred.insert(0, fullingred)
    for entry in range(0,len(self.directions)):
      for item in ingred:
        self.directions[entry] = self.directions[entry].replace(item, "tofu")
        self.directions[entry] = self.directions[entry].replace("meat", "tofu")
        self.directions[entry] = self.directions[entry].replace("them", "it")
        self.directions[entry] = self.directions[entry].replace("tofus", "tofu")
    return

  def removeParen(self, text):
    p = re.compile(r'\([^)]*\)')
    text = re.sub(p, '', text)
    if text[0]==' ':
      text = text[1:]
    return text

  def removePunct(self):
    for entry in self.ingredients:
      entry[1] = re.sub(r'[^\w\s]','',entry[1])
    return

  def removeDescriptors(self):
    for entry in range(0,len(self.ingredients)):
      self.ingredients[entry][1] = self.removeDescHelper(self.ingredients[entry][1].split())
    return

  def removeDescHelper(self, item_list):
    for desc in DESCRIPTORS:
      if desc in item_list:
        item_list.remove(desc)
    return " ".join(item_list)

  def __str__(self):
    dir = ("\n####" + self.title + "####" + '\n'
    + "\n#==========================================#\n"
    + "#  Recipe Time\n"
    + "#==========================================#\n"
    + "-->Prep Time:  " + self.time[0] + '\n'
    + "-->Cook Time:  " + self.time[1] + '\n'
    + "-->Total Time: " + self.time[2] + '\n'
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


def Initialize():
  print("\nWhat transformation would you like to perform?")
  print(" [V] Create a vegan option from an existing recipe")
  print(" [E] Exit")
  request = raw_input("-->")
  request = request.lower()
  if not request in ['v', 'e']:
    return Initialize()
  if request=='v':
    recipe = Recipe()
    recipe.veganize()
    print recipe
  if request=='e':
    print('\n')
    return
  return Initialize()


#-------------------------------------------------------------------------------
# Calling the functions defined about
#-------------------------------------------------------------------------------
#utensils = getUtensils()
#cookware = getCookware()

Initialize()



