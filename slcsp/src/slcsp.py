import csv
import itertools
from operator import itemgetter
from collections import OrderedDict

def run():
    #extract zipcodes from slcsp.csv
    with open('slcsp.csv', newline='') as slcspfile:
        slcspreader = csv.DictReader(slcspfile)
        zipcodes = [row['zipcode'].replace(",", "") for row in slcspreader]
    slcspfile.close()
    #extract corresponding rate areas for relevant zipcodes from zips.csv
    with open('zips.csv') as zipfile:
        zipreader = csv.DictReader(zipfile)
        zip_rates = [[row['zipcode'],row['rate_area']] for row in zipreader for zipcode in zipcodes if row['zipcode'] == zipcode]
    #extract all rates for relevant rate areas that are Silver metal level
    with open('plans.csv') as planfile:
        planreader = csv.DictReader(planfile)
        rates = []
        for row in planreader:
            for n, (i, s) in enumerate(zip_rates):
                if row['rate_area'] == s and row['metal_level'] == "Silver":
                    if [row['rate_area'],row['rate']] not in rates:
                        rates.append([row['rate_area'],row['rate']])
        rates = sorted(rates, key = itemgetter(0, 1))
    #organize and sort rate areas and corresponding rates
    concatenated_by_rate_area = []
    nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
            '12', '13', '14', '15', '16', '17', '18', '19']
    for val in nums:
        result = [(i,s) for n, (i, s) in enumerate(rates) if i == val]
        concatenated_by_rate_area.append(list(itertools.chain.from_iterable(result)))
    nested = [[x] for x in concatenated_by_rate_area]
    #extract second lowest cost rates
    slcsps = [x[3] for idx, item in enumerate(nested) for x in nested[idx] if idx not in [13, 16, 17]]
    #account for areas with no rate that matches the criteria so we can use enumerate() later
    slcsps.insert(13, '')
    slcsps.insert(16, '')
    slcsps.insert(17, '')
    slcsps.extend(('', '', '', '', '', '', '', '', '', '', ''))
    #write slcsp rates to csv file, avoiding writing the same information twice
    with open('slcsp.csv', 'w', newline='') as slcspfile:
        slcspfile.write('zipcode,rate\n')
        seen = set()
        for zipcode in zipcodes:
            for index, (zipcd, rate_area) in enumerate(zip_rates):
                if zipcd == zipcode:
                    if slcsps[int(rate_area)-1]:
                        slcsp = slcsps[int(rate_area)-1]
                    else:
                        slcsp = ''
                    line = zipcd + ',' + slcsp + '\n'
                    if line in seen:
                        continue
                    else:
                        seen.add(line)
                        slcspfile.write(line)
    slcspfile.close()
    #detect which zipcodes have multiple rates
    with open('slcsp.csv', newline='') as slcspfile:
        seen = set()
        slcspreader = csv.DictReader(slcspfile)
        duplicates = set(row['zipcode'] + ',' for row in slcspreader if row['zipcode'] in seen or seen.add(row['zipcode']))
    slcspfile.close()
    #make a dictionary whose keys are zipcodes and values are rates
    with open('slcsp.csv', newline='') as slcspfile:
        d = OrderedDict()
        slcspreader = csv.DictReader(slcspfile)
        for row in slcspreader:
            d[row['zipcode'] + ',']=row['rate']
    #keys who had multiple rates should be blank
    for key, value in d.items():
        for item in list(duplicates):
            if key == item:
                d[key] = ''
    slcspfile.close()
    #rewrite to slcsp.csv from the dictionary
    with open('slcsp.csv', 'w', newline='') as slcspfile:
        slcspfile.write('zipcode,rate\n')
        for key, value in d.items():
            line = key + value + '\n'
            slcspfile.write(line)
    slcspfile.close()

if __name__ == '__main__':
    run()
