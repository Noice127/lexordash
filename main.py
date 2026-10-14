from flask import Flask, render_template, request, jsonify
from menuscrape import get_menus
import recommendations
from recommendations import get_recommendation


app = Flask(__name__, template_folder='website/templates',)



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/menu", methods=["GET", "POST"])
def menu():

    if request.method == "POST":
        selected_meal = request.form.get("meal", "").lower()
        likes = request.form.get("likes", "")
        dislikes = request.form.get("dislikes", "")
    else:
        selected_meal = request.args.get("meal", "").lower()
        likes = request.args.get("likes", "")
        dislikes = request.args.get("dislikes", "")
    if selected_meal not in ("breakfast", "lunch", "dinner"):
        return "Invalid meal selection. Please go back and choose a meal.", 400


    menus = get_menus()
    menu_items = menus.get(selected_meal, [])
    try:
        recommendation = get_recommendation(selected_meal, likes, dislikes)
    except Exception:
        app.logger.exception("Failed to generate recommendation")
        recommendation = (
            "Sorry, I couldn't generate a recommendation right now. "
            "Please try again later."
    )
 
    return render_template(
        "menu.html",
        selected_meal=selected_meal,
        menu_items=menu_items,
        recommend = recommendation
    )

@app.route("/api/menu")
def menu_api():
    selected_meal = request.args.get("meal", "").lower()


    # Only accept supported meal names
    if selected_meal not in ("breakfast", "lunch", "dinner"):
        return jsonify({"error": "Invalid meal selection"}), 400

    try:
        menus = get_menus()
        menu_items = menus.get(selected_meal, [])

        return jsonify({
            "selected_meal": selected_meal,
            "menu_items": menu_items
        })

    except Exception:
        app.logger.exception("Failed to retrieve menu")
        return jsonify({"error": "Could not retrieve the menu"}), 500

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)