from hub import port, sound, button
from runloop import run, sleep_ms
import motor_pair
import motor
import math

############################################################################
# Verander niks aan de code hieronder! Scroll eerst helemaal naar beneden. #
############################################################################

class Robot:
    def __init__(self, motor_links, motor_rechts, motor_arm_voor, motor_arm_achter, wielbasis, wieldiameter):
        motor_pair.pair(motor_pair.PAIR_1, motor_links, motor_rechts)
        self.wielbasis = wielbasis
        self.wieldiameter = wieldiameter
        self.wielomtrek = wieldiameter * math.pi

        self.motor_links = motor_links
        self.motor_rechts = motor_rechts
        
        self.motor_arm_voor = motor_arm_voor
        self.arm_voor_laag = None 
        self.arm_voor_hoog = None

        self.motor_arm_achter = motor_arm_achter
        self.arm_achter_laag = None 
        self.arm_achter_hoog = None

    async def test_arm(self, arm):
        sound.beep(880, 200)
        while True:
            left_pressed = button.pressed(button.LEFT)
            right_pressed = button.pressed(button.RIGHT)
            if left_pressed and not right_pressed:
                await motor.run_for_degrees(arm, 30, 100)
            elif right_pressed and not left_pressed:
                await motor.run_for_degrees(arm, -30, 100)
            elif(left_pressed and right_pressed):
                break

        sound.beep(1320, 200)
        await sleep_ms(2000)

    async def test_arm_voor(self):
        await self.test_arm(self.motor_arm_voor)

    async def test_arm_achter(self):
        await self.test_arm(self.motor_arm_achter)

    def stel_arm_voor_in(self, laag, hoog):
        self.arm_voor_laag = laag
        self.arm_voor_hoog = hoog 

    def stel_arm_achter_in(self, laag, hoog):
        self.arm_achter_laag = laag
        self.arm_achter_hoog = hoog

    def corrigeer_wieldiameter(self, afstand_ingesteld, afstand_gereden):
        self.wieldiameter *= afstand_gereden / afstand_ingesteld

    def corrigeer_wielbasis(self, hoek_ingesteld, hoek_gedraaid):
        self.wielbasis *= hoek_ingesteld / hoek_gedraaid

    async def arm_voor_omhoog(self, snelheid):
        if self.motor_arm_voor is None or self.arm_voor_hoog is None:
            await sound.beep(880, 1000)
        else:
            await motor.run_to_absolute_position(self.motor_arm_voor, self.arm_voor_hoog, snelheid, direction=motor.CLOCKWISE)
            
    async def arm_voor_omlaag(self, snelheid):
        if self.motor_arm_voor is None or self.arm_voor_laag is None:
            await sound.beep(880, 1000)
        else:
            await motor.run_to_absolute_position(self.motor_arm_voor, self.arm_voor_laag, snelheid, direction=motor.COUNTERCLOCKWISE)

    async def arm_achter_omhoog(self, snelheid):
        if self.motor_arm_achter is None or self.arm_achter_hoog is None:
            await sound.beep(880, 1000)
        else:
            await motor.run_to_absolute_position(self.motor_arm_achter, self.arm_achter_hoog, snelheid, direction=motor.CLOCKWISE)

    async def arm_achter_omlaag(self, snelheid):
        if self.motor_arm_achter is None or self.arm_achter_laag is None:
            await sound.beep(880, 1000)
        else:
            await motor.run_to_absolute_position(self.motor_arm_achter, self.arm_achter_laag, snelheid, direction=motor.COUNTERCLOCKWISE)

    async def vooruit(self, afstand, snelheid):
        hoek = int(360 * afstand / (math.pi * self.wieldiameter))
        hoeksnelheid = int(360 * snelheid / (math.pi * self.wieldiameter))
        await motor_pair.move_for_degrees(motor_pair.PAIR_1, hoek, 0, velocity=hoeksnelheid)

    async def achteruit(self, afstand, snelheid):
        await self.vooruit(-afstand, snelheid)

    async def bocht(self, bocht_straal, bocht_hoek, snelheid, direction):
        bocht_hoek_rad = bocht_hoek * math.pi / 180
        bocht_afstand = (bocht_straal + self.wielbasis / 2) * bocht_hoek_rad
        tijd = bocht_afstand / snelheid

        wiel_hoek1 = 360 * bocht_hoek_rad * bocht_straal / self.wielomtrek
        wiel_hoek2 = 360 * bocht_hoek_rad * (bocht_straal + self.wielbasis) / self.wielomtrek

        hoeksnelheid1 = wiel_hoek1 / tijd
        hoeksnelheid2 = wiel_hoek2 / tijd

        if direction == "links":
            motor.run_for_degrees(self.motor_links, int(-wiel_hoek1), int(hoeksnelheid1))
            await motor.run_for_degrees(self.motor_rechts, int(wiel_hoek2), int(hoeksnelheid2))
        elif direction == "rechts":
            motor.run_for_degrees(self.motor_rechts, int(wiel_hoek1), int(hoeksnelheid1))
            await motor.run_for_degrees(self.motor_links, int(-wiel_hoek2), int(hoeksnelheid2))

    async def bocht_links(self, bocht_straal, bocht_hoek, snelheid):
        await self.bocht(bocht_straal, bocht_hoek, snelheid, direction="links")

    async def bocht_rechts(self, bocht_straal, bocht_hoek, snelheid):
        await self.bocht(bocht_straal, bocht_hoek, snelheid, direction="rechts")

    async def draai(self, hoek, snelheid):
        cirkel_omtrek = self.wielbasis * math.pi
        wiel_hoek = hoek * (cirkel_omtrek /self.wielomtrek)
        hoeksnelheid = 360 * snelheid / (math.pi * self.wieldiameter)

        motor.run_for_degrees(self.motor_links, int(wiel_hoek), int(hoeksnelheid))
        await motor.run_for_degrees(self.motor_rechts, int(wiel_hoek), int(hoeksnelheid))

    async def draai_links(self, hoek, snelheid):
        await self.draai(abs(hoek), abs(snelheid))
    
    async def draai_rechts(self, hoek, snelheid):
        await self.draai(-abs(hoek), abs(snelheid))


##########################################################################################
# Vanaf hier kun je de code aanpassen voor jouw eigen robot. Volg de aangegeven stappen. #
##########################################################################################

# Stap 1: Stel eerst je robot in. Verander de poorten, de wielbasis en de wieldiameter als
#         deze anders zijn op jouw eigen robot.
robot = Robot(motor_links = port.A, 
              motor_rechts = port.E, 
              motor_arm_voor = port.D,
              motor_arm_achter = port.C,
              wielbasis = 14.5, 
              wieldiameter = 8.5)

# Stap 2: Om de robot nauwkeuriger te maken, kun je metingen doen en de resultaten daarvan 
#         hieronder invoeren. Je moet hiervoor twee metingen doen.
#
#         !!! Deze metingen zijn optioneel, je kunt ook meteen door naar stap 3 en deze stap 
#         later doen als je robot onnauwkeurig blijkt te zijn. !!!
#
#         Meting 1: Geef de robot de opdracht om 100cm te rijden met het commando (in main)
#                           await robot.vooruit(afstand = 100, snelheid = 20)
#                   Voer de afstand (in cm) die de robot daadwerkelijk gereden heeft 
#                   hieronder in bij "afstand gereden":

robot.corrigeer_wieldiameter(afstand_ingesteld = 100, afstand_gereden = 100)

#         Meting 2: Geef de robot de opdracht om 360 graden te draaien met het commando
#                           await robot.draai(hoek = 360, snelheid = 20)
#                   Voer de hoek die de robot daadwerkelijk heeft gedraaid hieronder in
#                   bij "hoek_gedraaid": 

robot.corrigeer_wielbasis(hoek_ingesteld = 360, hoek_gedraaid = 360)

# Stap 3: Sla deze stap over als je de armen van de robot niet wil gebruiken. Probeer je dat 
#         toch te doen, dan zul je een harde piep van de robot horen om je eraan te herinneren
#         dat je deze stap alsnog moet doen!
#
#         Om de armen te kunnen gebruiken, moeten we de robot eerst vertellen bij welke motor-
#         standen de armen omhoog en omlaag staan. Om erachter te komen welke standen dat zijn, 
#         kun je eerst een test-commando geven (in een verder lege main):
#
#                 await robot.test_arm_voor()
#
#         Als je dit programma runt, zal de robot eerst piepen. Daarna kun je met de pijltjes-
#         knoppen op de robot de voorste arm op en neer bewegen. Zoek de uiterste standen op
#         en noteer de standen van de motor (die staan aangegeven boven in dit scherm). Voer
#         daarna de juiste waarden in in het commando hieronder.
#
# !!! Haal de hasttag (#) hieronder weg en vul de juiste waarden in:
# robot.stel_arm_voor_in(laag = ..., hoog = ...)
#
#         Doe nu hetzelfde voor de achterste arm:

#                 await robot.test_arm_achter()
#
# !!! Haal de hashtag (#) hieronder weg en vul de juiste waarden in:
# robot.stel_arm_achter_in(laag = ..., hoog = ...)


# Stap 4: Schrijf hieronder je programma in de main-functie. Alle code in de main-functie  
#         moet beginnen met een TAB (of een aantal spaties, zolang je maar steeds even 
#         veel gebruikt en de regels netjes onder elkaar komen te staan).
#
#         Hieronder staat een lijst van de commando's die je aan de robot kunt geven. 
#         Om deze commando's aan de robot te geven, gebruik je het volgende patroon:
#                  await robot.commando(argument1 = waarde1, argument2 = waarde2, etc)
#         Bijvoorbeeld, om 100cm vooruit te rijden met een snelheid van 30 cm/s:
#                  await robot.vooruit(afstand = 100, snelheid = 30)
#         Bekijk ook het voorbeeld-programma in main voor meer voorbeelden van commando's.
#
#         Beschikbare commando's:
#             vooruit(afstand, snelheid)
#             achteruit(afstand, snelheid)
#             bocht_links(bocht_straal, bocht_hoek, snelheid)
#             bocht_rechts(bocht_straal, bocht_hoek, snelheid)
#             draai_links(hoek, snelheid)
#             draai_rechts(hoek, snelheid)
#             arm_voor_omhoog(snelheid)
#             arm_voor_omlaag(snelheid)
#             arm_achter_omhoog(snelheid)
#             arm_achter_omlaag(snelheid)

async def main():
    # Dit is een voorbeeld-programma. Verander dit zodat de robot doet wat JIJ wil!
    await robot.arm_voor_omhoog(snelheid = 100)
    await robot.vooruit(afstand = 50, snelheid = 30)
    await robot.bocht_rechts(bocht_straal = 10, bocht_hoek = 180, snelheid = 30)
    await robot.vooruit(afstand = 50, snelheid = 50)
    await robot.arm_voor_omhoog(snelheid = 100)

#########################################
# STOP! Laat de regel hieronder intact. #
#########################################

run(main())
