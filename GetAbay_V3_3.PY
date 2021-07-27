
from requests.sessions import session
from requests_html import HTMLSession
from random import randint
from time import sleep
import time
import datetime
import pandas as pd
import re # for replace pattern
import concurrent.futures
import sys # for progress bar (sys.stdout)
import atexit

# scrap abay use Request session then render

pattern = (r',2%20items%20x%20|-Embraer%20|000,|%20|\%7C|,|---|--')


#pattern = (r'%20|\%7C|,E-|,Z1_ECO-|,ECONOMYSAVER-|,R-|,T-|,7kg-|,10kg-|,10kg-|,14kg-|2-items-x-9kg-|Embraer-|,A1_ECO-|,E1_ECO-|,J1_ECO-|,T1_ECO-|,M-|,P-|,S-|,L-|,K-|--')

f_saved = 'D:/THANGNM/AbayScrp/abay_data/flt_tbl_'+ str(datetime.datetime.today().strftime('%x%X')).replace('/','').replace(':','') + '.xlsx'

def midString(string, pref,suff):               # to remove a string after last char find in string
    return string[(string.find(pref)+len(pref)):(string.rfind(suff))]

df_sect = pd.read_excel('D:/THANGNM/AbayScrp/Scan_Sect.xlsx', sheet_name = 1)
sect_Li_o = df_sect['Sect'].tolist()
sect_Li = [x for x in sect_Li_o if str(x) != 'nan']

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

flts=[]


for url in urlsLi:
    session = HTMLSession()
    try:
        r = session.get(url)
        r.html.render(sleep=1, keep_page = True, scrolldown=1, timeout = 20)
        sleep(randint(1,5))

        flGs = r.html.find('.airlogo')
        fTbl = r.html.find('.linkViewFlightDetail')

        for i in range (0,len(fTbl)):               # fTbl size bcs sometime only 1 flights selll like Covid
            fInf = re.sub(pattern,'-',midString(str(fTbl[i]),'fi=','-Seat')).replace('--','-')
            flt = {
                'crr' : str(flGs[i])[46:48],
                #'fInf' : rAfter(re.sub(pattern,'-',str(fTbl[i])[69:])   #.replace(' ','-')
                'fInf' : fInf[:(fInf.rfind('-'))]
            }
            flts.append(flt)
        sleep(0.2)
        session.close()    
    except Exception:
        continue


    prgrss_cnt +=1
    prgrss_bar = str(int(prgrss_cnt*100/size_Crwl)) +'%'
    #your loop's complicated code here
    sys.stdout.write('\033[2K\033[1G') # Clear to the end of line
    sys.stdout.write(prgrss_bar); sys.stdout.flush();  # print a small number of progress bar
    sleep(0.01)

sys.stdout.write("]\n") # this ends the progress bar



df = pd.DataFrame(flts)


try:
    df[['from', 'to', 'doo', 'std0', 'fltNo', 'std', 'sta', 'h_bag', 'lugg', 'price', 'fareType', 'config'
]] = df['fInf'].str.split('-', n=12, expand = True) # New DF with Split Conlum Flight Infor into three other named cols 
    df.drop(columns=['fInf'], inplace=True)
except Exception:
    pass # or you could use 'continue'

#print(df)

df.to_excel(f_saved, index=False)

print(time.process_time())
