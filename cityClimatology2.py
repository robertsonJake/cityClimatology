

import numpy as np
import matplotlib.pyplot as pp
import seaborn


import urllib.request
urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt','stations.txt')


stations = {}

for line in open('stations.txt','r'):
     fields = line.split()
        
     stations[fields[0]] = ' '.join(fields[4:])
len(stations)

def findStation(s):
    while True:
        found = {code: name for code,name in stations.items() if s in name}
        if len(found)>1:
            print("Your search returned too many results")
            print("Please type in one of these, be specific")
            print()
        print("These are the airports that matched your search:")
        print("------------------------------------------------")
        for index in found:
            print(index,found[index])
        print("------------------------------------------------")
        print()
        if len(found) > 1:
            s = askStation()
        if len(found) == 1:
            break
    
    return found


def parsefile(filename):
    return np.genfromtxt(filename,
                         delimiter = dly_delimiter,
                         usecols = dly_usecols,
                         dtype = dly_dtype,
                         names = dly_names)

dly_delimiter = [11,4,2,4] + [5,1,1,1] * 31
dly_usecols = [1,2,3] + [4*i for i in range(1,32)]
dly_dtype = [np.int32,np.int32,(np.str_,4)] + [np.int32] * 31
dly_names = ['year','month','obs'] + [str(day) for day in range(1,31+1)]


def askStation():
    selectedStation = input("What weather station climate history do you want to look at? | ").upper()
    print()
    return selectedStation


selectedStation = ""
while selectedStation == "":
    selectedStation = askStation()
    if selectedStation == "":
        print("Please type in a station...")



##selectedStationCode = findStation(selectedStation)
##while selectedStation == "" or len(selectedStationCode) > 12:
##    askStation()
##    selectedStationCode = findStation(selectedStation)


selectedStation

selectedStationLine = findStation(selectedStation)


selectedStationCode = ""
for key in selectedStationLine:
    selectedStationCode = key
print(selectedStationCode)


urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/' + selectedStationCode + '.dly',selectedStationCode + '.dly')


citydata = parsefile(selectedStationCode + '.dly')


citydata

def unroll(record):
    startdate = np.datetime64('{}-{:02}'.format(record['year'],record['month']))
    dates = np.arange(startdate,startdate + np.timedelta64(1,'M'),np.timedelta64(1,'D'))
    
    rows = [(date,record[str(i+1)]/10) for i,date in enumerate(dates)]
    
    return np.array(rows,dtype=[('date','M8[D]'),('value','d')])


unroll(citydata[0])
citydata

def getobs(filename,obs):
    data = np.concatenate([unroll(row) for row in parsefile(filename) if row[2] == obs])
    
    data['value'][data['value'] == -999.9] = np.nan
    
    return data



city_tmin = getobs(selectedStationCode + '.dly','TMIN')
city_tmax = getobs(selectedStationCode + '.dly','TMAX')


pp.plot(city_tmax['date'],city_tmax['value'])
pp.plot(city_tmin['date'],city_tmin['value'])


def fillnans(data):
    dates_float = data['date'].astype(np.float64)
    
    nan = np.isnan(data['value'])
    
    data['value'][nan] = np.interp(dates_float[nan],dates_float[~nan],data['value'][~nan])



fillnans(city_tmin)
fillnans(city_tmax)


np.mean(city_tmin['value']), np.mean(city_tmax['value'])


pp.plot(city_tmax['date'],city_tmax['value'])
pp.plot(city_tmin['date'],city_tmin['value'])



def plot_smoothed(t,win=10):
    smoothed = np.correlate(t['value'],np.ones(win)/win,'same')
    
    pp.plot(t['date'],smoothed)


def selectyear(data,year):
    start = np.datetime64('{}'.format(year))
    end = start + np.timedelta64(1,'Y')
    
    return data[(data['date'] >= start) & (data['date'] < end)]['value']


pp.figure(figsize=(20,10))

plot_smoothed(getobs(selectedStationCode + '.dly','TMAX'),365)
plot_smoothed(getobs(selectedStationCode + '.dly','TMIN'),365)

#NEED TO GET THE FUNCTION TO RETURN WHATEVER CITY IS INPUTTED'S MINIMUM YEAR FOR VALUES
pp.title(selectedStation + " Weather Station ")
pp.axis(xmin=np.datetime64('1952'),xmax=np.datetime64('2012'),ymin=-10,ymax=30)



def selectyear(data,year):
    start = np.datetime64('{}'.format(year))
    end = start + np.timedelta64(1,'Y')
    
    return data[(data['date'] >= start) & (data['date'] < end)]['value']


selectyear(city_tmax,1959).shape
[selectyear(city_tmax,year).shape[:365] for year in range(1959,2015+1)]



city_tmax


years = np.arange(1959,2015+1)
city_tmax_all = np.vstack([selectyear(city_tmax,year)[:365] for year in range(1959,2015+1)])
city_tmin_all = np.vstack([selectyear(city_tmin,year)[:365] for year in range(1959,2015+1)])


city_tmax_all.shape


city_tmin_recordmin = np.min(city_tmin_all,axis=0)
city_tmin_recordmax = np.max(city_tmin_all,axis=0)
city_tmax_recordmin = np.min(city_tmax_all,axis=0)
city_tmax_recordmax = np.max(city_tmax_all,axis=0)

city_mean_maxes = np.mean(city_tmax_all,axis=1)
city_mean_mins = np.mean(city_tmin_all,axis=1)


city_warmest_recordWarm = years[np.argmax(city_mean_maxes)]
city_coldest_recordWarm = years[np.argmin(city_mean_maxes)]
city_warmest_recordLow = years[np.argmax(city_mean_mins)]
city_coldest_recordLow = years[np.argmin(city_mean_mins)]




pp.figure(figsize=(20,10))
pp.plot(years,city_mean_maxes,color='r')
pp.title(selectedStation + ' Mean Maximum Temperatures Across Time')
pp.ylabel('Mean Degrees C')
pp.xlabel('Year')


#

pp.figure(figsize = (20,10))
days = np.arange(1,365 + 1)
pp.fill_between(days,np.min(city_tmax_all,axis=0),np.max(city_tmax_all,axis=0),color='r', alpha=0.2)
pp.plot(selectyear(city_tmax,2012),color='r')
pp.fill_between(days,np.min(city_tmin_all,axis=0),np.max(city_tmin_all,axis=0),color='b',alpha=0.2)
pp.plot(selectyear(city_tmin,2012),color='b')
pp.axis(xmax=365)
pp.title("Mean Highs and Lows for Record Hottest Year of " + selectedStation + " Weather Station")
pp.xlabel("Days since January 1st")
pp.ylabel("Mean Degrees C")
pp.savefig(selectedStation)





#



