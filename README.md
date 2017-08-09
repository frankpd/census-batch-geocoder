# census-batch-geocoder
Uses the censusgecode wrapper and the Census Bureau's API to batch geocode text files of US addresses

Frank Donnelly, Geospatial Data Librarian, Baruch CUNY
francis.donnelly@baruch.cuny.edu

May 8, 2016

# INTRODUCTION

This Python 3 script relies on the 3rd party module CensusGeocode at https://pypi.python.org/pypi/censusgeocode as well as several internal Python modules to geocode a plain text file of parsed or unparsed US addresses using the Census Bureau's geocoding API, at http://geocoding.geo.census.gov/geocoder. The output file will contain: all of the fields from the input file, the address that was retrieved based on the input address, longitude and latitude coordinates in the NAD83 coordinate system, and 2010 census geography codes and names for the area in which the address is located. Addresses that are not matched are written to a separate file, and a summary report with a count of the results is also generated.

# LICENSE

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.

# SETUP

To use the script you need to install a recent version of Python 3.x from https://www.python.org/.

During the installation process for Windows, make sure you check the box to add Python to your environment variables.

You also need to download and setup the CensusGeocode module from https://github.com/fitnr/censusgeocode. The module doesn't use PIP or other Python installers, so you'll need to download and unzip the file, and then run the setup program to register it with your Python installation. The steps will vary based on your operating system. For Windows users:

1. Download the CensusGeocode module, place it in your Python scripts folder and unzip it.

2. Open the command prompt, move to the top of the directory tree and then move down into the folder where you unzipped the module.

3. Type: python setup.py install. This will print output to the screen and install the module. If this fails try typing python3 or py -3 instead of just python. Once again, this varies based on how python was installed on your system. You also need to insure you're using Python 3.x and not 2.x

For Mac and Linux users this is typically simpler, as Python is usually installed and can be launched from the shell by default (just verify that you have version 3.x).

# USAGE

For simplicity, you may want to store the script geocode_census_funct.py in the same folder as the data file that you're going to process, so you can simply provide the file name to the geocoding function. If you store the script in a different folder, you will need to provide the full path to the data file. All of the output files (matched addresses, non-matched addresses, and summary report) will be written to the same folder where the script is stored. Your data file must be a plain, delimited text file (txt, csv).

The script is written as a function and can be launched from the command line / shell or from IDLE (Python's IDE for writing and running scripts). 

Launch IDLE. When the IDLE shell opens, go to File and Open, and select the script geocode_census_funct.py. It will open in a separate script / editing window. Go to Run - Run Module; that will load the program into memory. Now you can type the actual function back in the Python shell to run the script:

census_geocode(datafile,delim,header,start,addcol)
(str,str,str,int,list[int]) -> files

The first three parameters are strings, and must be surrounded by single quotes. The fourth parameter is an integer number, and the fifth is a list of integers surrounded in brackets. The parameters are:

* datafile - this is the name of the file you want to process (file name and extension). If you place the geocode_census_funct.py file in the same directory as your data file, then you just need to provide the name of the file. Otherwise, you would need to type the full path to the file.

* delim - this is the delimiter or character that separates the values in your data file. Common delimiters includes commas ',', tabs '\t', and pipes '|'.

* header - here you specify whether your file has a header row, i.e. column names. Enter 'y' or 'yes' if it does, 'n' or 'no' if it doesn't.

* start - type 0 to specify that you want to start reading the file from the beginning. If you were previously running the script and it broke and exited for some reason, it provides an index number where it stopped reading; if that's the case you can provide that index number here, to pick up where you left off.

* addcol - provide a list that indicates the number of the columns that contain the address components in your data file. For an unparsed address, you'll provide just one position number. For a parsed address, you'll provide 4 positions: address, city, state, and ZIP code. Whether you provide 1 or 4, the numbers must be supplied in brackets, as the function requires a Python list.

# EXAMPLES

A tab-delimited, unparsed address file with a header that's stored in the same folder as the script. Start from the beginning and the address is in the 2nd column:

census_geocode('my_addresses.txt','\t','y',0,[2])

A comma-delimited, parsed address file with no header that's stored in the same folder as the script. Start from the beginning and the addresses are in the 2nd through 5th columns:

census_geocode('addresses_to_match.csv',',','n',0,[2,3,4,5])

A comma-delimited, unparsed address file with a header that's not in the same folder as the script. We ran the file before and it stopped at index 250, so restart there - the address is in the 3rd column:

census_geocode('C:\address_data\data1.csv',',','y',250,[3])

# OUTPUT

As the script runs it will provide an update for every 100 records it processes, along with a sample of the last record processed. If it encounters a problem it will also print a message as it tries again; if it fails after a number of attempts it will write the record to the non-matched file. If some unforeseen error occurs, the matching process will end and it will print the index of the record where it stopped. The input and output files will be closed and a summary report will be written. Since each record is written after a match result is received, all progress will be saved if the script exits cleanly. You can re-run the script and provide the index number to the function, to resume where it stopped - it will append records to the output files it previously created.

The Census Bureau's API is strict, so it will either return a good match or it will return nothing; for example if it can't find the street address it won't return ZIP Code or municipal centroids instead. You can compare your input address with the returned matched address to check for inconsistencies. The longitude and latitude coordinates are in NAD 83 (EPSG code 4269). The full ANSI / FIPS code for the census block is returned, as are the component codes: state, county, tract, block group, and block. Names for the tract, county, and state are also returned.

Unmatched addresses are written to a separate file with an error message. There are three possible errors:

1. Match not found - the Census API took the input address and could not find a match, an empty result was returned.

2. Failed to return geography - the Census API took the input address and found a match, but because of an internal error could not retrieve the census geography.

3. Server failed to return result - the Census API wasn't able to take the input address; either the server timed out or the input was invalid and couldn't be parsed.

Problem 1 can only be resolved by correcting the address or obtaining a new one. Problem 2 can usually be solved by attempting a rematch.  Problem 3 could be solved by trying a rematch (if the server simply timed out), but may require correcting the address (if the API wasn't able to parse it).

# NOTES

* Your output is only going to be as good as your input. Clean and standardize your addresses as much as possible before attempting to do a match. There's no use wasting time in providing incomplete addresses or PO Box numbers to the script - you won't get a match.

* This script uses Python's CSV module, and recognizes quoted characters in input and output. If you have a comma-delimited file and your data has commas embedded in certain values, the script will escape them properly. For example "500 W Main St, Apt 3A" would be recognized as one column (the address) and would not be split into two. If you have embedded commas in your data without quoted fields, the records will be parsed incorrectly and the match will fail.

* When the script writes output, it will create output files if they don't exist, but will append to them if they already exist. This is nice if the script gets interrupted so you can pick up where you left off - but be careful. If you accidentally re-run the process on the same file, you'll be writing duplicate records to the output files.

* Input files should be saved with UTF-8 encoding to insure that the script can interpret the files correctly.

* The script pauses for 1 second after every record, and again for 5 seconds after every 1,000 records. It also pauses for a second or two before attempting a rematch if there's some kind of problem. This was done to minimize the load on the Census Bureau's servers. Do the math, and you'll find you can do about 80k records in 24 hours.

* It may be wise to break your data up into several files if you have a lot of matching to do.
