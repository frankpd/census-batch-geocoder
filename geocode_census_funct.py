#!/usr/bin/env python3
#Geocode addresses using Census Geocoder API
#Frank Donnelly, Geospatial Data Librarian, Baruch College CUNY
#May 8, 2016

#Released under a GNU General Public License as published by the
#Free Software Foundation, WITHOUT ANY WARRANTY
#http://www.gnu.org/licenses/

def census_geocode(datafile,delim,header,start,addcol):
    """ (str,str,str,int,list[int]) -> files
    Datafile is file or path to process, delim is file's
    delimiter, specify if file has header row with y or n,
    specify 0 to read from beginning of file or index # to resume,
    addcol is a list of column numbers containing address components.
"""
    
    import csv, locale, traceback, time, datetime
    from urllib import error
    from censusgeocode import CensusGeocode

    cg=CensusGeocode()

    #Function for adding and summing entries in dictionaries
    def sumdict(theval,thedict):
        if theval in thedict:
            thedict[theval]=thedict[theval]+1
        else:
            thedict[theval]=1
          
    #Open files, set up environments. Match lists are for debugging; results
    #are written to output files as each record is handled. Headers added
    #based on user input. Types of non-matches stored in a dictionary for
    #output to report. Users should verify that input files are in UTF-8 before
    #matching.

    if type(addcol) is not list:
        print('Position numbers with address components must be provided in a list, i.e. [3] or [3,4,5,6]')
        raise SystemExit

    if len(addcol)==1:
        unparsed=addcol[0]-1
    elif len(addcol)==4:
        addstreet=addcol[0]-1
        thecity=addcol[1]-1
        thestate=addcol[2]-1
        thezip=addcol[3]-1
    else:
        print('Inappropriate number of positions given - provide either 1 for unparsed or 4 for parsed')
        raise SystemExit

    if header.lower()=='y' or 'yes' or 'n' or 'no':
        pass
    else:
        print("Must indicate whether there is a header row with 'y' or 'n'")
        raise SystemExit

    matched=[]
    nomatch=[]
    matchfails={}
    counter=0
    namefile=datafile[:-4]
    if datafile[-4:]=='.csv':
        ext='.csv'
    else:
        ext='.txt'

    readfile=csv.reader(open(datafile,'r', encoding='utf-8', errors='ignore'),delimiter=delim)
    matchfile=open(namefile+'_matched'+ext,'a', newline='', encoding='utf-8', errors='ignore')
    matchwrite=csv.writer(matchfile, delimiter=delim, quotechar='"', quoting=csv.QUOTE_MINIMAL)
    nomatchfile=open(namefile+'_nomatch'+ext,'a', newline='', encoding='utf-8', errors='ignore')
    nomatchwrite=csv.writer(nomatchfile, delimiter=delim, quotechar='"', quoting=csv.QUOTE_MINIMAL)

    if header.lower()==('y' or 'yes') and int(start)==0:
        headrow=next(readfile)
        headnomatch=list(headrow)
        headnomatch.append('error')
        nomatchwrite.writerow(headnomatch)
        headmatch=list(headrow)
        newhead=['matched_add','longitude','latitude','ansifips','stateid','countyid','tractid','blkgrpid','blkid',
                 'block','tract','county','state']
        headmatch.extend(newhead)
        matchwrite.writerow(headmatch)

    print('Match process launched...')

    #Start reading the file from the given row number;
    #if there is no result (no match) write record to no match list and output file;
    #if record has matches, take relevant data from the first match,
    #append it to the address and add it to the matched list and output file.
    #Outside try / except handles all errors, breaks off matching and writes report.
    #Inside try / except while true handles server time out, tries to rematch, or
    #if input is bad gives up after 5 times and writes no match. While true breaks
    #if no exception raised, moves on to next record. Internal i in range does rematch
    #if result returns no geography due to java error - by default a status key returns
    #no value if everything is ok, but returns a message value if there's a problem.
    #If there is a status value, tries again up to 3 times before giving up, then writes
    #no match. Otherwise in range loop breaks if a clean no match or match is made,
    #proceeds to next record.

    for index, record in enumerate(readfile):
        try:
            if index < int(start):
                continue
            else:
                error_count=0
                record=[x.strip() for x in record]
                while True:
                    try:
                        for i in range(4):    
                            if len(addcol)==1:
                                result=cg.onelineaddress(record[unparsed])
                            else:
                                result=cg.address(record[addstreet],city=record[thecity],state=record[thestate],zipcode=record[thezip])
                            if len(result)==0:
                                record.append('Match not found')
                                nomatch.append(record)
                                sumdict(record[-1],matchfails)
                                nomatchwrite.writerow(record)
                            else:                
                                geo=result[0].get('geographies')
                                blockinfo=geo.get('2010 Census Blocks')
                                tractinfo=geo.get('Census Tracts')
                                countyinfo=geo.get('Counties')
                                stateinfo=geo.get('States')
                                problemlist=[blockinfo[0].get('status'),tractinfo[0].get('status'),
                                             countyinfo[0].get('status'),stateinfo[0].get('status')]
                                
                                if any(v is not None for v in problemlist):                                              
                                    if i < 3:
                                        print('Trying to return geography at index '+str(index))                                   
                                        time.sleep(1)
                                        continue
                                    else:
                                        print ('Writing a no match for failed geography at index '+str(index))                                    
                                        record.append('Failed to return geography')
                                        nomatch.append(record)
                                        sumdict(record[-1],matchfails)
                                        nomatchwrite.writerow(record)                          
                                else:                  
                                    ansifips=blockinfo[0].get('GEOID')
                                    stateid=ansifips[0:2]
                                    countyid=ansifips[2:5]
                                    tractid=ansifips[5:11]
                                    blkgrpid=ansifips[11]
                                    blkid=ansifips[11:]

                                    blkname=blockinfo[0].get('NAME')                                    
                                    trctname=tractinfo[0].get('NAME')                                    
                                    coname=countyinfo[0].get('NAME')                                    
                                    stname=stateinfo[0].get('NAME')

                                    match=result[0].get('matchedAddress')
                                    coord=result[0].get('coordinates')
                                    lng=str(coord.get('x'))
                                    lat=str(coord.get('y'))

                                    newitems=match,lng,lat,ansifips,stateid,countyid,tractid,blkgrpid,blkid,blkname,trctname,coname,stname

                                    record.extend(newitems)
                                    matched.append(record)
                                    matchwrite.writerow(record)
                            break

                        counter=counter+1
                        time.sleep(1)
                        if counter % 100==0:
                            print(counter,' records processed so far...')
                            print ('Last record written was:')
                            print(record)
                        if counter % 1000==0:
                            time.sleep(5)
                            
                    except error.HTTPError as server_error:
                        if server_error.code==500:
                            error_count=error_count+1
                            if error_count < 5:
                                print('Got a server error, will try again from index '+str(index))
                                time.sleep(2)
                                continue
                            else:
                                print('Writing a no match as server failed to return result at index '+str(index))
                                record.append('Server failed to return result')
                                nomatch.append(record)
                                sumdict(record[-1],matchfails)
                                counter=counter+1
                                nomatchwrite.writerow(record)
                    break
                       
        except Exception as e:
            print('An error has occurred. File stopped at index '+str(index))
            traceback.print_exc()
            break
                
    #Close all files, write match summaries to report
        
    matchfile.close()
    nomatchfile.close()
    nomatch_cnt=len(nomatch)
    matched_cnt=len(matched)

    print(counter, ' records processed in total.')
    print(matched_cnt, ' records matched and ', nomatch_cnt, ' records had no matches.')

    ts=datetime.datetime.now().strftime("%Y_%m_%d_%H%M")

    report=open(namefile+'_report_'+ ts +'.txt','w')
    report.write('Summary of Census Geocoding Output for ' + datafile + ' on ' + ts + '\n' + '\n')
    report.write(str(counter) + ' records processed in total.'+'\n')
    report.write(str(matched_cnt) + ' records matched' +'\n')
    report.write(str(nomatch_cnt) + ' records had no matches' +'\n'+'\n')
    report.write('For the unmatched records, results and errors:'+'\n')
    for k,v in sorted(matchfails.items()):
        report.writelines('\t'+': '.join([k, str(v)])+'\n')
    report.close()   
