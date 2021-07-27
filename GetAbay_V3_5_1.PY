from helium import *
from time import sleep
import datetime
from random import randint
import random
import time
#import os   # to kill chrome if killbrowser not work
import pandas as pd
import concurrent.futures
import sys # for progress bar (sys.stdout)
import re # for replace pattern
import sys # for progress bar (sys.stdout)


# use helium instead of Request due to block

flts=[]
pattern = (r',2%20items%20x%20|-Embraer%20|000,|%20|\%7C|,|---|--')

# pattern = (r'%20|\%7C|,E-|,Z1_ECO-|,ECONOMYSAVER-|,R-|,T-|,7kg-|,10kg-|,10kg-|,14kg-|2-items-x-9kg-|Embraer-|,A1_ECO-|,E1_ECO-|,J1_ECO-|,T1_ECO-|,M-|,P-|,S-|,L-|,K-|--')

f_saved = 'D:/THANGNM/AbayScrp/abay_data/flt_tbl_'+ str(datetime.datetime.today().strftime('%x%X')).replace('/','').replace(':','') + '.xlsx'

def midString(string, pref,suff):                           # to remove a string after last char find in string
    return string[(string.find(pref)+len(pref)):(string.rfind(suff))]
def getInfo(url):
        try:
            kill_browser()
            sleep(0.2)
        except Exception:
            pass
        start_chrome(url, headless = True)
        sleep(1)
    # flts find all wweb element and then loop 3rd to get flts inf
        fLgs = find_all(S('.airlogo'))
        fTbl = find_all(S('.linkViewFlightDetail'))
        sleep(1)
        for i in range (0,len(fTbl)):
            flt = {
                    'crr' : fLgs[i].web_element.get_attribute('alt'),
                    'fInf' : fTbl[i].web_element.get_attribute('giatri')
                }
            flts.append(flt)
        kill_browser()      # force to kill browser if webdriver quite or kill browser not work
        sleep(randint(1,5))

# generate URL list 

df_sect = pd.read_excel('D:/THANGNM/AbayScrp/Scan_Sect.xlsx', sheet_name = 1)
sect_Li_o = df_sect['Sect'].tolist()
sect_Li = [x for x in sect_Li_o if str(x) != 'nan']              # to avoid none value

Urls = []
def UrlsList(t0,t1):
    t_d = datetime.datetime.today()
    for i in range(t0,t1):
        dt_nml = t_d + datetime.timedelta(days=i)
        dt_str = dt_nml.strftime('%d')+'/'+ dt_nml.strftime('%m')+'/'+dt_nml.strftime('%Y')
        
        for sect in sect_Li:
            ur_l = 'https://www.abay.vn/_Web/ResultDom/ResultDom.aspx?input='+ sect + '-1-0-0-' + dt_str + '-' + dt_str   # Url to get  2way sectors from abay websit
            Urls.append(ur_l)
    return Urls

# Start crawling from here
urlsLi = UrlsList(1,30)
prgrss_cnt = 0 # use to count progress
size_Crwl = len(urlsLi)
sys.stdout.write("\033[1;31m") #"All following prints will be red ..."

for ul in urlsLi:
    try:
       getInfo(ul)
    except Exception:
        continue 
    prgrss_cnt +=1              # for progress monitor 
    prgrss_bar = str(int(prgrss_cnt*100/size_Crwl)) +'%'
    sys.stdout.write('\033[2K\033[1G') # Clear to the end of line
    sys.stdout.write(prgrss_bar); sys.stdout.flush();  # print a small number of progress bar
    sleep(0.01)

sys.stdout.write("]\n")         # this ends the progress bar

df = pd.DataFrame(flts)         # to transform Data frame for columns


try:                            # to split row to col
    #df['crr'] = [str(itm)[46:48] for itm in df['crr']]
    df['fInf'] = [re.sub(pattern,'-',midString(str(itm),'fi=','-Seat')).replace('--','-') for itm in df['fInf']]
    df['fInf'] = [str(itm)[:(str(itm).rfind('-'))] for itm in df['fInf']]
    df[['from', 'to', 'doo', 'std0', 'fltNo', 'std', 'sta', 'h_bag', 'lugg', 'price', 'fareType', 'config']] = df['fInf'].str.split('-', n=12, expand = True) # New DF with Split Conlum Flight Infor into three other named cols 
    df.drop(columns=['fInf','std0'], inplace=True)
except Exception:
    pass # or you could use 'continue' (use in for loop)

df.to_excel(f_saved, index=False)
print(time.process_time())