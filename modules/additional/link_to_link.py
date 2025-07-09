from modules.load_django import *
from parser_app.models import Link, Link_australia_18_12

for item in Link_australia_18_12.objects.all().order_by('id'):
    
    obj, created = Link.objects.get_or_create(
        link=item.link,
        defaults={
            'country': item.country,
            'city': item.city,
            'state': item.state,
            'zip_code': item.zip_code,
            'category': item.category,
            'keyword': item.name,
            'name': item.name,
        }
    )
    print(created, obj)