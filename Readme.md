# LiSS internsidor

Linköpings Studentspex internsidor anno 2020, året då pesten kom till byn.

Systemet är byggt på Django och använder sig av OpenID Connect för autentisering. Tanken är att det här ska vara den enda vägen in till databasen med medlemsregistret, genom att följande funktioner hanteras:
  * Administration av medlemsregistret, via Djangos admin-gränssnitt.
  * Lookup av användare för en extern autentiseringlösning via ett HTTP/JSON-api. Lösenord hanteras dock av det externa systemet.
  * Administration av maillistor.
  * Lookup av mottagares mailadresser för maillistor och mailfiltrering från Postfix, via två små servrar som anropar databasen via Djangos python-api.
  * Allehanda småfunktioner för användare, som att kunna redigera sin egen info eller räkna föreställningar.

## Projektstruktur
Django-hemsidor organiseras i olika moduler eller "apps", vilket är där själva koden och logiken finns. I mappen "internsidor" finns inställningarna och konfigurationen för hela hemsidan.

Anledningen till denna struktur är att Django-appar lätt ska kunna återanvändas i andra hemsidor. Exempelvis använder detta projekt appen `mozilla_django_oidc` som sköter autentiseringen via OpenID Connect.

I detta projekt finns för närvarande två appar:
  * `batadasen`: innehåller den mesta koden som har med medlemsregistret och e-postlistor att göra.
  * `assetmanager`: inventariesystemet för spexets prylar.

Filer för frontend-utveckling finns i mappen `batadasen/templates/batadasen` och `batadasen/static/batadasen`. Html-filerna är Django-templates som återanvänder kod genom att `base.html` innehåller den grundläggande html-strukturen och sedan fyller varje templatefil sen på själva `content`-blocket med rätt innehåll. 

## Utvecklingsmiljö
Django har en inbyggd utvecklingsserver som man kan använda för lokal utveckling. Innan du kan komma igång behöver du ha installerat Python 3.6 eller högre. Det är också starkt rekommenderat att du sköter utveckilengen i en så kallad virtuella miljö, inte att förväxla med en virtuell maskin.

1. Skapa först den virtuella miljön:
   ```
   python3 -m venv virtual-environment
   ```
   Vad det i praktiken gör är att det skapar en mapp `virtual-environment` som kommer innehålla en pythoninstallation separat från operativsystemets.
   
   Var gång du sedan ska utveckla internsidorna ska du börja med att "aktivera" den här utvecklingsmiljön i ditt skal:
   ```
   # På Linux, Mac OS eller Windows POSIX-kompabilitetslager likt WSL och MingW
   source virtual-environment/bin/activate 
   # På Windows med cmd
   virtual-environment\Scripts\activate.bat
   # På Windows med PowerShell
   virtual-environment\Scripts\activate.ps1
   ```

1. För att snabbt installera alla python-dependencies som behövs kan man köra följande:
    ```
    python3 -m pip install -r requirements.txt
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

Något att tänka på när man använder lokala utvecklingsservern är att funktionen att skicka mail till personer så att de kan skapa en användare inte fungerar utan vidare. Man får då skapa en användare manuellt från admin-interfacet. 

## Extern lookup mot databasen
I projektet finns också några små python-skript som kan använda Djangos databas-koppling för att publicera grejer åt andra system som behöver information från databasen. Det ersätter direkt uppkoppling mot Postgres-databasen som gjorts tidigare.

### Lookup av mottagare för epost-listor
Filen `postfix_daemon.py` är en liten TCP-server som svarar på anrop från Postfix via API:t från följande sida: http://www.postfix.org/socketmap_table.5.html

### Mail-filtrering
För att kunna filtrera ut så att endast vissa personer kan skicka mail till vissa maillistor används ett så kallat milter (mail filter) som är ett program som hakar på i vissa steg av SMTP-protokollet och kan avbryta en mail-transaktion om avsändaren inte uppfyller vissa villkor. Det finns i filen `lissmilter.py` och är baserat på biblioteket `pymilter`.

Vi använder det också för att skriva om ämnesraden till vissa maillistor.
