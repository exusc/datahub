""" Alle information about how rls is generated must be defined here

"""

from django.template.loader import render_to_string
from . models import Area
import datetime


def area_script(area:Area):
    """ Creates the complete script for rls of an area """
    
    def get_tables_for_but(column_name):
        """ get all tables having specific column_name"""
        sql = f"""select table_name from information_schema.columns
          where table_schema = '{area.schematables}' and column_name = '{column_name.lower()}'
        """
        rows = area.database.exec_sql(sql)
        return {row[0] for row in rows}
    
    context = {'area' : area, 'time' : datetime.datetime.now() }

    bu1_tables = get_tables_for_but(area.application.bu1_field.lower())
    context.update({'bu1_tables': bu1_tables})
    bu2_tables = get_tables_for_but(area.application.bu2_field.lower())
    context.update({'bu2_tables': bu2_tables})

    rls_tables = bu1_tables | bu2_tables
    context.update({'rls_tables': rls_tables})

    # Connection = Defaults from ContainerSystem updated by specific Container
    connection = area.database.containersystem.connection
    if area.database.connection:
        connection.update(area.database.connection)
    
    context.update({'db_name': connection.get('NAME')})
    context.update({'db_host': connection.get('HOST')})
    context.update({'role': f'_{area.schematables}_read_only'})

    return render_to_string("rls/PostGres/area.txt", context)
