Version 1.5 of Prototype for Concept Discussions

Supports base functionality for 
- Standard administration of DATA-Hub objects
- Self service with restriction to owned objects
- db actions logged but not executed
- Initial health checks implemented
- Unload aund load of complete hub control
Changes to original concept
- Defines Areascopes instead of scopes
- Groups are not owner specific

Open Stories
- Connection to secure connect
- UI should use Abraxas Base Components
- Support of MinIo

Next Tasks
- Applikation TEST aufbauen mit den Testfällen aus Confluence -
  RLS für den Hub selbst definieren - per Applikation Test in eigener DB

Next Stories
- Load nur noch AW, Rest aus JSON
- Health-Check weitermachen
- MyDataHUB (Index.html) verkürzen - Liste der Applikationen -> Health-Check
- FileStorage im Filesystem fertigmachen:
  Scripttype einbauen 
  scope_delete if not empty
  scope_exists, scope is_empty()
- Alle Scopes anlegen als Funktion auf den Containern
- Implement health checks
- Execution of container actions in db and filestorage
- Usage of *-functionality with Areascopes
- Scopes with from to for Schutzstufen 
- UI for scope adding
- Multi-language-support

------------------------------------------------------------------------------------------
Tipp:
  https://docs.djangoproject.com/en/5.1/ref/templates/builtins/#include
  {% include "pagination.html" with obj="page_obj"  %}

Test cases
  https://confluence.abraxas-tools.ch/confluence/display/DSc/RLS+-+Test+Cases
