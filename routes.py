from flask import render_template, redirect, url_for, flash, request
from app import app, db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from models import User, ImageHistory
import os
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Ensure 'static/images' directory exists
os.makedirs("static/images", exist_ok=True)

def add_watermark(image, watermark_text):
    """
    Adds a watermark to the provided image with dynamic text color based on background.

    :param image: PIL Image object to watermark
    :param watermark_text: Text to display as the watermark
    """
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    margin = 20
    position = (image.width - text_width - margin, image.height - text_height - margin)
    # Sample background color to determine text visibility
    sample_area = image.crop((position[0], position[1], position[0] + text_width, position[1] + text_height))
    avg_color = sample_area.resize((1, 1)).getpixel((0, 0))
    text_color = (255, 255, 255) if sum(avg_color[:3]) < 400 else (0, 0, 0)
    draw.text(position, watermark_text, fill=text_color, font=font)

@app.route("/")
def home():
    """Renders the home page."""
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration with form validation and feedback."""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can log in now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login with authentication and feedback."""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("profile"))

        flash("Invalid credentials!", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Logs out the current user with confirmation feedback."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/profile")
@login_required
def profile():
    """Displays the user's profile with their image history."""
    images = ImageHistory.query.filter_by(user_id=current_user.id).order_by(ImageHistory.timestamp.desc()).all()
    return render_template("profile.html", images=images)

@app.route("/generate", methods=["POST"])
@login_required
def generate():
    """Generates an AI image from a user prompt with validation and processing."""
    prompt = request.form["prompt"].strip()
    if len(prompt) < 5:
        flash("Prompt must be at least 5 characters long.", "danger")
        return redirect(url_for("profile"))

    logging.info(f"Starting image generation for user {current_user.id} with prompt: {prompt}")

    width, height = 800, 600
    seed = random.randint(1, 10000)
    model = "flux"
    image_url = f"https://pollinations.ai/p/{prompt}?width={width}&height={height}&seed={seed}&model={model}"

    try:
        # Fetch image from API
        response = requests.get(image_url, timeout=30)
        response.raise_for_status()

        # Process image
        image = Image.open(BytesIO(response.content))
        width, height = image.size
        cropped_image = image.crop((0, 0, width, int(height * 0.90)))
        add_watermark(cropped_image, "@abhinandan_ap_")

        # Save image to filesystem
        image_filename = f"{current_user.id}_{random.randint(1, 10000)}.jpg"
        image_path = os.path.join("static", "images", image_filename)
        cropped_image.save(image_path)

        # Save image metadata to database
        new_image = ImageHistory(user_id=current_user.id, prompt=prompt, image_path=image_filename)
        db.session.add(new_image)
        db.session.commit()

        logging.info(f"Image generated and saved: {image_filename}")
        flash("Image generated successfully!", "success")
        return redirect(url_for("profile"))

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to generate image: {e}")
        flash("Failed to generate image. Please try again.", "danger")
        return redirect(url_for("profile"))

@app.route("/delete/<int:image_id>")
@login_required
def delete_image(image_id):
    """Deletes a user's image with ownership verification and feedback."""
    image = ImageHistory.query.get(image_id)
    if image and image.user_id == current_user.id:
        try:
            os.remove(os.path.join("static", "images", image.image_path))
        except FileNotFoundError:
            flash("File not found. It may have already been deleted.", "warning")
        db.session.delete(image)
        db.session.commit()
        flash("Image deleted successfully!", "success")
    else:
        flash("Unauthorized action.", "danger")
    return redirect(url_for("profile"))

# Run the app if executed directly
if __name__ == "__main__":
    app.run(debug=True)