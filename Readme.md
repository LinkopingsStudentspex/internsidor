# LiSS internsidor

Ett utkast till hur en ny generation av internsidor för LiSS kan se ut.

Systemet är byggt på Django och använder sig av OpenID Connect för autentisering. Tanken är att det här ska vara den enda vägen in till databasen med medlemsregistret, genom att följande funktioner hanteras:
  * Administration av medlemsregistret, via Djangos admin-gränssnitt.
  * Lookup av användare för en extern autentiseringlösning via ett HTTP/JSON-api. Lösenord hanteras dock av det externa systemet.
  * Administration av maillistor.
  * Lookup av mottagares mailadresser för maillistor från Postfix, via en liten TCP-server som anropar databasen via Djangos python-api.
  * Allehanda småfunktioner för användare, som att kunna redigera sin egen info eller räkna föreställningar.