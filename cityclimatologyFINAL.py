
import numpy as np
import matplotlib.pyplot as pp
import seaborn


import urllib.request
urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt','stations.txt')


dly_delimiter = [11,4,2,4] + [5,1,1,1] * 31
dly_usecols = [1,2,3] + [4*i for i in range(1,32)]
dly_dtype = [np.int32,np.int32,(np.str_,4)] + [np.int32] * 31
dly_names = ['year','month','obs'] + [str(day) for day in range(1,31+1)]

##--------------------------------------------------------------------------------------

def main():

	stations = {}

	menu()

	for line in open('stations.txt','r'):
    	fields = line.split()
        
    	stations[fields[0]] = ' '.join(fields[4:])

	stationName = askStation()
	findStation(stationName)

	getStationData(stationName)



##--------------------------------------------------------------------------------------
#Gives start menu

def menu():
	while True:
		print("----------------------------------")
		print("(N)ew Station | e(X)it")
		print()
		choice = input("Select a choice and press enter").upper()
		if choice != 'N' or choice != 'X':
			print("Invalid Choice")
		if choice == 'N':
			break
		if choice == 'X':
			exit()


##---------------------------------------
#prompts the user to enter a station

def askStation():
    while True:
    	selectedStation = input("What weather station climate history do you want to look at? | ").upper()
    	if selectedStation == "":
    		print("please enter a station...")
    	if len(selectedStation) > 1:
    		break
    print()
    return selectedStation

##---------------------------------------
#finds the station the user entered in the stations.txt file

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
        if len(found) > 1 or len(found) == 0:
            s = askStation()
        if len(found) == 1:
            break
    
    return found


##---------------------------------------
#proceeds to get the data for the selected station, as well as perform the calculations we will need to do.

def getStationData(selectedStation):
	
	selectedStationLine = findStation(selectedStation)
	selectedStationCode = ""
	for key in selectedStationLine:
    	selectedStationCode = key

	urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/all/' + selectedStationCode + '.dly',selectedStationCode + '.dly')

	citydata = parsefile(selectedStationCode + '.dly')
	unroll(citydata[0])


	city_tmin = getobs(selectedStationCode + '.dly','TMIN')
	city_tmax = getobs(selectedStationCode + '.dly','TMAX')




##---------------------------------------
#parses the data set file we obtain after FTPing noaa for the exact station, giving us the columns we want to look at


def parsefile(filename):
    return np.genfromtxt(filename,
                         delimiter = dly_delimiter,
                         usecols = dly_usecols,
                         dtype = dly_dtype,
                         names = dly_names)

#----------------------------------------

#----------------------------------------
#re-aligns the matrix so that each row is the year with the following data values in that row

def unroll(record):
    startdate = np.datetime64('{}-{:02}'.format(record['year'],record['month']))
    dates = np.arange(startdate,startdate + np.timedelta64(1,'M'),np.timedelta64(1,'D'))
    
    rows = [(date,record[str(i+1)]/10) for i,date in enumerate(dates)]
    
    return np.array(rows,dtype=[('date','M8[D]'),('value','d')])

#----------------------------------------

def graphData():


#----------------------------------------
#fills all the NaN values in our data set

def fillnans(data):
    dates_float = data['date'].astype(np.float64)
    
    nan = np.isnan(data['value'])
    
    data['value'][nan] = np.interp(dates_float[nan],dates_float[~nan],data['value'][~nan])


#----------------------------------------
#takes the data from the rows we want and puts it into a matrix

def getobs(filename,obs):
    data = np.concatenate([unroll(row) for row in parsefile(filename) if row[2] == obs])
    
    data['value'][data['value'] == -999.9] = np.nan
    
    return data



#----------------------------------------


#----------------------------------------
