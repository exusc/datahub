Version 1.1.0 of Prototype for Concept Discussions
   ContainerSystem in use, test cases including Taxa PoC complete

Supports base functionality for 
- Standard administration of DATA-Hub objects
- Self service with restriction to owned objects
- db actions logged but not executed
- Initial health checks implemented

Open Tasks
- Connection to secure connect
- UI should use Abraxas Base Components
- Support of Min-IO
- Scope must be connected to areas instead of applications

Next Tasks
- Health-Check auf Applikationsebene 
  - Informationen zu Applikation (Business-Units, Anzahl Scopes) siehe DashBoard
  - keine Gesamtübersicht: Applikations-DBs alle Datenbanken / Login-Hook
  - Areas mit ihren Checks
- MyDataHUB (Index) verkürzen - Liste der Applikationen -> Health-Check
- FileStorage im Filesystem fertigmachen:
  Scripttype einbauen 
  scope_delete if not empty
  scope_exists, scope is_empty()
- Alle Scopes anlegen als Funktion auf den Containern

Next Stories
- Implement health checks
- Execution of container actions in db and filestorage
- Active References - Container->Area->Application
- Usage of *-functionality with scopes
- Scopes with from to for Schutzstufen 
- UI for scope adding
- Multi-language-support

------------------------------------------------------------------------------------------
Tipp:
  https://docs.djangoproject.com/en/5.1/ref/templates/builtins/#include
  {% include "pagination.html" with obj="page_obj"  %}

