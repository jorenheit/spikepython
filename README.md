# Welkom!
Wat leuk dat je verder gaat met programmeren in Python na de workshop. Hier kun je alles terugvinden wat je hebt gebruikt tijdens de workshop.

## workshop.llsp3
In dit bestand vind je alles wat je nodig hebt om je robot in actie te laten komen. Open het bestand op je computer (het is een Spike-project bestand) en volg de stappen die hierin beschreven staan.

## presentatie.pdf
Dit is (een verbeterde versie van) de presentatie die tijdens de workshop op het scherm heeft gestaan. Als je daar nog eens rustig naar wilt kijken, download dan dit bestand.

## UbboSpike
### Installatie
Zoals je in het workshop-bestand kunt zien, is er eerst een heleboel code nodig voordat je de robot commando's kunt geven. Dat maakt het bestand niet heel overzichtelijk en bovendien moet je al deze code steeds weer toevoegen als je een nieuw project start. Dit kun je voorkomen door UbboSpike te installeren op je robot. Dat werkt als volgt:

1. Download het ubbospike.zip bestand en pak de bestanden uit in een nieuwe map.
2. Dubbelklik op run.bat. Er wordt een nieuw project aangemaakt: installeer_ubbospike.llsp3
3. Open dit project in de Spike software, verbind je robot en voer het programma uit op je robot.
4. Als alles goed gaat, verschijnt er in beeld dat de upload geslaagd is. UbboSpike is nu geïnstalleerd op je robot.

Als je UbboSpike eenmaal hebt geïnstalleerd, hoef je deze stappen niet te herhalen. Een update van de firmware van je robot kan er wel toe leiden dat je deze stappen opnieuw moet doen.

### UbboSpike gebruiken
In het demobestand (ubbospike_demo.llsp3) kun je zien hoe je UbboSpike gebruikt. Het grote verschil is dat je nu de UbboSpike module moet importeren:
```
from UbboSpike import Robot
```
Daarna kun je net als voorheen je robot aanmaken, instellen en besturen.

### Commando's Stapelen
Een nieuwe feature van UbboSpike is dat je commando's kunt stapelen en daarna tegelijkertijd kunt uitvoeren. Hiervoor gebruik je de nieuwe functies `taak()` en `doe_taken()`. Eerst verzamel je de commando's die je tegelijkertijd wilt uitvoeren. Let er wel op dat dit taken zijn die tegelijkertijd uitgevoerd kunnen worden (je kunt natuurlijk niet tegelijkertijd vooruit en achteruit rijden).
```
vooruit =  robot.taak("vooruit", afstand = 50, snelheid = 50)
arm_voor = robot.taak("arm_voor_procent", percentage = 50, snelheid = 200) 
arm_achter = robot.taak("arm_achter_procent", percentage = 50, snelheid = 200)
```
Daarna kun je al deze taken doorgeven aan de `doe_taken()`-functie:
```
robot.doe_taken(vooruit, arm_voor, arm_achter)
```
De robot zal deze taken tegelijkertijd uitvoeren (als dat kan).

## Hulp nodig?
Stuur me gerust een berichtje via teams (Meneer Heit) of Magister. Ik help je graag!
