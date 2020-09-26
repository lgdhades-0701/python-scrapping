class Env:
    # a variable which indicates the year to scrap data. If it set None, it will indicate the current year (e.g. _Year=None is equal to _Year=2020)
    _Year = 2020

    # a variable which indicates the month to scrap data. _Month 0: January, _Month 1: February,  11: December. If it set None, it indicates the latest month depends on the _Year variable
    # (e.g _Year=2020 or None and _Month is set to None, _Month variable indicates September so it's value is 8. If _Year=2019 and _Month=None, it indicates December so 11)
    _Month = 8

    # a variable on how far to then scrap from the current date (according to the _Year and _Month). If it set None, it will scrap all days in the month
    _BackDate = None

    #  max number of races for each meeting to scrap. range is 1 ~ 12
    _MaxRace = 12

    # log & output file path
    _LogPath = ".\log"
    _OutputCsvPath = ".\output"
