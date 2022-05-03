import csv, json, math, pytz, datetime, timezonefinder, re

tf = timezonefinder.TimezoneFinder()

birdJson = {}
timeCodes = {}
errors = {'keyError':[], 'valueError':[]}
progress = 0

start_date = datetime.date(2021, 1, 1) 
end_date = datetime.date(2021, 1, 31)
delta = end_date - start_date


for date in range(delta.days + 1):
	for hour in range(24):
		day = start_date + datetime.timedelta(days=date)
		time = str(hour).rjust(2,'0')+':00'
		timeStamp = f'{day} {time}'
		birdJson[timeStamp] = []

with open('nzBirdData.txt','r',encoding='utf-8-sig') as testFile:
	testDataSource = csv.DictReader(testFile,delimiter='\t')
	testData = list(testDataSource)
	dataLength = len(testData)
	with open('taxonomy.csv','r',encoding='utf-8-sig') as taxonomyFile:
		taxonomyData = csv.DictReader(taxonomyFile)
		taxonOrder = {}
		for row in taxonomyData:
			taxonOrder[row['TAXON_ORDER']] = row['ORDER1']
		
		for row in testData:
			progress += 1
			print(f'{progress}/{dataLength} ({int(progress/dataLength*100)}%)')

			try:
				lat = float(row['LATITUDE'])
				lng = float(row['LONGITUDE'])

				obvsDate = row['OBSERVATION DATE']
				obsvTime = row['TIME OBSERVATIONS STARTED']

				if row['STATE CODE'] not in timeCodes:
					timezone_str = tf.certain_timezone_at(lat=lat, lng=lng)
					timezone_add = pytz.timezone(timezone_str)
					timeCodes[row['STATE CODE']] = timezone_add

				timezone = timeCodes[row['STATE CODE']]
				obsvLOC = datetime.datetime.strptime(f'{obvsDate} {obsvTime}','%Y-%m-%d %H:%M:%S')
				obsvUTC = timezone.localize(obsvLOC).astimezone(pytz.UTC)

				timeFormat = re.split(":", str(obsvUTC))
				obsvFormat = timeFormat[0]+':00'

				if row['OBSERVATION COUNT'] != 'X':
					birdData = {'Species': row['SCIENTIFIC NAME'],
								'Order': taxonOrder[row['TAXONOMIC ORDER']],
								'Count': math.log(int(row['OBSERVATION COUNT'])),
								'Latitude': lat,
								'Longitude': lng,
								'Duration': row['DURATION MINUTES'],
								'Delay': timeFormat[1]
								}
					birdJson[obsvFormat].append(birdData)
			except KeyError as e:
				errors['keyError'].append(str(e))
				pass
			except ValueError as e:
				errors['valueError'].append(str(e))
				pass

with open("nzBirdErrors.json",'w') as out:
	json.dump(errors,out,indent=2)

with open("nzBirdTest.json",'w') as out:
	json.dump(birdJson,out,indent=2)

