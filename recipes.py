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
        "duck", "filet", "gizzard", "goos", "grous", "ham", "hen", "lamb", "liv", 
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

QUANTITIES = ["teaspoon", "dessertspoon", "tablespoon", "ounce", "fluid ounce", "cup", "pint", "pinch", "quart", "gallon", "liter"]
ABR_QUANTITIES = dict(tsp = "teaspoon", tbsp = "tablespoon", floz = "fluid ounce", oz = "ounce", pt = "pint", qt = "quart", gal = "gallon")

#-------------------------------------------------------------------------------
# This part gets a list of kitchen tools by parsing the following wikipedia pages:
# List of food preparation utensils
# Cookware and bakeware
#-------------------------------------------------------------------------------


# Utensils
def getUtensils():
  utensils_response = urllib2.urlopen("https://en.wikipedia.org/w/index.php?title=Category:Cooking_utensils&gettingStartedReturn=true")
  utensils_html = utensils_response.read()
  utensils_soup = Soup(utensils_html)
  utensils = []
  i=1
  for li in utensils_soup.findAll('li'):
    if i>6 and i<102:
      text = removeParen(li.getText().lower())
      utensils.append(text)
    i = i+1
  #grab utensils from another page
  utensils_response = urllib2.urlopen('http://en.wikipedia.org/wiki/List_of_food_preparation_utensils')
  utensils_html = utensils_response.read()
  utensils_soup = Soup(utensils_html)
  utensils2 = []
  i = 1
  for table in utensils_soup.findAll('table'):
    if(i==1):
      for a in table.findAll('tr'):
        link = a.find('th').find('a')
        if(link):
          utensils2.append(removeParen(link.string.lower()))
    i+= 1
  #combine the two lists
  all_utensils = list(set(utensils) - set(utensils2)) + utensils2
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
          cookware.append(removeParen(item.lower()))
        else:
          link = li.find('a')
          cookware.append(removeParen(link.string.lower()))
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

def removeParen(text):
  p = re.compile(r'\([^)]*\)')
  text = re.sub(p, '', text)
  if text[0]==' ':
    text = text[1:]
  return text


#-------------------------------------------------------------------------------
# Class related to the specific recipe.
#   -Requests URL for recipe
#   -Retrieves page in HTML
#   -Parses HTML for specific information (i.e. Title, Cook Time, Ingredients, etc)
#-------------------------------------------------------------------------------
class Recipe:
  def __init__(self):
    print("Initializing...")
    self.pageurl = ""
    self.recipe_html = ""
    self.recipe_soup = ""
    self.recipe_info = dict(method= "", ingredients= [], tools= [], time = dict())
    self.title = ""
    self.ingredients = []

    self.cooking_tools = getUtensils() + getCookware()

    self.directions = []
    self.RetrieveInfo()
    print(self.recipe_info)

  def RetrieveInfo(self):
    self.ParsePage()
    #====retrieve specific items from the page====
    print("Preparing to retrieve information...")
    self.ExtractTitle()
    self.ExtractIngredients()
    self.ExtractTime()
    self.ExtractDirections()
    print("Normalizing information...")
    self.Normalize()
    self.removeDescriptors()
    self.ExtractMethod(getTechniques())
    self.ExtractTools()
    return

  def ParsePage(self):
    #====request page URL====
    print('\n')
    self.pageurl = raw_input("Please input the URL of a recipe from ALLRecipes.com: ")
    print('\n')
    #====convert the page to HTML that can be handled by Beautiful Soup====
    print("Loading page...")
    page = urllib2.urlopen(self.pageurl)
    print("Converting page...")
    self.recipe_html = page.read()
    self.recipe_soup = Soup(self.recipe_html)
    return

  def ExtractTitle(self):
    print("Extracting recipe...")
    listing = self.recipe_soup.find('span', id="lblTitle")
    self.title = listing.getText()
    return

  def ExtractIngredients(self):
    print("Extracting recipe ingredients...")
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
    print("Extracting preparation time...")
    listingM = self.recipe_soup.find('span', id="prepMinsSpan")
    listingH = self.recipe_soup.find('span', id="prepHoursSpan")
    if listingM and listingH:
      preptimeM = listingM.getText()
      preptimeH = listingH.getText()
      preptime = preptimeH+","+preptimeM
      self.recipe_info['time']['preptime'] = preptime
    elif listingM:
      preptimeM = listingM.getText()
      self.recipe_info['time']['preptime'] = preptimeM
    elif listingH:
      preptimeH = listingH.getText()
      self.recipe_info['time']['preptime'] = preptimeH
    else:
      self.recipe_info['time']['preptime'] = ""
    #get the cook time minutes and hours
    print("Extracting cooking time...")
    listingM = self.recipe_soup.find('span', id="cookMinsSpan")
    listingH = self.recipe_soup.find('span', id="cookHoursSpan")
    if listingM and listingH:
      cooktimeM = listingM.getText()
      cooktimeH = listingH.getText()
      cooktime = cooktimeH+","+cooktimeM
      self.recipe_info['time']['cooktime'] = cooktime
    elif listingM:
      cooktimeM = listingM.getText()
      self.recipe_info['time']['cooktime'] = cooktimeM
    elif listingH:
      cooktimeH = listingH.getText()
      self.recipe_info['time']['cooktime'] = cooktimeH
    else:
      self.recipe_info['time']['cooktime'] = ""
    #get the total time minutes and hours
    print("Extracting total time...")
    listingM = self.recipe_soup.find('span', id="totalMinsSpan")
    listingH = self.recipe_soup.find('span', id="totalHoursSpan")
    if listingM and listingH:
      totaltimeM = listingM.getText()
      totaltimeH = listingH.getText()
      totaltime = totaltimeH+","+totaltimeM
      self.recipe_info['time']['totaltime'] = totaltime
    elif listingM:
      totaltimeM = listingM.getText()
      self.recipe_info['time']['totaltime'] = totaltimeM
    elif listingH:
      totaltimeH = listingH.getText()
      self.recipe_info['time']['totaltime'] = totaltimeH
    else:
      self.recipe_info['time']['totaltime'] = ""
    return

  def ExtractDirections(self):
    print("Extracting recipe instructions...")
    desc = self.recipe_soup.find('ol')
    directions = desc.getText()
    #split and normalize directions
    Enders = re.compile('[.!?]')
    self.directions = Enders.split(directions)
    for i in range(0,len(self.directions)):
      self.directions[i] = self.directions[i].split()
      self.directions[i] = " ".join(self.directions[i])
    if not self.directions[-1]:
      self.directions = self.directions[:len(self.directions)-1]
    return

  def ExtractMethod(self, methodlist):
    print("Extracting cooking method...")
    for sentence in self.directions:
      sentence = sentence.split()
      for token in sentence:
        temptoken = st.stem(token)
        if unicode(temptoken) in methodlist:
          self.recipe_info['method'] = token
          return
    return

  def ExtractTools(self):
    print("Determining cooking tools...")
    tools = []
    for item in self.cooking_tools:
      for ingred in self.ingredients:
        if item in ingred:
          tools.append(item)
      for direct in self.directions:
        if item in direct:
          tools.append(item)
    tools = list(set(tools))
    self.recipe_info['tools'] = tools
    return


  def veganize(self):
    print("Preparing to veganize...")
    #if already vegan, do nothing
    if "vegan" in self.title or "Vegan" in self.title:
      if self.verifyVegan:
        print("*RECIPE IS ALREADY VEGAN FRIENDLY!*")
        return
    #else, make it vegan
    self.title = "Vegan " + self.title
    counter = 0
    print("Updating ingredients...")
    for ingredient in self.ingredients:
      #remove information in parentheses
      ingredient[1] = removeParen(ingredient[1])
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
            new_weight = int(ingredient[0])*WEIGHT[item]
          else:
            new_weight = 0
          checker+=1
      if checker==len(ingred_list):
        self.updateDirections(ingredient[1], ingred_list)
        if new_weight>0:
          ingredient[0] = str(new_weight) + " ounces"
        ingredient[1] = "tofu"
      checker+= 1
    if not self.verifyVegan():
      print("COULD NOT BE TRANSFORMED INTO VEGAN FRIENDLY RECIPE")
    return

  def updateDirections(self, fullingred, ingred):
    print("Updating recipe instructions...")
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

  def verifyVegan(self):
    print("Verifying recipe...")
    for ingred in self.ingredients:
      counter = 0
      temp = ingred[1].split()
      for item in temp:
        if item in MEAT:
          counter+= 1
      if counter==len(temp):
        return False
    return True

  def Normalize(self):
    for entry in self.ingredients:
      entry[0] = re.sub(r'[^\w\s]','',entry[0])
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
    dir = ("\n\n\n####" + self.title + "####" + '\n'
    + "\n#==========================================#\n"
    + "#  Recipe Time\n"
    + "#==========================================#\n"
    + "-->Prep Time:  " + self.recipe_info['time']['preptime'] + '\n'
    + "-->Cook Time:  " + self.recipe_info['time']['cooktime'] + '\n'
    + "-->Total Time: " + self.recipe_info['time']['totaltime'] + '\n'
    + '\n#==========================================#\n'
    + "#  Ingredients\n"
    + "#==========================================#\n")

    for item in self.ingredients:
        dir = dir + "-->" + item[1] + " (" + item[0] + ")\n"

    dir = (dir + "\n##==========================================#\n"
      + "#  Tools\n"
      + "#==========================================#\n")
    for item in self.recipe_info['tools']:
      dir = dir + "-->" + item + '\n'

    dir = (dir + "\n#==========================================#\n"
    + "#  Directions\n"
    + "#==========================================#\n")

    for i in range(1, len(self.directions)+1):
        dir = dir + " " + str(i) + ".) " + self.directions[i-1] + '\n'

    dir = (dir + "\n#==========================================#\n"
    + "#  Preparation Technique\n"
    + "#==========================================#\n"
    + "-->" + self.recipe_info['method'] + '\n\n')

    return dir



def Initialize():
  print("\nWhat transformation would you like to perform?")
  print(" [V] Create a vegan option from an existing recipe")
  print(" [E] Exit")
  request = raw_input("--->")
  request = request.lower()
  if not request in ['v', 'e']:
    return Initialize()
  if request=='v':
    print('\n')
    recipe = Recipe()
    recipe.veganize()
    print(recipe.recipe_info)
    print recipe
  if request=='e':
    print('\n')
    return
  return Initialize()


#-------------------------------------------------------------------------------
# Calling the functions defined about
#-------------------------------------------------------------------------------

Initialize()



