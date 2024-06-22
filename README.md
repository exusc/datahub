Supports base functionality for 
- standard administration of DATA-Hub Security
- self service with restriction to wned objects

Open: 
- connection to secure connect
- Owner-Concept:
  Each object has an Owner Element
  User have one owner and multiple maintains
  filter for self service should be on super class level 
  Using ownership on all objects in the same manner, 
  copy owner information during save process to dependent objects (scope and are will get it from application )
- implementation of actions within data container (add are with existing scopes, add scope, ...)
- translation of literals

Reporting has to be implemented in a separate app
