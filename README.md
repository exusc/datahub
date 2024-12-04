Version 2.0.1 of Prototype for Concept Discussions

Supports base functionality for 
- Standard administration of DATA-Hub objects
- Self service with restriction to owned objects
- db actions logged but not executed
- Initial health checks implemented
- Unload and load of complete hub control
Changes to version 1 of teh concept:
- Scopes are linked to areas instead of applications
- Groups are not owner specific

Open Stories
- Connection to secure connect
- UI should use Abraxas Base Components
- Support of MinIo


Next Tasks
- See TODO in User admin: selection of areasscopes must include own scopes
  Beispiel besser machen
- Passwort auslagern?
- Scopes with from to for Schutzstufen 
- Create application Test based on definition in Confluence

Next Stories
- Define RLS for the hub itself
- Extend Health-Check 
- Reduce load function to AW - others are loaded by Json
- Execution of container actions in db and filestorage
- Usage of *-functionality with Areascopes
- UI for scope adding
- Multi-language-support

------------------------------------------------------------------------------------------
Tipp:
  https://docs.djangoproject.com/en/5.1/ref/templates/builtins/#include
  {% include "pagination.html" with obj="page_obj"  %}

Test cases
  https://confluence.abraxas-tools.ch/confluence/display/DSc/RLS+-+Test+Cases
