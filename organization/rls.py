""" Alle information about how rls is generated must be defined here

"""

from django.template.loader import render_to_string
from . models import Area
import datetime


def area_script(area:Area):
    context = {'area' : area, 'time' : datetime.datetime.now() }

    # Connection = Defaults from ContainerSystem updated by specific Container
    connection = area.database.containersystem.connection
    if area.database.connection:
        connection.update(area.database.connection)
    
    context.update({'db_name': connection.get('NAME')})
    context.update({'db_host': connection.get('HOST')})
    
    return render_to_string("rls/PostGres/area.txt", context)
