from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView
from models import LinksModel, PlaceModel, UserModel

def register_admin(app):
    admin = Admin(app, name='Адмінка', template_mode='bootstrap4')
    admin.add_view(ModelView(LinksModel))
    admin.add_view(ModelView(PlaceModel))
    admin.add_view(ModelView(UserModel))
