from hub import port
from runloop import run
import motor_pair
import motor
import math

class Robot:
    def __init__(self, motor_links, motor_rechts, wielbasis, wieldiameter):
        motor_pair.pair(motor_pair.PAIR_1, motor_links, motor_rechts)
        self.wielbasis = wielbasis
        self.wieldiameter = wieldiameter
        self.wielomtrek = wieldiameter * math.pi
        self.motor_links = motor_links
        self.motor_rechts = motor_rechts
        
    def corrigeer_wieldiameter(self, afstand_ingesteld, afstand_gereden):
        self.wieldiameter *= afstand_gereden / afstand_ingesteld

    def corrigeer_wielbasis(self, hoek_ingesteld, hoek_gedraaid):
        self.wielbasis *= hoek_ingesteld / hoek_gedraaid
        
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


# Stel hieronder eerst je motor in. Verander de vraagtekens naar de juiste letters en waarden:
robot = Robot(motor_links = port.?, motor_rechts = port.?, wielbasis = ?, wieldiameter = ?)
robot.corrigeer_wieldiameter(afstand_ingesteld = 100, afstand_gereden = 100)
robot.corrigeer_wielbasis(hoek_ingesteld = 360, hoek_gedraaid = 360)

async def main():
    # Schrijf hieronder de code om de robot mee te sturen.

run(main())
