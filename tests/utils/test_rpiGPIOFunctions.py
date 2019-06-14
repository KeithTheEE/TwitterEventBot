



from utils.rpiGPIOFunctions import *
 
 
def test_checkHardware():
    '''
    This test just verifies the boolean is called correctly after an
    attempt to import RPi.GPIO
    '''
    localMeasure = False
    try:
        import RPi.GPIO as GPIO
        localMeasure = True
    except:
        localMeasure = False

    assert checkHardware() == localMeasure


    return

