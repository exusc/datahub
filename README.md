Version 2.0.6 of Prototype for Concept Discussions
- first version of rls template for areas 

Supports base functionality for 
- Standard administration of DATA-Hub objects
- Self service with restriction to owned objects
- db actions logged but not executed
- Initial health checks implemented
- Unload and load of complete hub control
Changes to version 1 of the concept:
- Scopes are linked to areas instead of applications
- Groups are not owner specific

Open Stories
- Connection to secure connect
- UI should use Abraxas Base Components
- Support of MinIo

In Progress
- Test the rls scripts 
- Using PK if value depends on table ... ?

Backlog
- PropagationProcess
- BUT with type (TEXT, Integer, Boolean)
- Scopes with min max for Schutzstufen 
- Create application Test based on definition in Confluence
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


