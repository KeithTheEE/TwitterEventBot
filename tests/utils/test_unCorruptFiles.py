


from utils.unCorruptFiles import *


def test_cleanIt():

    invalidBytesCount, validBytesCount, totalBytesCount, edited = clear_corrupted_bytes('tests/clean_missile.txt', allowedToEdit=False)
    #clear_corrupted_bytes('tests/corrupt_missile.txt', allowedToEdit=False)
    pass
