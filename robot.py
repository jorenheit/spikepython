from hub import port, sound, button
from runloop import run, sleep_ms
import motor_pair
import motor
import math

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

    def stel_arm_voor_in(self, motor_arm_voor, arm_voor_laag, arm_voor_hoog):
        self.motor_arm_voor = motor_arm_voor
        self.arm_voor_hoog = arm_voor_hoog 
        self.arm_voor_laag = arm_voor_laag

    def stel_arm_achter_in(self, motor_arm_achter, arm_achter_laag, arm_achter_hoog):
        self.motor_arm_achter = motor_arm_achter
        self.arm_achter_hoog = arm_achter_hoog
        self.arm_achter_laag = arm_achter_laag

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


# Stel hier je robot in:
robot = Robot(motor_links = port.A, 
              motor_rechts = port.E, 
              motor_arm_voor = port.D,
              motor_arm_achter = port.C,
              wielbasis = 14.5, 
              wieldiameter = 8.5)

robot.corrigeer_wieldiameter(afstand_ingesteld = 100, afstand_gereden = 100)
robot.corrigeer_wielbasis(hoek_ingesteld = 360, hoek_gedraaid = 360)

async def main():
    # Hier komt de code om de robot mee te besturen

run(main())
