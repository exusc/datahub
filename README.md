Version 1.0.2 of Prototype for Concept Discussions

Supports base functionality for 
- Standard administration of DATA-Hub objects
- Self service with restriction to owned objects
- First version of health checks implemented

Open Tasks
- connection to secure connect
- implementation of actions within data container (add area with existing scopes, add scope, ...)

Next Stories
- usage of *-functionality with scopes
- UI for add scope 
- multi-language-support

------------------------------------------------------------------------------------------
Infos
- Reduce Consolen-Output 
  - https://stackoverflow.com/questions/6175030/django-shut-off-console-output-of-http-response-messages
  - https://forum.djangoproject.com/t/no-console-output-for-http-request-messages-from-django-3-1-in-ubuntu-20/5046/2


Raw Queries
https://docs.djangoproject.com/en/5.0/topics/db/sql/
direkt: https://docs.djangoproject.com/en/5.0/topics/db/sql/#executing-custom-sql-directly
https://docs.djangoproject.com/en/5.0/ref/models/querysets/

SELECT * FROM pg_catalog.pg_database 
SELECT * from pg_catalog.pg_namespace
SELECT * FROM pg_catalog.pg_tables     WHERE schemaname = 'dat_cd_base'
SELECT * FROM pg_catalog.pg_views      WHERE schemaname = 'dmo_rd'

SELECT * FROM pg_tables
  WHERE schemaname!='pg_catalog'
    AND schemaname!='information_schema';

------------------------------------------------------------------------------------------

