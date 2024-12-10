from hub import port, sound, button
from runloop import run, sleep_ms
from collections import namedtuple
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

        self.motor_busy = {
            self.motor_arm_voor: False,
            self.motor_arm_achter: False,
            self.motor_links: False,
            self.motor_rechts: False
        }

    async def test_arm(self, arm):
        sound.beep(880, 200)

        while True:
            left_pressed = button.pressed(button.LEFT)
            right_pressed = button.pressed(button.RIGHT)
            if left_pressed and not right_pressed:
                motor.run(arm, 100)
            elif right_pressed and not left_pressed:
                motor.run(arm, -100)
            elif not left_pressed and not right_pressed:
                motor.stop(arm)
            elif left_pressed and right_pressed:
                motor.stop(arm)
                break

        sound.beep(1320, 200)
        await sleep_ms(1000)

    async def test_arm_voor(self):
        await self.test_arm(self.motor_arm_voor)

    async def test_arm_achter(self):
        await self.test_arm(self.motor_arm_achter)
        
    async def test_armen(self):
        await self.test_arm(self.motor_arm_voor)
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

    ArmCommando = namedtuple("ArmCommando", ["arm", "percentage", "snelheid"])
    RechtdoorCommando = namedtuple("RechtdoorCommando", ["richting", "afstand", "snelheid"])
    BochtCommando = namedtuple("BochtCommando", ["richting", "straal", "hoek", "snelheid"])
    DraaiCommando = namedtuple("DraaiCommando", ["richting", "hoek", "snelheid"])

    def taak(self, naam, **args):
        if naam == "arm_voor_omhoog":
            return Robot.ArmCommando(arm = self.motor_arm_voor, percentage = 100, snelheid = args["snelheid"])
        if naam == "arm_voor_omlaag":
            return Robot.ArmCommando(arm = self.motor_arm_voor, percentage = 0, snelheid = args["snelheid"])
        if naam == "arm_achter_omhoog":
            return Robot.ArmCommando(arm = self.motor_arm_achter, percentage = 100, snelheid = args["snelheid"])
        if naam == "arm_achter_omlaag":
            return Robot.ArmCommando(arm = self.motor_arm_achter, percentage = 0, snelheid = args["snelheid"])
        if naam == "arm_voor_procent":
            return Robot.ArmCommando(arm = self.motor_arm_voor, percentage = args["percentage"], snelheid = args["snelheid"])
        if naam == "arm_achter_procent":
            return Robot.ArmCommando(arm = self.motor_arm_achter, percentage = args["percentage"], snelheid = args["snelheid"])
        if naam == "rechtdoor":
            return Robot.RechtdoorCommando(richting = args["richting"], afstand = args["afstand"], snelheid = args["snelheid"])
        if naam == "vooruit":
            return Robot.RechtdoorCommando(richting = "vooruit", afstand = args["afstand"], snelheid = args["snelheid"])
        if naam == "achteruit":
            return Robot.RechtdoorCommando(richting = "achteruit", afstand = args["afstand"], snelheid = args["snelheid"])
        if naam == "bocht":
            return Robot.BochtCommando(richting = args["richting"], straal = args["straal"], hoek = args["hoek"], snelheid = args["snelheid"])
        if naam == "bocht_links":
            return Robot.BochtCommando(richting = "links", straal = args["straal"], hoek = args["hoek"], snelheid = args["snelheid"])
        if naam == "bocht_rechts":
            return Robot.BochtCommando(richting = "rechts", straal = args["straal"], hoek = args["hoek"], snelheid = args["snelheid"])
        if naam == "draai":
            return Robot.DraaiCommando(richting = args["richting"], hoek = args["hoek"], snelheid = args["snelheid"])
        if naam == "draai_links":
            return Robot.DraaiCommando(richting = "links", hoek = args["hoek"], snelheid = args["snelheid"])
        if naam == "draai_rechts":
            return Robot.DraaiCommando(richting = "rechts", hoek = args["hoek"], snelheid = args["snelheid"])

        raise ValueError("Unknown command name: {}".format(naam))

    class BeweegStopConditie:
        def __init__(self, motor_links, motor_rechts, delta_links, delta_rechts):
            self.delta_links = delta_links
            self.delta_rechts = delta_rechts
            self.count_links = 0
            self.count_rechts = 0

            self.motor_links = motor_links
            self.motor_rechts = motor_rechts

            self.stand_links = None
            if motor_links is not None:
                self.stand_links = motor.absolute_position(motor_links)
                while self.stand_links < 0: self.stand_links += 360

            self.stand_rechts = None
            if motor_rechts is not None:
                self.stand_rechts = motor.absolute_position(motor_rechts)
                while self.stand_rechts < 0: self.stand_rechts += 360

        def __call__(self):
            if self.motor_links is None or self.motor_rechts is None or self.stand_links is None or self.stand_rechts is None:
                return True

            links_nu = motor.absolute_position(self.motor_links)
            while links_nu < 0: links_nu += 360
            d = abs(links_nu - self.stand_links)
            self.count_links += min(d, 360 - d)
            self.stand_links = links_nu

            rechts_nu = motor.absolute_position(self.motor_rechts)
            while rechts_nu < 0: rechts_nu += 360
            d = abs(rechts_nu - self.stand_rechts)
            self.count_rechts += min(d, 360 - d)
            self.stand_rechts = rechts_nu

            stop_links = False
            if self.count_links >= self.delta_links:
                motor.stop(self.motor_links)
                stop_links = True

            stop_rechts = False
            if self.count_rechts >= self.delta_rechts:
                motor.stop(self.motor_rechts)
                stop_rechts = True

            return stop_links and stop_rechts

        def motoren(self):
            return (self.motor_links, self.motor_rechts)

    class ArmStopConditie:
        def __init__(self, arm, direction, target):
            self.arm = arm
            self.direction = direction
            self.target = target

        def __call__(self):
            if self.arm is None or self.direction is None or self.target is None:
                return False

            current = motor.absolute_position(self.arm)
            while current < 0: current += 360
            if (self.direction == motor.CLOCKWISE and current > self.target) or (self.direction == motor.COUNTERCLOCKWISE and current < self.target):
                motor.stop(self.arm)
                return True

            return False

        def motoren(self):
            return (self.arm,)    

    class Idle:
        def __call__(self):
            return True    
        def motoren(self):
            return ()

    async def doe_taken(self, *taken):
        stop_conditions = []
        for taak in taken:
            s = None
            if isinstance(taak, Robot.ArmCommando):
                s = await self.start_arm_commando(taak)
            elif isinstance(taak, Robot.RechtdoorCommando):
                s = await self.start_rechtdoor_commando(taak)
            elif isinstance(taak, Robot.BochtCommando):
                s = await self.start_bocht_commando(taak)
            elif isinstance(taak, Robot.DraaiCommando):
                s = await self.start_draai_commando(taak)
            if s is not None:
                stop_conditions.append([s, False])

        for (stop, done) in stop_conditions:
            self.motor_busy.update({m: True for m in stop.motoren()})

        while any(not stop[1] for stop in stop_conditions):
            for idx, (stop, done) in enumerate(stop_conditions):
                if not done and stop():
                    stop_conditions[idx][1] = True
                    self.motor_busy.update({m: False for m in stop.motoren()})

        
    async def start_rechtdoor_commando(self, commando):
        if self.motor_busy[self.motor_links] or self.motor_busy[self.motor_rechts]:
            return Robot.Idle()

        hoek_delta = int(360 * abs(commando.afstand) / (math.pi * self.wieldiameter))
        hoeksnelheid = int(360 * abs(commando.snelheid) / (math.pi * self.wieldiameter))        
        
        factor = 1 if commando.richting == "vooruit" else -1 if commando.richting == "achteruit" else 0
        if factor == 0:
            return Robot.Idle()

        motor.run(self.motor_links, -hoeksnelheid * factor)
        motor.run(self.motor_rechts, hoeksnelheid * factor)
        return Robot.BeweegStopConditie(self.motor_links, self.motor_rechts, hoek_delta, hoek_delta)

    async def start_bocht_commando(self, commando):
        if self.motor_busy[self.motor_links] or self.motor_busy[self.motor_rechts]:
            return Robot.Idle()

        hoek_rad = commando.hoek * math.pi / 180
        afstand = (commando.straal + self.wielbasis / 2) * hoek_rad
        tijd = afstand / commando.snelheid

        hoek_binnen = 360 * hoek_rad * commando.straal / self.wielomtrek
        hoek_buiten = 360 * hoek_rad * (commando.straal + self.wielbasis) / self.wielomtrek

        hoeksnelheid_binnen = int(hoek_binnen / tijd)
        hoeksnelheid_buiten = int(hoek_buiten / tijd)   

        if commando.richting == "links":
            motor.run(self.motor_links, -hoeksnelheid_binnen)
            motor.run(self.motor_rechts, hoeksnelheid_buiten)
            return Robot.BeweegStopConditie(self.motor_links, self.motor_rechts, hoek_binnen, hoek_buiten)
        elif commando.richting == "rechts":
            motor.run(self.motor_links, -hoeksnelheid_buiten)
            motor.run(self.motor_rechts, hoeksnelheid_binnen)
            return Robot.BeweegStopConditie(self.motor_links, self.motor_rechts, hoek_buiten, hoek_binnen)
        
        return Robot.Idle()

    async def start_arm_commando(self, commando):
        if self.motor_busy[commando.arm]:
            return Robot.Idle()

        if commando.arm == self.motor_arm_voor:
            hoog = self.arm_voor_hoog
            laag = self.arm_voor_laag
        elif commando.arm == self.motor_arm_achter:
            hoog = self.arm_achter_hoog
            laag = self.arm_achter_laag
        else:
            hoog = None
            laag = None

        if commando.arm is None or laag is None or hoog is None:
            await sound.beep(880, 1000)
            return Robot.Idle()

        hoog_norm = hoog - laag
        while hoog_norm < 0: hoog_norm += 360
        target = int(hoog_norm / 100 * commando.percentage)
        current = motor.absolute_position(commando.arm) - laag
        while current < 0: current += 360
        if current > hoog_norm:
            current = hoog_norm if (current - hoog_norm) < (360 - current) else 0
        if abs(current - target) <= 5: return Robot.Idle()
        direction = motor.CLOCKWISE if current < target else motor.COUNTERCLOCKWISE
        target = (target + laag) % 360

        direction_factor = 1 if direction == motor.CLOCKWISE else -1
        motor.run(commando.arm, commando.snelheid * direction_factor)
        return Robot.ArmStopConditie(commando.arm, direction, target)

    async def start_draai_commando(self, commando):
        hoek = commando.hoek * (self.wielbasis * math.pi /self.wielomtrek)
        hoeksnelheid = 360 * commando.snelheid / (math.pi * self.wieldiameter)

        factor = 1 if commando.richting == "links" else -1 if commando.richting == "rechts" else 0
        if factor == 0: return Robot.Idle()

        motor.run(self.motor_links, int(factor * hoeksnelheid))
        motor.run(self.motor_rechts, int(factor * hoeksnelheid))
        return Robot.BeweegStopConditie(self.motor_links, self.motor_rechts, hoek, hoek)

    async def arm_voor_procent(self, percentage, snelheid):
        await self.doe_taken(self.taak("arm_voor_procent", percentage = percentage, snelheid = snelheid))

    async def arm_voor_omhoog(self, snelheid):
        await self.doe_taken(self.taak("arm_voor_omhoog", snelheid = snelheid))

    async def arm_voor_omlaag(self, snelheid):
        await self.doe_taken(self.taak("arm_voor_omlaag", snelheid = snelheid))

    async def arm_achter_procent(self, percentage, snelheid):
        await self.doe_taken(self.taak("arm_achter_procent", percentage = percentage, snelheid = snelheid))

    async def arm_achter_omhoog(self, snelheid):
        await self.doe_taken(self.taak("arm_achter_omhoog", snelheid = snelheid))

    async def arm_achter_omlaag(self, snelheid):
        await self.doe_taken(self.taak("arm_achter_omlaag", snelheid = snelheid))

    async def rechtdoor(self, richting, afstand, snelheid):
        await self.doe_taken(self.taak("rechtdoor", richting = richting, afstand = afstand, snelheid = snelheid))

    async def vooruit(self, afstand, snelheid):
        await self.doe_taken(self.taak("vooruit", afstand = afstand, snelheid = snelheid))

    async def achteruit(self, afstand, snelheid):
        await self.doe_taken(self.taak("achteruit", afstand = afstand, snelheid = snelheid))

    async def bocht(self, richting, straal, hoek, snelheid):
        await self.doe_taken(self.taak("bocht", richting = richting, straal = straal, hoek = hoek, snelheid = snelheid))

    async def bocht_links(self, straal, hoek, snelheid):
        await self.doe_taken(self.taak("bocht_links", straal = straal, hoek = hoek, snelheid = snelheid))

    async def bocht_rechts(self, straal, hoek, snelheid):
        await self.doe_taken(self.taak("bocht_rechts", straal = straal, hoek = hoek, snelheid = snelheid))

    async def draai(self, richting, hoek, snelheid):
        await self.doe_taken(self.taak("draai", richting = richting, hoek = hoek, snelheid = snelheid))

    async def draai_links(self, hoek, snelheid):
        await self.doe_taken(self.taak("draai_links", hoek = hoek, snelheid = snelheid))
        
    async def draai_rechts(self, hoek, snelheid):
        await self.doe_taken(self.taak("draai_rechts", hoek = hoek, snelheid = snelheid))