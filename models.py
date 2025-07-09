from flask_mongoengine import MongoEngine

db = MongoEngine()

class LinksModel(db.Document):
    user = db.ReferenceField('UserModel', required=True)
    link = db.StringField(required=True, unique=True)
    name = db.StringField()
    country = db.StringField()
    city = db.StringField()
    category = db.StringField()
    status = db.StringField(default='Pending')

class PlaceModel(db.Document):
    user = db.ReferenceField('UserModel', required=True)
    link = db.StringField(required=True, unique=True)
    category = db.StringField()
    name = db.StringField()
    rating = db.FloatField()
    num_reviews = db.IntField()
    about = db.DictField()
    full_address = db.StringField()
    country = db.StringField()
    city = db.StringField()
    state = db.StringField()
    zip_code = db.StringField()
    address = db.StringField()
    located_in = db.StringField()
    lat = db.FloatField()
    lng = db.FloatField()
    place_type = db.StringField()
    open_hours = db.DictField()
    open_24_7 = db.DictField()
    phone = db.StringField()
    website = db.StringField()
    image = db.StringField()

class UserModel(db.Document):
    full_name = db.StringField(required=True)
    city = db.StringField()
    phone = db.StringField()
    email = db.StringField()
    interests = db.StringField()
    telegram = db.StringField()
    social_media = db.ListField(db.StringField())
    telegram_chat_id = db.StringField(required=False)
    photo = db.StringField()

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        # якщо хочеш, щоб користувач міг логінитись, повертай True
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
