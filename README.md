Version 1.0.7.7 of Prototype for Concept Discussions

Supports base functionality for 
- Standard administration of DATA-Hub objects
- Self service with restriction to owned objects
- db actions logged but not executed
- Initial health checks implemented

Open Tasks
- connection to secure connect

Next Tasks
- FileStorage im Filesystem: scope_add implemented - next steps open
- Alle Scopes anlegen als Funktion auf den Containern

Next Stories
- Execution of container actions in db and filestorage
- Active References - Container->Area->Application
- Implement health check for tables
- Usage of *-functionality with scopes
- Scops with from to for Schutzstufen 
- UI for scope adding
- Multi-language-support

------------------------------------------------------------------------------------------
Tipp:
  https://docs.djangoproject.com/en/5.1/ref/templates/builtins/#include
  {% include "pagination.html" with obj="page_obj"  %}

