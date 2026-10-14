import menuscrape
from menuscrape import get_menus
import os
from groq import Groq#GROQ AI setup
from dotenv import load_dotenv

load_dotenv()

def get_recommendation(meal, likes, dislikes):
    """
    Generate a personalized recommendation for an IMSA meal.

    meal: breakfast, lunch, or dinner
    likes: free-response text describing preferred foods
    dislikes: free-response text describing disliked foods
    """

    #meal = meal.strip().lower()
    meal = (meal or "").strip().lower()
    likes = (likes or "").strip()
    dislikes = (dislikes or "").strip()

    if meal not in ("breakfast", "lunch", "dinner"):
        raise ValueError("Invalid meal selection.")

    # Retrieve the current IMSA menu.
    menus = get_menus()
    menu_items = menus.get(meal, [])

    if not menu_items:
        return f"No {meal} menu items were found. Please try again later."

    # Keep the API key on the Python backend.
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("The GROQ_API_KEY environment variable is missing.")

    client = Groq(api_key=api_key)

    # Send the student's preferences and the menu to the AI.
    chat_completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": """
You are Lex or Dash, a friendly food decision assistant for IMSA students.

Your job is to help the student decide whether to eat at the school
cafeteria or consider ordering food.

Choose between:
- LEX: Eat at the school cafeteria.
- DASH: Consider ordering food.

Rules:
- Compare the actual cafeteria menu with the student's likes and dislikes.
- Recommend a cafeteria item when it reasonably matches their preferences.
- Point out unfamiliar foods that might be worth trying.
- If the menu looks or sounds unappealing, you may suggest considering takeout.
-If the menu doesn't match their preferences (likes and dislikes) well also consider ordering food
- Do not claim a dish contains a particular ingredient unless the menu
  or reliable information supports that conclusion.
- Do not invent restaurant names, current deals, prices, or delivery fees.
-Look for any restaruant or fast food chain near and close by 1500 Sullivan Rd, Aurora, IL 60506
  Be transparent if current prices or deals cannot be verified.
- Keep the response under 80 words. (Don't use any special characters only regular text)
-In your response tell me whether or not I should Eat at my school's cafteria (Lex) or Order food (Dash). 
    -If you decide to Dash, pick a restaurant or food chain, that I should order from, tell me what I should get from there, and tell me the estimated cost (aim for under $20)
        -Give me at least 5 recommendations and let me know of any current deals taking place at the restaruant or happening on Doordash or ubereats 
- Be conversational and give a clear recommendation. 
"""
            },
            {
                "role": "user",
                "content": f"""
                        Meal: {meal}

                        Foods I like:
                        {likes or "No preferences provided."}

                        Foods I dislike:
                        {dislikes or "No dislikes provided."}

                        Today's IMSA cafeteria menu:
                        {chr(10).join(str(item) for item in menu_items)}

                        Should I eat at the cafeteria or consider ordering food?
                        Explain your recommendation briefly.
                    """
            }
        ],
    )

    return chat_completion.choices[0].message.content
