Version 0.9.3.1

Supports base functionality for 
- Standard administration of DATA-Hub objects
- Self service with restriction to owned objects
- Reporting has to be implemented in a separate app

Open Tasks
- connection to secure connect
- implementation of actions within data container (add are with existing scopes, add scope, ...)

To be discussed
- Scopes are defined on application level - if we want to reduce user access to specific areas, we have to define that
- Are the schemas ...-base still needed if we use privileges instead of barrier views?
- In AW we are supporting Abraxas applications which are not owned by the client - client is part of the scope, and data is in the same db
