import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import PlaceModel, UserModel
from admin import register_admin
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from modules.get_links import run_parsing
from modules.get_place import process_places_for_user
from flask_mongoengine import MongoEngine
from mongoengine import disconnect


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'places_db',
    'host': 'mongodb://db:27017/places_db'
}
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = 'super_secret_key_12345'

db = MongoEngine()

disconnect(alias='default')
db.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
register_admin(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return UserModel.objects(id=user_id).first()

@app.route('/')
@login_required
def index():
    return render_template('home.html', user=current_user)

@app.route('/contacts/')
def contacts():
    return render_template('contacts.html')

@app.route('/market/')
def market():
    page = request.args.get('page', 1, type=int)
    per_page = 9

    name_query = request.args.get('name', '').strip()
    category_query = request.args.get('category', '').strip()

    base_query = PlaceModel.objects

    if name_query:
        base_query = base_query.filter(name__icontains=name_query)
    if category_query:
        base_query = base_query.filter(category__icontains=category_query)

    total_places = base_query.count()
    places = base_query.skip((page - 1) * per_page).limit(per_page)
    total_pages = (total_places + per_page - 1) // per_page

    return render_template(
        'market.html',
        places=places,
        page=page,
        total_pages=total_pages
    )

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        city = request.form.get('city')
        phone = request.form.get('phone')
        email = request.form.get('email')
        interests = request.form.get('interests')
        telegram = request.form.get('telegram')
        social_media = request.form.get('social_media', '').split()
        telegram_chat_id = request.form.get('telegram_chat_id')
        photo_file = request.files.get('photo')

        photo_path = None
        if photo_file and photo_file.filename:
            filename = photo_file.filename
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo_file.save(photo_path)
            photo_path = photo_path.replace('static/', '')  # для шаблону

        user = UserModel(
            full_name=full_name,
            city=city,
            phone=phone,
            email=email,
            interests=interests,
            telegram=telegram,
            social_media=social_media,
            telegram_chat_id=telegram_chat_id,
            photo=photo_path
        )
        user.save()

        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        user = UserModel.objects(email=email).first()
        if user:
            login_user(user)
            flash('Вхід успішний!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Користувача не знайдено', 'error')

    return render_template('login.html')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('Ви вийшли з акаунту', 'info')
    return redirect(url_for('login'))

@app.route("/search_links", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        country = request.form.get("country")
        city = request.form.get("city")
        category = request.form.get("category")

        try:
            run_parsing(country, city, category, current_user)
            flash("✅ Парсинг виконано!", "success")
        except Exception as e:
            print("❌ Error:", e)
            flash("❌ Помилка під час парсингу", "danger")

        try:
            process_places_for_user(current_user)
            flash("✅ Обробка місць завершена!", "success")
        except Exception as e:
            print("❌ Error in process_places_for_user:", e)
            flash("❌ Помилка при обробці місць", "danger")

        return redirect(url_for("search"))

    return render_template("request.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
