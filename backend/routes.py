from flask import Blueprint, jsonify

# Create a Blueprint for general routes
main = Blueprint('main', __name__)

@main.route("/")
def home():
    return jsonify({"message": "Welcome to Spot A Friend Backend!"})
