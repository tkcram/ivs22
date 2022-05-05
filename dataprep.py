import csv, json, math, pytz, datetime, timezonefinder, re

tf = timezonefinder.TimezoneFinder()

birdJson = {}
timeCodes = {}
birdOrders = []
errors = {'keyError':[], 'valueError':[], 'indexError':[]}
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

				order = taxonOrder[row['TAXONOMIC ORDER']]

				obsDate = row['OBSERVATION DATE']
				obsTime = row['TIME OBSERVATIONS STARTED']

				# if row['STATE CODE'] not in timeCodes:
				# 	timezone_str = tf.certain_timezone_at(lat=lat, lng=lng)
				# 	timezone_add = pytz.timezone(timezone_str)
				# 	timeCodes[row['STATE CODE']] = timezone_add

				# timezone = timeCodes[row['STATE CODE']]
				# obsLOC = datetime.datetime.strptime(f'{obvsDate} {obsTime}','%Y-%m-%d %H:%M:%S')
				# obsUTC = timezone.localize(obsLOC).astimezone(pytz.UTC)

				obsUTC = f'{obsDate} {obsTime}'
				timeFormat = re.split(":", str(obsUTC))
				obsFormat = timeFormat[0]+':00'

				if row['OBSERVATION COUNT'] != 'X':
					birdData = {'ScientificName': row['SCIENTIFIC NAME'],
								'CommonName': row['COMMON NAME'],
								'Order': order,
								'Count': int(row['OBSERVATION COUNT']),
								'Latitude': lat,
								'Longitude': lng,
								'Duration': row['DURATION MINUTES'],
								'Delay': timeFormat[1]
								}

					birdJson[obsFormat].append(birdData)

					if order not in birdOrders:
						birdOrders.append(order)

			except KeyError as e:
				errors['keyError'].append(str(e))
				pass
			except ValueError as e:
				errors['valueError'].append(str(e))
				pass
			except IndexError as e:
				errors['indexError'].append(str(e))
				pass

# print(birdOrders)
# with open('nzBirdTest.json','r',encoding='utf-8-sig') as nzFile:
# 	with open('ausBirdTest.json','r',encoding='utf-8-sig') as ausFile:
# 		nzData = json.load(nzFile)
# 		ausData = json.load(ausFile)

# 		for timeStamp in nzData:
# 			nzData[timeStamp].extend(ausData[timeStamp])

		# with open("anzacBirdTest.json",'w') as out:
		# 	json.dump(nzData,out,indent=2)

with open("nzBirdErrors.json",'w') as out:
	json.dump(errors,out,indent=2)

with open("nzBirdTest.json",'w') as out:
	json.dump(birdJson,out,indent=2)


