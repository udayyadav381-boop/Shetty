from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
import time
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# 🔥 REDIRECT NON-WWW TO WWW
@app.before_request
def redirect_to_www():
    if request.host == "vijayviju.in":
        return redirect("https://www.vijayviju.in" + request.full_path)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
PROFILE_PATH = DATA_DIR / "profile.json"

def default_profile():
    return {
        "name": "Vijay Viju",
        "subtitle": "Actor | Theatre Artist",
        "background_image": "images/vijay.jpg",
        "basic_info": [
            {"label": "Age", "value": "34 - 40"},
            {"label": "Height", "value": "5 ft 7 inches"},
            {"label": "Weight", "value": "60 kg"},
            {"label": "Waist", "value": "30"},
            {"label": "Shoe Size", "value": "7"},
            {"label": "City", "value": "Mumbai"},
            {"label": "Nationality", "value": "Indian"},
            {"label": "Passport", "value": "Yes"},
        ],
        "experience": [
            {
                "title": "Films",
                "description": "Traffic Signal, Rahasya, Stone Man, Allah Ke Bandhe, College Campus, Indu Sarkar, Life in Dark, Teen Shayne, India Lockdown, What An Idea Sirji, MBDK, IPC & many more."
            },
            {
                "title": "TVC Ads & TV",
                "description": "Various projects across brands and regional television productions."
            }
        ],
        "skills": ["Driving", "Acting", "Action"],
        "hobbies": ["Reading", "Traveling"],
        "languages": ["Hindi", "Marathi", "English", "Gujarati", "Kannada"],
        "portfolio": [
    {"src": "images/work1.jpg", "alt": "Portfolio image 1"},
    {"src": "images/work2.jpg", "alt": "Portfolio image 2"},
    {"src": "images/work3.jpg", "alt": "Portfolio image 3"},
    {"src": "images/work4.jpg", "alt": "Portfolio image 4"},
    {"src": "images/work5.jpeg", "alt": "Portfolio image 5"},
    {"src": "images/work6.jpeg", "alt": "Portfolio image 6"},
    {"src": "images/work7.jpeg", "alt": "Portfolio image 7"},
    {"src": "images/work8.jpeg", "alt": "Portfolio image 8"},
]
        ],
        "videos": [
            {"id": "pKaev88OVus", "label": "Showreel 1"},
            {"id": "agR7TmegcUc", "label": "Showreel 2"},
            {"id": "LCkfYP2UoCg", "label": "Showreel 3"},
        ],
        "contact": [
            {"label": "Mobile", "value": "9821288527 / 7304542336"},
            {"label": "Emergency", "value": "9004749001"},
            {"label": "Email", "value": "viijayshetty@gmail.com"},
        ],
    }

def load_profile():
    if PROFILE_PATH.exists():
        try:
            return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return default_profile()
    else:
        p = default_profile()
        save_profile(p)
        return p

def save_profile(profile):
    PROFILE_PATH.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")

@app.route("/")
def home():
    profile = load_profile()
    return render_template("index.html", profile=profile)

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT

@app.route("/admin", methods=["GET", "POST"])
def admin():
    profile = load_profile()
    if request.method == "POST":
        file = request.files.get("image")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Only image files are allowed (png,jpg,jpeg,gif)")
                return redirect(url_for("admin"))
            filename = secure_filename(file.filename)
            timestamp = int(time.time())
            dest_name = f"{timestamp}_{filename}"
            save_path = Path("static") / "images" / dest_name
            save_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(save_path)
            where = request.form.get("add_to") or "portfolio"
            label = request.form.get("image_label") or dest_name
            if where == "background":
                profile["background_image"] = f"images/{dest_name}"
            else:
                profile.setdefault("portfolio", []).append({"src": f"images/{dest_name}", "alt": label})
            save_profile(profile)

        video_id = request.form.get("video_id")
        video_label = request.form.get("video_label") or "Showreel"
        if video_id:
            profile.setdefault("videos", []).append({"id": video_id.strip(), "label": video_label.strip()})
            save_profile(profile)

        contact_label = request.form.get("contact_label")
        contact_value = request.form.get("contact_value")
        if contact_label and contact_value:
            profile.setdefault("contact", []).append({"label": contact_label.strip(), "value": contact_value.strip()})
            save_profile(profile)

        flash("Changes saved")
        return redirect(url_for("admin"))

    return render_template("admin.html", profile=profile)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)