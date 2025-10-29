# LiSS internsidor
Linköpings Studentspex internsidor anno 2020, året då pesten kom till byn.

Systemet är byggt på Django och använder sig av OpenID Connect för autentisering. Tanken är att det här ska vara den
enda vägen in till databasen med medlemsregistret, genom att följande funktioner hanteras:
  * Administration av medlemsregistret, via Djangos admin-gränssnitt.
  * Lookup av användare för en extern autentiseringlösning via ett HTTP/JSON-api. Lösenord hanteras dock av det externa
    systemet.
  * Administration av maillistor.
  * Lookup av mottagares mailadresser för maillistor och mailfiltrering från Postfix, via två små servrar som anropar
    databasen via Djangos python-api.
  * Allehanda småfunktioner för användare, som att kunna redigera sin egen info eller räkna föreställningar.

## Projektstruktur
Django-hemsidor organiseras i olika moduler eller "apps", vilket är där själva koden och logiken finns. I mappen
"internsidor" finns inställningarna och konfigurationen för hela hemsidan.

Anledningen till denna struktur är att Django-appar lätt ska kunna återanvändas i andra hemsidor. Exempelvis använder
detta projekt appen `mozilla_django_oidc` som sköter autentiseringen via OpenID Connect.

I detta projekt finns för närvarande två appar:
  * `batadasen`: innehåller den mesta koden som har med medlemsregistret och e-postlistor att göra.
  * `assetmanager`: inventariesystemet för spexets prylar.

Filer för frontend-utveckling finns i mappen `batadasen/templates/batadasen` och `batadasen/static/batadasen`.
Html-filerna är Django-templates som återanvänder kod genom att `base.html` innehåller den grundläggande html-strukturen
och sedan fyller varje templatefil sen på själva `content`-blocket med rätt innehåll.

## Utvecklingsmiljö
Innan du kan komma igång behöver du ha installerat en liten mjukvara som heter `uv`. Det är ett smidigt program som
abstraherar bort saker som olika versioner av Python eller installation av dependencies.

### uv
1. Gå till https://docs.astral.sh/uv/ så får du hjälp med hur du installerar för just din brödrost.
2. Det finns inget steg 2, du är klar nu.

Om du har utvecklat i Python förut kommer du få vänja dig att skriva `uv` innan kommandon. Det ersätter att hålla koll
på virtuell miljöer och pip.

### Initisera en databas
Initialisera en lokal databasfil med:
```
uv run manage.py migrate
```
Filen "db.sqlite3" kommer skapas.

För att kunna använda admingränssnittet behöver man skapa en superanvändare med:
```
uv run manage.py createsuperuser
```

### Starta utveckolingsserver
Django har en inbyggd utvecklingsserver som man kan använda för lokal utveckling. Starta utvecklingsservern med:
```
python manage.py runserver
```

Nu kommer du åt hemsidan via http://localhost:8000. Servern kommer automatiskt ladda om sig när man gör ändringar i
filer så du kan ha den igång hela tiden när du utvecklar.

Något att tänka på när man använder lokala utvecklingsservern är att funktionen att skicka mail till personer så att de
kan skapa en användare inte fungerar utan vidare. Man får då skapa en användare manuellt från admin-interfacet.

### Generera hittepådata
För att slippa skapa upp alla modeller från scratch när man testar kan man använda skriptet `generate_fixture.py`:
```
uv run scripts/generate_fixture.py
```

Detta skapar filen fixture.json som sedan kan importeras till databasen:
```
uv run  manage.py loaddata --format json fixture.json
```

## Extern lookup mot databasen
I projektet finns också några små python-skript som kan använda Djangos databas-koppling för att publicera grejer åt
andra system som behöver information från databasen. Det ersätter direkt uppkoppling mot Postgres-databasen som gjorts
tidigare.

### Lookup av mottagare för epost-listor
Filen `postfix_daemon.py` är en liten TCP-server som svarar på anrop från Postfix via API:t från följande sida:
http://www.postfix.org/socketmap_table.5.html

### Mail-filtrering
För att kunna filtrera ut så att endast vissa personer kan skicka mail till vissa maillistor används ett så kallat
milter (mail filter) som är ett program som hakar på i vissa steg av SMTP-protokollet och kan avbryta en
mail-transaktion om avsändaren inte uppfyller vissa villkor. Det finns i filen `lissmilter.py` och är baserat på
biblioteket `pymilter`.

Vi använder det också för att skriva om ämnesraden till vissa maillistor.
