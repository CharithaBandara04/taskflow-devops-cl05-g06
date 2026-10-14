from flask import Blueprint, jsonify, render_template

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "TaskFlow"
    }), 200
