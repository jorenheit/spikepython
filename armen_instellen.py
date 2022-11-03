from spike import *
from spike.control import *

arm_voor = Motor('D')
arm_achter = Motor('C')
hub = PrimeHub()

def armen_instellen(speed = 20):
    l = hub.left_button
    r = hub.right_button
    count = 1
    DELAY = 0.2
    count_changed = True
    while (count < 3):
        if count_changed: 
            hub.light_matrix.write(count) 
        
        arm = arm_voor if count == 1 else arm_achter
        l_press = l.is_pressed()
        r_press = r.is_pressed()
        if l_press and r_press:
            count += 1
            count_changed = True
            l.wait_until_released()
            r.wait_until_released()
            continue
        elif l_press:
            wait_for_seconds(DELAY)
            if l.is_pressed() and not r.is_pressed():
                arm.start(speed)
                l.wait_until_released()
                arm.stop()
        elif r_press:   
            wait_for_seconds(DELAY)         
            if r.is_pressed() and not l.is_pressed():
                arm.start(-speed)
                r.wait_until_released()
                arm.stop()
            
        count_changed = False

    return arm_voor.get_position(), arm_achter.get_position()
    

beginstand_voor, beginstand_achter = armen_instellen()
print('Stand voor: {voor}, Stand achter: {achter}'.format(voor=beginstand_voor, achter=beginstand_achter))
hub.light_matrix.write('Klaar!')