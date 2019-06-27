

'''
This should handle all hardware specific issues,
(raspberry pi gpio setup, and testing computer setup)
'''

import logging


def tryRPiProcesses():
    rPi = False
    try: 
        import RPi.GPIO as GPIO 
        # Currently on the raspberry pi, or have a fake pi gpio library running
        rPi = True
        # These two lines are for the pi graphics handling the plots
        import matplotlib as mpl
        mpl.use('Agg')
        # Image Data
        import matplotlib.pyplot as plt
        import matplotlib.mlab as mlab
        import matplotlib.dates as mdates
        # Actual twitter bot info
        import getKMKeys # Format of CK, CS, AK, AS
        #[CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET]
    except:
        # Image Data
        import matplotlib.pyplot as plt
        import matplotlib.mlab as mlab
        import matplotlib.dates as mdates
        rPi = False
        # Demo bot info since testing uses @keithChatterBot
        #   Basically, I won't be using keith_event on the computer unless specific cir.
        import getChatBotKeys as getKMKeys
    return rPi