from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("base.html")


@app.route("/my_finances")
def my_finances():
    return render_template("my_finances.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/goal_progress")
def goal_progress():
    return render_template("goal_progress.html")


@app.route("/custom_goal")
def custom_goal():
    return render_template("custom_goal.html")


@app.route("/register")
def register():
    return render_template("register.html")