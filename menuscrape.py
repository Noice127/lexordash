import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import date


url = "https://menus.tenkites.com/eliorna/d1654" #menu site url 
LOCATION_ID = "cc588e31-0df1-4067-a851-b051b211216d"#cafteria location (IMSA) id


MEALS = ("breakfast", "lunch", "dinner") #the 3 different type of menus we want to access


#our main function
def get_menus(menu_date=None):
  #if the function is not given a specific date it defaults to the current day
    if menu_date is None:
      menu_date = date.today().isoformat()#current date: 2026-10-12 format
    """
    Return breakfast, lunch, and dinner menu items for a date.

    Returns:
        {
            "breakfast": ["Food 1", "Food 2"],
            "lunch": ["Food 3", "Food 4"],
            "dinner": ["Food 5", "Food 6"]
        }

    A meal with no available menu is returned as an empty list.
    """

    menus = {meal: [] for meal in MEALS} #creates a dictionary for menus

    """
      ex:  
      breakfast = []
      lunch = []
      dineer = []

      and all of this is stored in menus
    """

    session = requests.Session() #A session manages repeated requests to the same website and can reuse connection settings and cookies. Since you request multiple menus, a session is useful.

    # 1. Fetch the page to discover the menu IDs for this date.
    response = session.get(
        url,
        params={#params is a dictionary of query parameters that Python adds to the URL.
            "cl": "true",
            "mguid": LOCATION_ID, #imsa location
            "mldate": menu_date, #date
        },
        timeout=25,#It limits how long the request waits for a response before timing out.
    )
    response.raise_for_status()#It raises an error if the server responds with an unsuccessful HTTP status, such as 404 or 500. This prevents your code from silently continuing as if the request succeeded.

    soup = BeautifulSoup(response.text, "html.parser") #reads and returns html from the webpage

    # 2. Find the embedded menu schedule. from the script elements
    scripts = "\n".join(
        script.get_text()
        for script in soup.find_all("script")
    )

  #searchs the same script that contains menu schedule and the result is stored in math
    match = re.search(
        r'k10\.settings\.menuCycle\.items\s*=\s*JSON\.parse\(`(.*?)`\);',
        scripts,
        re.DOTALL,
    )

    if not match: #if it struggles to find the menu schedule it returns an error
        raise ValueError("Could not find the menu schedule in the page.")

    menu_cycles = json.loads(match.group(1)) #converts text into json python data

    # 3. Find each meal's ID for the requested date.
    menu_ids = {}

    for cycle in menu_cycles:
        for day in cycle.get("mcca", []):
            if day.get("ddn", "")[:10] != menu_date:
                continue

            for menu in day.get("MenuCycleContentItems", []):
                meal_name = menu.get("milna", "").strip().lower()#retrieves menu name ex: breakast, lunch, dinner

                if meal_name in MEALS:
                    menu_ids[meal_name] = menu.get("midnt") #stores menu name 

    # 4. Request each available meal and extract its food items.
    for meal in MEALS:
        menu_id = menu_ids.get(meal)#uses the meal id (breakfast, lunch, dinner) to then actucally get menu items

        if not menu_id:
            continue

        response = session.get(
            url,
            params={
                "cl": "true",
                "mguid": LOCATION_ID,
                "mldate": menu_date,
                "mlguid": menu_id,
                "internalrequest": "true",
            },
            timeout=20,
        )
        response.raise_for_status()

        meal_soup = BeautifulSoup(response.text, "html.parser")

        menus[meal] = [
            recipe.get_text(" ", strip=True)
            for recipe in meal_soup.select("span.k10-recipe__name")
        ]

    return menus

'''
How to implement into other files and applications


menu = get_menus()
menu['breakfast']
print(menu['dinner'])




if you only want to retreive the specific items without brackets

menu = get_menus()

print("Dinner Menu:")

for item in menu["dinner"]:
    print("-", item)


    or
from menu_scraper import get_menus

menus = get_menus()

for meal, items in menus.items():
    print(f"\n{meal.title()} Menu:")

    if items:
        for item in items:
            print(f"- {item}")
    else:
        print("No menu items found.")
'''
