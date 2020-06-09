# LiSS internsidor

Ett utkast till hur en ny generation av internsidor för LiSS kan se ut.

Systemet är byggt på Django och använder sig av OpenID Connect för autentisering. Tanken är att det här ska vara den enda vägen in till databasen med medlemsregistret, genom att följande funktioner hanteras:
  * Administration av medlemsregistret, via Djangos admin-gränssnitt.
  * Lookup av användare för en extern autentiseringlösning via ett HTTP/JSON-api. Lösenord hanteras dock av det externa systemet.
  * Administration av maillistor.
  * Lookup av mottagares mailadresser för maillistor och mailfiltrering från Postfix, via två små servrar som anropar databasen via Djangos python-api.
  * Allehanda småfunktioner för användare, som att kunna redigera sin egen info eller räkna föreställningar.

## Projektstruktur
Django-hemsidor organiseras i olika moduler eller "apps". I detta projekt finns bara en enda app utvecklad, "batadasen", vilket är där den mesta av koden och logiken finns. I mappen "internsidor" finns inställningarna och konfigurationen för hela hemsidan.

Anledningen till denna struktur är att Django-appar lätt ska kunna återanvändas i andra hemsidor. Exempelvis använder detta projekt appen `mozilla_django_oidc` som sköter autentiseringen via OpenID Connect.

Filer för frontend-utveckling finns i mappen `batadasen/templates/batadasen` och `batadasen/static/batadasen`. Html-filerna är Django-templates som återanvänder kod genom att `base.html` innehåller den grundläggande html-strukturen och sedan fyller varje templatefil sen på själva `content`-blocket med rätt innehåll. 

## Utvecklingsmiljö
Django har en inbyggd utvecklingsserver som man kan använda för lokal utveckling. Innan du kan komma igång behöver du ha installerat Python 3.6 eller högre.

1. För att snabbt installera alla python-dependencies som behövs kan man köra följande:
    ```
    pip install -r requirements.txt
    ```

2. Initialisera en lokal databasfil med:
    ```
    python manage.py migrate
    ```
    Filen "db.sqlite3" kommer skapas.

3. För att kunna använda admingränssnittet behöver man skapa en superanvändare med:
    ```
    python manage.py createsuperuser
    ```

4. Starta utvecklingsservern med:
    ```
    python manage.py runserver
    ```
    Nu kommer du åt hemsidan via http://localhost:8000. Servern kommer automatiskt ladda om sig när man gör ändringar i filer.

Just nu finns ingen förstasida med länkar till de olika sidorna, så man får själv skriva in URL:er för att komma dit man vill. För att se vilka URL:er som finns kan man kika i `internsidor/urls.py` och `batadasen/urls.py`. URL:erna i `batadasen/urls.py` inkluderas under prefixet `/batadasen`. 

Ett urval av de utkast till sidor som finns än så länge:
  * `/admin` - Djangos administrationsinterface. Här lägger man till och redigerar typ allt; personer, användare, maillistor, uppsättningar etc.
  * `/batadasen/minsida` - En sida för att redigera sin egen info.
  * `/batadasen/email_lists` - Lista över e-postlistor och deras medlemmar.
  * `/persons/<medlemsnummer>` - Information om en person.
  * `/api` - innehåller endpoints för ett JSON-api för att göra lookups av användare. Går inte att komma åt som vanlig användare utan det krävs att HTTP-anropet har en särskild nyckel som bara inloggningsservern har. 

Något att tänka på när man använder lokala utvecklingsservern är att funktionen att skicka mail till personer så att de kan skapa en användare inte fungerar utan vidare. Man får då skapa en användare manuellt från admin-interfacet. 

## Extern lookup mot databasen
I projektet finns också några små python-skript som kan använda Djangos databas-koppling för att publicera grejer åt andra system som behöver information från databasen. Det ersätter direkt uppkoppling mot Postgres-databasen som gjorts tidigare.

### Lookup av mottagare för epost-listor
Filen `postfix_daemon.py` är en liten TCP-server som svarar på anrop från Postfix via API:t från följande sida: http://www.postfix.org/socketmap_table.5.html

### Mail-filtrering
För att kunna filtrera ut så att endast vissa personer kan skicka mail till vissa maillistor används ett så kallat milter (mail filter) som är ett program som hakar på i vissa steg av SMTP-protokollet och kan avbryta en mail-transaktion om mottagaren inte uppfyller vissa villkor. Det finns i filen `lissmilter.py` och är baserat på biblioteket `pymilter`.

Vi använder det också för att skriva om ämnesraden till vissa maillistor.
