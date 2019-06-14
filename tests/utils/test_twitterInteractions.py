



from utils.twitterInteractions import *


def test_is_connected():
    basicRun = False
    try:
        temp = is_connected()
        basicRun = True
    except:
        basicRun = False
    assert basicRun
    return