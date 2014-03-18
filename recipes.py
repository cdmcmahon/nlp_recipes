from alchemyapi import AlchemyAPI
alchemyapi = AlchemyAPI()
import pprint
import json
import nltk
from nltk.stem.lancaster import LancasterStemmer
st = LancasterStemmer()
import re, string, sys, os, codecs
import urllib2
from BeautifulSoup import BeautifulSoup as Soup
import BeautifulSoup
from fractions import Fraction

# response = urllib2.urlopen('http://allrecipes.com/Recipe/Lentils-and-Rice-with-Fried-Onions-Mujadarrah/Detail.aspx?soid=carousel_0_rotd&prop24=rotd')

#-------------------------------------------------------------------------------
# Constants and Variables
#-------------------------------------------------------------------------------

def loadMeat():
  filename = "meat.txt"
  if not os.path.exists(filename):
    print("ERROR: Meat list could not be loaded.")
    close = raw_input('--> ')
    return sys.exit()
  meat = []
  for line in codecs.open(filename, 'r', encoding='utf-8'):
    line = line.rstrip('\n')
    meat.append(line)
  return meat

def updateMeat(newitem):
  try:
    temp = alchemyapi.keywords('text', newitem, {'maxRetrieve': 1})
  except:
    print("\n####ERROR: Alchemy limit exceeded. Change API Keys to continue.")
    sys.exit(0)
  for keyword in temp['keywords']:
    ntemp = keyword['text']
  newlist = ntemp.split()
  with codecs.open("meat.txt", 'a+', encoding = 'utf-8') as File:
    for item in newlist:
      item = st.stem(item)
      File.write('\n' + item)
  return

FISH = ["catfish", "pollock", "mackerel", "flounder", "halibut", "mahi", "tuna", "salmon", "blue gill", "shark",
        "grouper", "haddock", "bass", "trout", "crappie", "bluefish", "bluefin", "cod", "carp", "sheephead",
        "snapper", "mahi-mahi", "perch", "panfish", "yellowfin", "walleye", "tilapia", "smallmouth", "largemouth",
        "roughy", "pollock", "rainbow", "sole"]

EXCEPTIONS = ["season", "seasoning", "powder", "powders", "glaz", "glaze", "sauce", "sauc", "sauces",
              "spice", "spic", "spices", "mix"]

WEIGHT = dict(bacon = .66, breast = 6, chicken = 64, chop = 4, duck = 64, turkey = 160) #in ounces

VEGANCHANGE = dict(beefbouillon = "vegetable bouillon", beefbroth = "french onion soup", beefstock = "vegetable stock",
                    chickenbouillon = "vegetable bouillon", chickenbroth = "french onion soup", chickenstock = "vegetable stock",
                    hamstock = "vegetable stock", fishstock = "vegetable stock",
                    vealstock = "vegetable stock", vealbouillon = "vegetable bouillon", shrimpbouillon = "shrimp bouillon")

DESCRIPTORS = ["fat-free", "thick", "half", "halves", "boneless", "skinless", ",", "strip", "flank", "cut", "thin", "long",
              "into"]

QUANTITIES = ["teaspoon", "dessertspoon", "tablespoon", "ounce", "ount", "pound", "fillet", "fluid ounce", "can", "cup", "pack", "package",
              "pint", "pinch", "quart", "gallon", "liter", "slic", "slice", "bottle", "bottl", "clove", "clov",
              "teaspoons", "dessertspoons", "tablespoons", "ounces", "ounts", "pounds", "fillets", "fluid ounces", "cans", "cups", "packs",
              "packages" "pints", "pinches", "quarts", "gallons", "liters", "slices", "bottles", "cloves"]

ABR_QUANTITIES = dict(tsp = "teaspoon", tsps = "teaspoons", tbsp = "tablespoon", tbsps = "tablespoons", lbs = "pounds", lb = "pound",
                      floz = "fluid ounce", oz = "ounce", pt = "pint", qt = "quart", gal = "gallon")

FRUITS = ["apple", "orange", "pear", "grape", "tangerine", "clementine", "banana", "peach", "blueberry", "blackberry", "cranberry",
"guava", "eggplant", "backcurrant", "redcurrant", "gooseberry", "tomato", "lucuma", "kiwi", "kiwigruit", "grapefruit", "pumpkin", "gourd",
"cucumber", "melon", "lemon", "lime", "grapefruit", "boysenberry", "pineapple", "fig"];

VEGETABLES = ["carrot", "parsnip", "beet", "beetroot", "broccoli", "cauliflower", "artichoke", "corn", "sweet corn",
"capers", "kale", "collard greens", "spinach", "arugula", "lettuce", "spinach", "leeks", "brussel sprouts", "brussels sprouts",
"celery", "rhubarb", "asparagus", "sweet potatoes", "yams", "sprout", "onion", "shallot", "zucchini", "peppers", "okra", "avocado", "corn", "green beans", "peas", "snow peas"];

HIGH_FAT_INGREDIENTS_REDUCE = [["shortening", "oil"],
["sugar"],
["salt"]];

HIGH_FAT_INGREDIENTS_REPLACE = dict(butter = "low-fat margarine", )
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

original_recipe = dict()
#-------------------------------------------------------------------------------
# Class related to the specific recipe.
#   -Requests URL for recipe
#   -Retrieves page in HTML
#   -Parses HTML for specific information (i.e. Title, Cook Time, Ingredients, etc)
#-------------------------------------------------------------------------------
class Recipe:
  def __init__(self):
    print("Initializing...")
    self.pageurl = None
    self.recipe_html = ""
    self.recipe_soup = ""
    self.recipe_info = dict(method= "", ingredients= [], tools= [], time = dict())
    self.title = ""

    self.cooking_tools = getUtensils() + getCookware()
    self.ingredients = []
    self.directions = []

    self.meat = loadMeat()
    self.RetrieveInfo()

  def RetrieveInfo(self, url=None):
    self.ParsePage(url)
    #====retrieve specific items from the page====
    print("Preparing to retrieve information...")
    self.ExtractTitle()
    self.ExtractIngredients()
    self.ExtractTime()
    self.ExtractDirections()
    print("Normalizing information...")
    self.Normalize()
    self.ExtractMethod(getTechniques())
    self.ExtractTools()
    return

  def ParsePage(self, url):
    if url:
      page = urllib2.urlopen(self.pageurl)
      print("Converting page...")
      self.recipe_html = page.read()
      self.recipe_soup = Soup(self.recipe_html)
      return
    else:
    #====request page URL====
      print('\n')
      self.pageurl = raw_input("Please input the URL of a recipe from AllRecipes.com: ")
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
      tempDict = dict()
      #extract quantity and measurement
      amount = listing.find('span', id="lblIngAmount")
      if amount:
        quantitytext = "None"
        amounttext = removeParen(amount.getText().lower()).split()
        #separate quantities and measurements
        i = 0
        for item in amounttext:
          tempitem = st.stem(item)
          if tempitem in QUANTITIES:
            quantitytext = item
            amounttext.remove(item)
            i-= 1
          elif item in ABR_QUANTITIES.keys():
            quantitytext = ABR_QUANTITIES[item]
            amounttext.remove(item)
            i-= 1
          #convert fractions to decimals
          else:
            try:
              amounttext[i] = str(float(Fraction(item)))
            except:
              print "ERROR: Unrecognized quantity"
              amounttext[i] = ""
          i+= 1
        amounttext = " ".join(amounttext)
      else:
        amounttext = 'None'
      tempDict['measurement'] = quantitytext
      tempDict['quantity'] = amounttext
      tempDict['descriptor'] = "None"
      tempDict['preparation'] = "None"
      #extract ingredient name
      ingred = listing.find('span', id="lblIngName")
      if ingred:
        ingredtext = ingred.getText().lower()
      else:
        break
      tempDict['name'] = ingredtext
      self.recipe_info['ingredients'].append(tempDict)
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
      self.recipe_info['time']['preptime'] = "None"
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
      self.recipe_info['time']['cooktime'] = "None"
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
      self.recipe_info['time']['totaltime'] = "None"
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
    self.recipe_info['instructions'] = self.directions
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

  # USING TECHNIQUES FROM MAYO CLINIC WEBSITE
  # http://www.mayoclinic.org/healthy-living/nutrition-and-healthy-eating/in-depth/healthy-recipes/art-20047004
  def makeHealthy(self):
    print("Preparing to make healthier...")
    for ingredient in self.recipe_info['ingredients']:
      # Reduce/replace butter and replace with unsweetened applesauce
      if "butter" in ingredient['name'].lower():
        ingredient['name'] = "low-fat margarine"
        ingredient['quantity'] = str(float(ingredient['quantity']) * .5)
        newIngredient = dict()
        newIngredient['name'] = "applesauce"
        newIngredient['descriptor'] = "unsweetened"
        newIngredient['quantity'] = ingredient['quantity']
        newIngredient['measurement'] = ingredient['measurement']
        newIngredient['preparation'] = "None"
        self.recipe_info['ingredients'].append(newIngredient)
      # Reduce Shortening and replace with unsweetened applesauce
      if "shortening" in ingredient['name'].lower():
        ingredient['quantity'] = str(float(ingredient['quantity']) * .5)
        newIngredient = dict()
        newIngredient['name'] = "applesauce"
        newIngredient['descriptor'] = "unsweetened"
        newIngredient['quantity'] = ingredient['quantity']
        newIngredient['measurement'] = ingredient['measurement']
        newIngredient['preparation'] = "None"
        self.recipe_info['ingredients'].append(newIngredient)
      # Reduce amount of oil
      if "oil" in ingredient['name'].lower():
        ingredient['quanitity'] = str(float(ingredient['quantity']) * .7)
      # Reduce sugar and add spices to compensate
      if "sugar" == ingredient['name'].lower():
        ingredient['quantity'] = str(float(ingredient['quantity']) * .6)
        newIngredient = dict()
        newIngredient['name'] = "assorted spices (cinnamon, cloves, allspice, nutmeg, vanilla extract) to replace sugar"
        newIngredient['descriptor'] = "unsweetened"
        newIngredient['quantity'] = "2"
        newIngredient['measurement'] = "pinches"
        newIngredient['preparation'] = "None"
        self.recipe_info['ingredients'].append(newIngredient)
      # Reduce salt use dramatically
      if "salt" == ingredient['name'].lower():
        ingredient['quantity'] = str(float(ingredient['quantity']) * .25)
      # Use low-fat pasta
      if "pasta" in ingredient['name'].lower():
        ingredient['name'] = ingredient['name'] + " (low-fat)"
      # Fat free milk saves calories and lowers fat content
      if "milk" in ingredient['name'].lower():
        ingredient['name'] = "fat-free milk";
      # Remove some cheese
      if "cheese" in ingredient['name'].lower() and "shredded" in ingredient['preparation'].lower():
        ingredient['quantity'] = str(float(ingredient['quantity']) * .75)
      if "cheese" in ingredient['name'].lower():
        ingredient['quantity'] = str(float(ingredient['quantity']) * .6)
      # Increase fruits and vegetables
      for veg in VEGETABLES:
        if veg in ingredient['name'].lower():
          ingredient['quantity'] = str(float(ingredient['quantity']) * 2)
      for fruit in FRUITS:
        if fruit in ingredient['name'].lower():
          ingredient['quantity'] = str(float(ingredient['quantity']) * 2)
      # Replace ground beef
      if "ground beef" in ingredient['name'].lower():
        ingredient['name'] = "ground turkey"
      if "beef" in ingredient['name'].lower():
        ingredient['quantity'] = str(float(ingredient['quantity']) * .75)
    # End of foor loop
    self.title = "Low-fat " + self.title
    print("All possible substitutions, reductions and increases in ingredients have been made.")
    return


  def vegetarianize(self):
    print("Preparing to vegetarianize...")
    option = self.checkFish()
    #else, make it vegan
    counter = 0
    numchanges = 0
    print("Updating ingredients...")
    for ingredient in self.recipe_info['ingredients']:
      try:
        temp = alchemyapi.keywords('text', ingredient['name'], {'maxRetrieve': 1})
      except:
        print("\n####ERROR: Alchemy limit exceeded. Change API Keys to continue.")
        sys.exit(0)
      for keyword in temp['keywords']:
        ntemp = keyword['text']
        ntemp = ntemp.split()
      #change broths, stocks, etc. into vegan options
        if "".join(ntemp) in VEGANCHANGE.keys():
          for entry in range(0,len(self.directions)):
            self.directions[entry] = self.directions[entry].replace(ingredient['name'], VEGANCHANGE[ingredient['name'].replace(" ", "")])
          ingredient['name'] = VEGANCHANGE["".join(ntemp)]
      #replace meat with tofu
        checker = True
        counter = 0
        for item in ntemp:
          if item in EXCEPTIONS:
            checker = False
        if checker:
          for item in ntemp:
            nitem = st.stem(item)
            if nitem in self.meat or nitem in FISH:
              counter+= 1
          if counter==len(ntemp):
            self.updateDirections(item, ingredient['name'].split(), option[0])
            ingredient['name'] = option[0]
            ingredient['measurement'] = option[1]
            numchanges+= 1
    if numchanges==0:
      self.findNewMeat()
    if not self.verifyVegetarian():
      print("COULD NOT BE TRANSFORMED INTO VEGETARIAN RECIPE")
      self.findNewMeat()
    self.recipe_info['instructions'] = self.directions
    self.title = "Vegetarian " + self.title
    return
  #check if vegetarian option can include fish
  def checkFish(self):
    print('\n')
    response = raw_input("Do you eat fish? (Y or N) ")
    print('\n')
    response = response.lower()
    if not response in ['y', 'n']:
      return self.checkFish()
    if response=='y':
      return ['tilapia', 'filets']
    return ['tofu', 'pounds']

  def updateDirections(self, fullingred, ingredlist, option):
    ingredlist.insert(0, fullingred)
    for item in ingredlist:
      for entry in range(0,len(self.directions)):
        self.directions[entry] = self.directions[entry].replace(item, option)
        self.directions[entry] = self.directions[entry].replace("meat", option)
        self.directions[entry] = self.directions[entry].replace("tofus", option)
        self.directions[entry] = self.directions[entry].replace(str(option + ' ' + option), option)
    return

  def verifyVegetarian(self):
    print("Verifying recipe...")
    for ingred in self.recipe_info['ingredients']:
      counter = 0
      try:
        temp = alchemyapi.keywords('text', ingred['name'], {'maxRetrieve': 1})
      except:
        print("\n####ERROR: Alchemy limit exceeded. Change API Keys to continue.")
        sys.exit(0)
      for keyword in temp['keywords']:
        ntemp = keyword['text']
        ntemp = ntemp.split()
        for item in ntemp:
          item = st.stem(item)
          if item in self.meat:
            counter+= 1
        if counter==len(ntemp):
          return False
    return True

  def findNewMeat(self):
    print('\nERROR: Meat unknown.\nWhich of the following is meat?')
    i = 1
    intrange = [0]
    for ingred in self.recipe_info['ingredients']:
      intrange.append(i)
      print("  ["+str(i)+"] " + ingred['name'])
      i+= 1
    print("  [0] None")
    answer = None
    while not answer:
      answer = raw_input("---> ")
      if not int(answer) in intrange:
        answer = None
    if int(answer)==0:
      return
    updateMeat(self.recipe_info['ingredients'][int(answer)-1]['name'])
    self.meat = loadMeat()
    print("\nMeat database updated!")
    return self.vegetarianize()

  def Normalize(self):
    for entry in self.recipe_info['ingredients']:
      entry['name'] = re.sub(r'[^\w\s]','',entry['name'])
    return

  def revert(self):
    print('\n')
    response = raw_input("Would you like to revert to the original recipe? (Y or N)? ")
    response = response.lower()
    if not response in ['y', 'n']:
      return self.revert()
    if response=='y':
      self.recipe_info.clear()
      self.recipe_info = dict(method= "", ingredients= [], tools= [], time = dict())
      self.RetrieveInfo(self.pageurl)
      return True
    return False

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

    for item in self.recipe_info['ingredients']:
        dir = dir + "-->" + item['name'] + " (" + item['quantity'] + " " + item['measurement'] + ")\n"

    dir = (dir + "\n#==========================================#\n"
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
  print(" [V] Create a vegetarian option from an existing recipe")
  print(" [H] Create a healthier option from an existing recipe")
  print(" [N] No transformation")
  print(" [E] Exit")
  request = raw_input("--->")
  request = request.lower()
  if not request in ['v', 'e', 'h', 'n']:
    return Initialize()
  else:
    print("\n")

  if request=='v':
    recipe = Recipe()
    recipe.vegetarianize()
    print recipe
    answer = recipe.revert()
    if answer:
      print recipe
    #pprint.pprint(recipe.recipe_info)
  if request=='h':
    recipe = Recipe()
    recipe.makeHealthy()
    print recipe
    answer = recipe.revert()
    if answer:
      print recipe
  if request == 'n':
    recipe = Recipe()
    print recipe

  if request=='e':
    return

  raw_input("Press any key to continue.") #so they have time to actually read the recipe
  return Initialize()


#-------------------------------------------------------------------------------
# Calling the functions defined about
#-------------------------------------------------------------------------------

Initialize()



