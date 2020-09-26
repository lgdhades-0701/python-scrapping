# - *- coding: utf- 8 - *-
from datetime import datetime
from datetime import date
from datetime import timedelta
from bs4 import BeautifulSoup
import os.path
from env import Env
import csv
import calendar
import sys
import requests
import json

_OutputCsvPath = Env._OutputCsvPath

# set last day to scrap the data from the env file
_Year = Env._Year
_Month = Env._Month
_Day = 1
_BackDate = Env._BackDate
_MaxRace = Env._MaxRace
curDate = datetime.now()
if _Year is None:
    _Year = curDate.year
    if _Month is None:
        _Month = curDate.month - 1
        _Day = curDate.day
    else:
        if _Month > curDate.month - 1:
            print ('The inputted month is out the scope.')
            sys.exit()
        elif _Month == curDate.month - 1:
            _Day = curDate.day
        else:
            _Day = calendar.monthrange(_Year, _Month + 1)[1]
else:
    if _Year > curDate.year:
        print ('The inputted year is out the scope.')
        sys.exit()
    elif _Year == curDate.year:
        if _Month is None:
            _Month = curDate.month - 1
            _Day = curDate.day
        else:
            if _Month > curDate.month - 1:
                print ('The inputted month is out the scope.')
                sys.exit()
            elif _Month == curDate.month - 1:
                _Day = curDate.day
            else:
                _Day = calendar.monthrange(_Year, _Month + 1)[1]
    else:
        if _Month is None:
            _Month = 11
            _Day = calendar.monthrange(_Year, _Month + 1)[1]
        else:
            _Day = calendar.monthrange(_Year, _Month + 1)[1]

print (_Year, _Month, _Day, _BackDate)
logFileName = str(_Year) + str(_Month) + str(_Day)
_logFile = Env._LogPath + "\\" + logFileName

if (os.path.isdir(_OutputCsvPath) == False):
    os.mkdir(_OutputCsvPath)
if (os.path.isdir(Env._LogPath) == False):
    os.mkdir(Env._LogPath)

resultList = []
resultDetail = []


class ResultList:
    racecorse = ''
    id = ''
    club = ''
    date = ''


class TableData:
    date = ''
    meeting = ''
    race = ''
    start = ''
    cla = ''
    dis = ''
    prise = ''
    plc = ''
    number = ''
    horse = ''
    stake = ''
    f400 = ''
    l800 = ''
    l600 = ''
    l400 = ''
    l200 = ''
    time = ''


MonthList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def getResultList():
    resultList = []
    start_date = 1
    start_str = ''
    try:
        url = "https://loveracing.nz/ServerScript/RaceInfo.aspx/GetMeetingResults"
        if _BackDate is None:
            start_date = 1
        else :
            if _BackDate > _Day :
                start_date = 1
                print ('You entered a backdate bigger than the current date. Scrapping from on 1st.')
            else :
                start_date = _Day - _BackDate + 1

        start_str = str(start_date) + ' ' + MonthList[_Month] + ' ' + str(_Year)
        json_param = {
            'start' : start_str
        }
        payload = json.dumps(json_param)
        headers = {
            'referer': 'https://loveracing.nz/RaceInfo',
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        meetingResults = json.loads(response.text.encode('utf8'))
        content_uni = list(meetingResults.values())[0]
        content = json.loads(content_uni.encode('utf-8'))
        if content == False :
            return
        for i in content :
            itemList = list(i.values())
            item_date = itemList[1]
            item_racecorse = itemList[4]
            item_club = itemList[3]
            item_id = itemList[2]
            str_comp = item_date[-3:]
            if MonthList[_Month] == str_comp :
                objResultList = ResultList()
                objResultList.id = item_id
                objResultList.racecorse = item_racecorse
                objResultList.club = item_club
                objResultList.date = item_date
                resultList.append(objResultList)
    except Exception as e:
        print (e)
        exceptionFile = open(_logFile, "w+")
        exceptionFile.write(str(e))
        exceptionFile.close()
    return resultList


def getMainContent(id, meeting, dobj):
    csv_date = datetime.strftime(dobj, "%d/%m/%Y")
    csv_meeting = meeting
    url = 'https://loveracing.nz/RaceInfo/' + id + '/Meeting-Overview.aspx'
    print ('get data from ' + url)
    try:
        resultList = []
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        race_results = soup.find_all('li', {'class': 'race results'})
        circle_number = race_results.__len__()
        if _MaxRace < race_results.__len__() :
            circle_number = _MaxRace
        for i in range(0, circle_number):
        # for i in range(0, 1):
            subinfo = race_results[i].find_all('td')
            race = subinfo[0].text
            start = subinfo[1].text
            class_dis_price = subinfo[3].text
            item_array = class_dis_price.split('-')
            price = item_array[1]
            class_dist = item_array[0]
            item_array = class_dist.split()
            len = item_array.__len__()
            dist = item_array[len-1]
            clas = ''
            for k in range(0, len - 1) :
                clas = clas + ' ' + item_array[k]
            time=subinfo[4].text
            plc_url = 'https://loveracing.nz/RaceInfo/' + id + '/' + str(i+1) + '/Race-Detail.aspx'
            print (plc_url)
            plc_page = requests.get(plc_url)
            plc_soup = BeautifulSoup(plc_page.content, "html.parser")
            plc_info = plc_soup.find("ul", id="sectionals")
            horse_info = plc_soup.find("ul", {"class" : "horse-list"})
            if plc_info is None :
                continue
            else :
                plc_list = plc_info.find_all('li')
                horse_list = horse_info.find_all('li')
                for j in range(1, plc_list.__len__()):
                # for j in range(1, 2):
                    objResult = TableData()
                    objResult.date = csv_date
                    objResult.meeting = csv_meeting
                    objResult.race = race
                    objResult.start = start
                    objResult.time = time
                    objResult.cla = clas
                    objResult.dis = dist
                    objResult.prise = price
                    objResult.plc = str(j)
                    plc = plc_list[j]
                    horse = horse_list[j]
                    strt_number = horse.find("div", {"class" : "column race-number startnumber"}).text
                    horse_name = horse.find("div", {"class" : "column horse"}).find(text=True)
                    stake = horse.find("div", {"class" : "column odds"}).text
                    objResult.number = strt_number
                    objResult.horse = horse_name
                    objResult.stake = stake
                    objResult.f400 = plc.find_all("div")[0].text
                    objResult.l800 = plc.find_all("div")[1].text
                    objResult.l600 = plc.find_all("div")[2].text
                    objResult.l400 = plc.find_all("div")[3].text
                    objResult.l200 = plc.find_all("div")[4].text
                    resultList.append(objResult)
        return resultList
    except Exception as e:
        print (e)
        exceptionFile = open(_logFile, "a")
        exceptionFile.write(str(e))
        exceptionFile.close()


def main():
    print ('start .....')
    header = ['DATE', 'MEETING', 'RACE', 'START', 'CLASS', 'DIS', 'PRISE', 'PLC', 'NUMBER', 'HORSE', 'STAKE',
              'F400', 'L800', 'L600', 'L400', 'L200', 'TIME']
    results = getResultList()
    for i in range(0, results.__len__()):
        result = results[i]
        datestr = result.date[4:] + ' ' + str(_Year)
        dateobj = datetime.strptime(datestr, '%d %b %Y')
        csvname = result.racecorse + datetime.strftime(dateobj, "%d%m%Y")
        print (csvname + '.csv is creating ...')
        try:
            with open(_OutputCsvPath + "\\" + csvname + '.csv', 'w', newline='') as csvfile:
                outputwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                outputwriter.writerow(header)

                maincontent = getMainContent(str(result.id), result.club, dateobj)
                for j in range(0, maincontent.__len__()):
                    content = maincontent[j]
                    oneRow = []
                    oneRow.append(content.date.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.meeting.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.race.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.start.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.cla.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.dis.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.prise.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.plc.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.number.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.horse.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.stake.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.f400.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.l800.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.l600.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.l400.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.l200.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    oneRow.append(content.time.replace(",", "").replace("\r", "").replace("\n", "").strip())
                    outputwriter.writerow(oneRow)
        except Exception as e:
            print (e)
            exceptionFile = open(_logFile, "a")
            exceptionFile.write(str(e))
            exceptionFile.close()
        print ('One file created!')
    print ('end')


main();
