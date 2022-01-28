import zipfile
import os
import glob
from datetime import datetime
import shutil

import pandas as pd
import numpy as np
from time import sleep

def scheck(series,count): #Series 인자로 받은 후 이상치값 분석, return 값보다 작으면 이상치
	if count==0:
		return 0	   
	anum=int(count/4)
	bnum=anum*3
	print(anum,' ',bnum)
	valuech=series[bnum]-series[anum]
	print(series)    
	value=series[anum]-(2*valuech)

	return value

def bcheck(series,count): #Series 인자로 받은 후 이상치값 분석, return 값보다 크면 이상치
	if count==0:
		return 0	   
	anum=int(count/4)
	bnum=anum*3
	valuech=series[bnum]-series[anum]
	value=series[bnum]+(2*valuech)

	return value	 	  

def printall(ertype,mid,day,num,tfile) :
	if ertype==1 :
		tfile.write(mid+'미터의 '+day+' 날짜의 데이터 갯수는 '+num+' 개 입니다.\n')
		tfile.write('갯수가 정상 범위가 아니므로 확인이 필요합니다.\n')
		tfile.write('----------------------------------------------------------------------\n\n')	   
	elif ertype==2 :
		tfile.write(mid+' 의 '+day+' 날짜에 숫자가 아닌 데이터가 있습니다.\n')
		tfile.write('----------------------------------------------------------------------\n\n')	
	elif ertype==3 :	
		tfile.write(mid+' 의 '+day+' 날짜의 데이터값이 이상합니다. 확인이 필요합니다.\n')
		tfile.write('----------------------------------------------------------------------\n\n')	   
	elif ertype==4 :
		tfile.write(mid+' 의 '+day+' 날짜에 MTime값이 상이한 데이터가 있습니다.\n')
		tfile.write('----------------------------------------------------------------------\n\n')	

def elp(fname,tfile): #E타입 LP검침
	data=pd.read_csv(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	data2=data[[" LTE SysT"," Meter ID"," MTime"," FAP"," WC"]]
	data2.rename(columns={' FAP':'FEP'},inplace=True) #이하 처리를 위한 행제목 변경
	data2.rename(columns={' WC':'WC'},inplace=True)
	data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
	data2.rename(columns={' MTime':'CTime'},inplace=True)
	data2['FEP']=pd.to_numeric(data2['FEP'],errors='coerce')
	   
	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	   
	for i in range(0,data6.MeterID.count()):
		data8=data2[(data2.MeterID==data6.MeterID[i])]
		data8=data8.sort_values(by='FEP',ascending=True)
		data8=data8.reset_index(drop=True)
		o=data8.FEP.count()
		svalue=scheck(data8.FEP.values,o)
		bvalue=bcheck(data8.FEP.values,o)
		print(svalue)		   
		print(bvalue)		   
		kk=bvalue-svalue
		if(bvalue==0 & svalue==0):
			kk=-1			
		sleep(0.1) #제대로 작동안하는듯하다	   
		for j in range(0,data7.CTime.count()):		
			data8=data2[(data2.MeterID==data6.MeterID[i])]
			data8=data8.sort_values(by='FEP',ascending=True)
			data8=data8.reset_index(drop=True)		 	
			data8=data2[(data2.MeterID==data6.MeterID[i])] # 아래의 경우 2*o로 사용가능
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]
			data8=data8.drop_duplicates('CTime',keep='first') # 시간 중복데이터 제거 	 
			k=data8.FEP.count() # 하루치 LP갯수
			data8['FEP']=pd.to_numeric(data8['FEP'],errors='coerce') #쓰레기값 여부 확인을 위해 datatype 변경
			data8['WC']=pd.to_numeric(data8['WC'],errors='coerce')   
				# print(data8) #데이터 맞게 가지고 있음 
			if k!=96: #일일 LP 개수가 정상이 아닐경우 체크
				if k!=0:
					printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			check=data8['FEP'].isnull().sum()+data8['WC'].isnull().sum()
			if check>0:
				printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)				
			else:	
				if kk==-1 :
					data10=data8[data8['FEP']>2000000]
				else :		   
					data10=data8[data8['FEP']>bvalue]
					data10=data10+data8[data8['FEP']<svalue]	 
					data10=data10+data8[data8['FEP']>2000000] #FEP의 쓰레기값 조건 범위 확인
					data10=data10+data8[data8['FEP']<0] #FEP의 쓰레기값 조건 범위 확인
					data10=data10+data8[data8['WC']>1]
					data10=data10+data8[data8['WC']<0]		 		
				if data10.empty==False: #하나라도 쓰레기값 범위인 경우
					printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile)	

def glp(fname,tfile): #G,AE,S타입 LP검침
	data=pd.read_csv(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	data2=data[[" LTE SysT"," Meter ID"," CTime"," FAP"," LARAP"," LERAP"," AP"]]
	data2.rename(columns={' FAP':'FEP'},inplace=True) #이하 처리를 위한 행제목 변경
	data2.rename(columns={' LARAP':'LARAP'},inplace=True)
	data2.rename(columns={' LERAP':'LERAP'},inplace=True)
	data2.rename(columns={' AP':'AP'},inplace=True)
	data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
	data2.rename(columns={' CTime':'CTime'},inplace=True)
	data2['FEP']=pd.to_numeric(data2['FEP'],errors='coerce')
	#print(data2['FEP'].quantile(0.5),'FEP')
	   
	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	   
	for i in range(0,data6.MeterID.count()):
		print('')
		data8=data2[(data2.MeterID==data6.MeterID[i])]
		data8=data8.sort_values(by='FEP',ascending=True)
		data8=data8.reset_index(drop=True)
		o=data8.FEP.count()		
		svalue=scheck(data8.FEP.values,o)
		bvalue=bcheck(data8.FEP.values,o)
		print(data6.MeterID[i])
		print(svalue)		   
		print(bvalue)		   
		kk=bvalue-svalue
		if(bvalue==0 & svalue==0):
			kk=-1		
		sleep(0.1) #제대로 작동안하는듯하다	   
		for j in range(0,data7.CTime.count()):
			data8=data2[(data2.MeterID==data6.MeterID[i])] # 아래의 경우 2*o로 사용가능
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]
			data8=data8.drop_duplicates('CTime',keep='first') # 시간 중복데이터 제거 	 
			k=data8.FEP.count() # 하루치 LP갯수
			data8['FEP']=pd.to_numeric(data8['FEP'],errors='coerce') #쓰레기값 여부 확인을 위해 datatype 변경
			data8['LARAP']=pd.to_numeric(data8['LARAP'],errors='coerce')
			data8['LERAP']=pd.to_numeric(data8['LERAP'],errors='coerce')
			data8['AP']=pd.to_numeric(data8['AP'],errors='coerce')   
			# print(data8) #데이터 맞게 가지고 있음 
			if k!=96: #일일 LP 개수가 정상이 아닐경우 체크
				if k!=0:  
					printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			
			check=data8['FEP'].isnull().sum()+data8['LARAP'].isnull().sum()+data8['LERAP'].isnull().sum()+data8['AP'].isnull().sum()
			if check>0:
				printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)				
			else:	
				if kk==-1 :
					data10=data8[data8['FEP']>2000000]
				else :		   
					data10=data8[data8['FEP']>bvalue]
					data10=data10+data8[data8['FEP']<svalue]	 
					data10=data10+data8[data8['FEP']>2000000] #FEP의 쓰레기값 조건 범위 확인
					data10=data10+data8[data8['FEP']<0] #FEP의 쓰레기값 조건 범위 확인
					data10=data10+data8[data8['LARAP']>2000000]
					data10=data10+data8[data8['LARAP']<0]		 
					data10=data10+data8[data8['LERAP']>2000000]
					data10=data10+data8[data8['LERAP']<0]
					data10=data10+data8[data8['AP']>2000000]
					data10=data10+data8[data8['AP']<0]		
				if data10.empty==False: #하나라도 쓰레기값 범위인 경우
					printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile)	 	 

def grg(fname,tfile): #G,AE타입 정기검침
	data=pd.read_csv(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	data2=data[[" Meter ID"," Received Time"," APT1"," APT2"," RPT"," LPT"," PFT"]]
	data2.rename(columns={' APT1':'APT1'},inplace=True) #이하 처리를 위한 행제목 변경
	data2.rename(columns={' APT2':'APT2'},inplace=True)
	data2.rename(columns={' RPT':'RPT'},inplace=True)	   
	data2.rename(columns={' LPT':'LPT'},inplace=True)	   
	data2.rename(columns={' PFT':'PFT'},inplace=True)	   
	data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
	data2.rename(columns={' Received Time':'CTime'},inplace=True)

	data2['APT1']=pd.to_numeric(data2['APT1'],errors='coerce') #쓰레기값 여부 확인을 위해 datatype 변경
	data2['APT2']=pd.to_numeric(data2['APT2'],errors='coerce')
	data2['RPT']=pd.to_numeric(data2['RPT'],errors='coerce')
	data2['LPT']=pd.to_numeric(data2['LPT'],errors='coerce')
	data2['PFT']=pd.to_numeric(data2['PFT'],errors='coerce')
	   
	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	   
	for i in range(0,data6.MeterID.count()):
		for j in range(0,data7.CTime.count()):
			data8=data2[(data2.MeterID==data6.MeterID[i])] # 아래의 경우 2*o로 사용가능
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]
		#  data8=data8.drop_duplicates('CTime',keep='first') # 시간 중복데이터 제거 
			k=data8.APT1.count() # 하루치 LP갯수
 
			if not(k==6 or k==12 or k==18 or k==24) : #일일 LP 개수가 정상이 아닐경우 체크
				if k!=0:  
					printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)

			check=data8['APT1'].isnull().sum()+data8['APT2'].isnull().sum()+data8['RPT'].isnull().sum()+data8['LPT'].isnull().sum()+data8['PFT'].isnull().sum()
			if check>0:
				printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			else :			
				data10=data8[data8['APT1']>2000000] #FEP의 쓰레기값 조건 범위 확인
				data10=data10+data8[data8['APT1']<0] #FEP의 쓰레기값 조건 범위 확인
				data10=data10+data8[data8['APT2']>2000000]
				data10=data10+data8[data8['APT2']<0]		 
				data10=data10+data8[data8['RPT']>2000000]
				data10=data10+data8[data8['RPT']<0]
				data10=data10+data8[data8['LPT']>2000000]
				data10=data10+data8[data8['LPT']<0]		 
				data10=data10+data8[data8['PFT']>1]
				data10=data10+data8[data8['PFT']<-1]	
		 
			if data10.empty==False: #하나라도 쓰레기값 범위인 경우
				printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile) 

def erg(fname,tfile): #E타입 정기검침
	data=pd.read_csv(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	data2=data[[" Meter ID"," Received Time"," SAP"," Status"]]
	data2.rename(columns={' SAP':'SAP'},inplace=True) #이하 처리를 위한 행제목 변경
	data2.rename(columns={' Status':'Status'},inplace=True)   
	data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
	data2.rename(columns={' Received Time':'CTime'},inplace=True)   

	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	   
	for i in range(0,data6.MeterID.count()):
		for j in range(0,data7.CTime.count()):
			data8=data2[(data2.MeterID==data6.MeterID[i])] # 아래의 경우 2*o로 사용가능
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]
#  data8=data8.drop_duplicates('CTime',keep='first') # 시간 중복데이터 제거 
			k=data8.SAP.count() # 하루치 LP갯수
 
			if not(k==6 or k==12 or k==18 or k==24) : #일일 정기검침 개수가 정상이 아닐경우 체크
				if k!=0:
					printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			data8['SAP']=pd.to_numeric(data8['SAP'],errors='coerce') #쓰레기값 여부 확인을 위해 datatype 변경
			data8['Status']=pd.to_numeric(data8['Status'],errors='coerce')   

			check=data8['SAP'].isnull().sum()+data8['Status'].isnull().sum()
			if check>0:
				printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)
   
			else :
				data10=data8[data8['SAP']>2000000] #SAP의 쓰레기값 조건 범위 확인
				data10=data10+data8[data8['SAP']<0]
				data10=data10+data8[data8['Status']!=1]	 
			if data10.empty==False: #하나라도 쓰레기값 범위인 경우
				printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile)	      

def srg(fname,tfile): #S타입 정기/현재검침
	data=pd.read_csv(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	data2=data[[" Meter ID"," Received Time"," APT"," RPT"," PFT"," 검침구분"]]
	data2.rename(columns={' APT':'APT'},inplace=True) #이하 처리를 위한 행제목 변경
	data2.rename(columns={' RPT':'RPT'},inplace=True)	      
	data2.rename(columns={' PFT':'PFT'},inplace=True)	   
	data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
	data2.rename(columns={' Received Time':'CTime'},inplace=True)   
	data2.rename(columns={' 검침구분':'sel'},inplace=True)  
		
	data2['APT']=pd.to_numeric(data2['APT'],errors='coerce')
	data2['RPT']=pd.to_numeric(data2['RPT'],errors='coerce')
	data2['PFT']=pd.to_numeric(data2['PFT'],errors='coerce')
	   
	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	   
	for i in range(0,data6.MeterID.count()):
		for j in range(0,data7.CTime.count()):
			data8=data2[(data2.MeterID==data6.MeterID[i])] # 아래의 경우 2*o로 사용가능
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]
			data9=data8[(data8['sel'].str.contains("현재검침"))]
			data8=data8[(data8['sel'].str.contains("정기검침"))]
			k=data8.APT.count() # 하루치 정기검침 갯수
			l=data9.APT.count() # 하루치 현재검침 갯수
		 
			if k!=0: #일일 LP 개수가 정상이 아닐경우 체크
				if not(k==6 or k==12 or k==18 or k==24):
					print(k,'개 입니다. 1')
					tfile.write('정기 검침\n')		  
					printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			if not(94<l<98): #일일 LP 개수가 정상이 아닐경우 체크
				if l!=0:  
					tfile.write('현재 검침\n')				  
					printall(1,data6.MeterID[i],data7.CTime[j],str(l),tfile)
		   
			check=data8['APT'].isnull().sum()+data8['RPT'].isnull().sum()+data8['PFT'].isnull().sum()+data9['APT'].isnull().sum()+data9['RPT'].isnull().sum()+data9['PFT'].isnull().sum()
			if check>0:
				printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			else :
				data10=data8[data8['APT']>20000000]
				data10=data10+data8[data8['APT']<0]
				data10=data10+data8[data8['RPT']>20000000]
				data10=data10+data8[data8['RPT']>20000000]
				data10=data10+data8[data8['PFT']>1]
				data10=data10+data8[data8['PFT']<-1]  

				data11=data9[data9['APT']>20000000]
				data11=data11+data9[data9['APT']<0]
				data11=data11+data9[data9['RPT']>20000000]
				data11=data11+data9[data9['RPT']>20000000]
				data11=data11+data9[data9['PFT']>1]
				data11=data11+data9[data9['PFT']<-1] 
		 
				if data10.empty==False: #하나라도 쓰레기값 범위인 경우
					tfile.write('정기 검침\n')				  
					printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile)   		 
				if data11.empty==False: #하나라도 쓰레기값 범위인 경우
					tfile.write('현재 검침\n')		
					printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile)    		 

def avg(fname,tfile): #G,AE타입 평균전압/전류
	data=pd.read_csv(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	if ' AVG_VOL' in data.columns :
		data2=data[[" Meter ID"," VOL CTime"," AVG_VOL"," AVG_AMP"]]
		data2.rename(columns={' AVG_VOL':'VOL'},inplace=True) #이하 처리를 위한 행제목 변경
		data2.rename(columns={' AVG_AMP':'AMP'},inplace=True)	      
		data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
		data2.rename(columns={' VOL CTime':'CTime'},inplace=True)   

	elif ' VOL_AB' in data.columns :
		data2=data[[" Meter ID"," VOL CTime"," VOL_AB"," AMP_A"]]
		data2.rename(columns={' VOL_AB':'VOL'},inplace=True) #이하 처리를 위한 행제목 변경
		data2.rename(columns={' AMP_A':'AMP'},inplace=True)	      
		data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
		data2.rename(columns={' VOL CTime':'CTime'},inplace=True)
		
	else :
		tfile.write('평균전압/전류 파일이 이상합니다. 확인이 필요합니다.')		   
		
	data2['VOL']=pd.to_numeric(data2['VOL'],errors='coerce')
	data2['AMP']=pd.to_numeric(data2['AMP'],errors='coerce')

	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	   
	for i in range(0,data6.MeterID.count()):
		for j in range(0,data7.CTime.count()):
			data8=data2[(data2.MeterID==data6.MeterID[i])] # 아래의 경우 2*o로 사용가능
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]
			k=data8.VOL.count() # 하루치 평균전압전류 갯수
		 
			if k!=96: #일일 LP 개수가 정상이 아닐경우 체크
				if k!=0:  
					printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)

			check=data8['VOL'].isnull().sum()+data8['AMP'].isnull().sum()
			if check>0:
				printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)  
			else :		   
				data10=data8[data8['VOL']>235]
				data10=data10+data8[data8['VOL']<220]
				data10=data10+data8[data8['AMP']>10]
				data10=data10+data8[data8['AMP']<0] 

			if data10.empty==False: #하나라도 쓰레기값 범위인 경우
				printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile)		 

def grd(fname,tfile): #G,AE타입 정기수요 데이터
	data=pd.read_csv(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	data2=data[[" Meter ID"," Received Time"," ITime"," MTime"," AP"," TAP"]]
	data2.rename(columns={' AP':'AP'},inplace=True) #이하 처리를 위한 행제목 변경
	data2.rename(columns={' TAP':'TAP'},inplace=True)
	data2.rename(columns={' ITime':'ITime'},inplace=True)	   
	data2.rename(columns={' MTime':'MTime'},inplace=True)	   
	data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
	data2.rename(columns={' Received Time':'CTime'},inplace=True)

	data2['AP']=pd.to_numeric(data2['AP'],errors='coerce') #쓰레기값 여부 확인을 위해 datatype 변경
	data2['TAP']=pd.to_numeric(data2['TAP'],errors='coerce')
	   
	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	   
	for i in range(0,data6.MeterID.count()):
		for j in range(0,data7.CTime.count()):
			data8=data2[(data2.MeterID==data6.MeterID[i])] # 아래의 경우 2*o로 사용가능
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]
		#  data8=data8.drop_duplicates('CTime',keep='first') # 시간 중복데이터 제거 
			k=data8.AP.count() # 하루치 LP갯수
			#개수 분석부
			if k!=6 and k!=12 and k!=18 and k!=24: #일일 개수가 정상이 아닐경우 체크
				if k!=0:  
					printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)
						
			#MTime 분석부
			data9=data8[(data8.ITime==data8.MTime)] #MTime이 ITime과 같을때
			data9=data9+data8[(data8.CTime==data8.MTime)] #MTime이 Received time과 같을때
			if data9.empty==False:
				printall(4,data6.MeterID[i],data7.CTime[j],str(k),tfile) 
				
			'''
			data10=data9[['MTime']] # 시간축 데이터만 잘라냄
			data10['MTime']=data10['MTime'].apply(lambda f:f.split()[0]) # MTime이 2000년으로 출력되는경우
			data10=data10[(data10.MTime=='2000')]
			if data10.empty==False:
				printall(4,data6.MeterID[i],data7.CTime[j],str(k),tfile) 
			'''
			#데이터 분석부
			check=data8['AP'].isnull().sum()+data8['TAP'].isnull().sum()
			if check>0:
				printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			else :
				data10=data8[data8['AP']>2000000] #FEP의 쓰레기값 조건 범위 확인
				data10=data10+data8[data8['AP']<0] #FEP의 쓰레기값 조건 범위 확인
				data10=data10+data8[data8['TAP']>2000000]
				data10=data10+data8[data8['TAP']<0]		 
		 
			if data10.empty==False: #하나라도 쓰레기값 범위인 경우
				printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile) 		
				
def sgd(fname,tfile): #S타입 정기/현재수요 데이터
	data=pd.read_csv(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	data2=data[[" Meter ID"," Received Time"," ITime"," MTime"," AP"," TAP"," 검침구분"]]
	data2.rename(columns={' AP':'AP'},inplace=True) #이하 처리를 위한 행제목 변경
	data2.rename(columns={' TAP':'TAP'},inplace=True)
	data2.rename(columns={' ITime':'ITime'},inplace=True)	   
	data2.rename(columns={' MTime':'MTime'},inplace=True)	   
	data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
	data2.rename(columns={' Received Time':'CTime'},inplace=True)
	data2.rename(columns={' 검침구분':'sel'},inplace=True)

	data2['AP']=pd.to_numeric(data2['AP'],errors='coerce') #쓰레기값 여부 확인을 위해 datatype 변경
	data2['TAP']=pd.to_numeric(data2['TAP'],errors='coerce')
	   
	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	   
	for i in range(0,data6.MeterID.count()):
		for j in range(0,data7.CTime.count()):
			data8=data2[(data2.MeterID==data6.MeterID[i])] # 아래의 경우 2*o로 사용가능
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]
			data9=data8[(data8['sel'].str.contains("현재수요"))]
			data8=data8[(data8['sel'].str.contains("정기수요"))]
			k=data8.AP.count() # 하루치 정기검침 갯수
			l=data9.AP.count() # 하루치 현재검침 갯수

			#개수 분석부
			
			if k!=0: #일일 LP 개수가 정상이 아닐경우 체크
				if not(k==6 or k==12 or k==18 or k==24):
					print(k,'개 입니다. 1')
					tfile.write('정기 수요\n')		  
					printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)

			if l!=0: #일일 LP 개수가 정상이 아닐경우 체크
				if not(l==6 or l==12 or l==18 or l==24):
					print(l,'개 입니다. 1')
					tfile.write('현재 수요\n')		  
					printall(1,data6.MeterID[i],data7.CTime[j],str(l),tfile)			
						
			#MTime 분석부
			data10=data8[(data8.ITime==data8.MTime)] #MTime이 ITime과 같을때
			data10=data10+data8[(data8.CTime==data8.MTime)] #MTime이 Received time과 같을때
			if data10.empty==False:
				tfile.write('정기 수요\n')
				printall(4,data6.MeterID[i],data7.CTime[j],str(k),tfile) 
				
			data10=data9[(data9.ITime==data9.MTime)] #MTime이 ITime과 같을때
			data10=data10+data9[(data9.CTime==data9.MTime)] #MTime이 Received time과 같을때
			if data10.empty==False:
				tfile.write('현재 수요\n')
				printall(4,data6.MeterID[i],data7.CTime[j],str(k),tfile) 	

			#데이터 분석부
			check=data8['AP'].isnull().sum()+data8['TAP'].isnull().sum()+data9['AP'].isnull().sum()+data9['TAP'].isnull().sum()
			if check>0:
				printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			else :			
				data10=data8[data8['AP']>2000000] #FEP의 쓰레기값 조건 범위 확인
				data10=data10+data8[data8['AP']<0] #FEP의 쓰레기값 조건 범위 확인
				data10=data10+data8[data8['TAP']>2000000]
				data10=data10+data8[data8['TAP']<0]		 
				
				data11=data9[data9['AP']>2000000] #FEP의 쓰레기값 조건 범위 확인
				data11=data11+data9[data9['AP']<0] #FEP의 쓰레기값 조건 범위 확인
				data11=data11+data9[data9['TAP']>2000000]
				data11=data11+data9[data9['TAP']<0]		 
		 
			if data10.empty==False: #하나라도 쓰레기값 범위인 경우
				tfile.write('정기 수요\n')
				printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile) 
				
			if data11.empty==False: #하나라도 쓰레기값 범위인 경우
				tfile.write('현재 수요\n')
				printall(3,data6.MeterID[i],data7.CTime[j],str(l),tfile) 	
				
def gva(fname,tfile): #G,AE타입 순시전압 데이터
	data=pd.read_csv(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	data2=data[[" Meter ID"," Received Time"," ITime"," MTime"," INS_AMP_A"," INS_VOL_A"," INS_VOL_THD_A"," INS_PF_A"," INS_VI_Phase_A"," INS_TEMP"]]
	data2.rename(columns={' INS_AMP_A':'AMP'},inplace=True) #이하 처리를 위한 행제목 변경
	data2.rename(columns={' INS_VOL_A':'VOL'},inplace=True)
	data2.rename(columns={' INS_VOL_THD_A':'THD'},inplace=True)
	data2.rename(columns={' INS_PF_A':'PF'},inplace=True)
	data2.rename(columns={' INS_VI_Phase_A':'PH'},inplace=True)
	data2.rename(columns={' INS_TEMP':'TEMP'},inplace=True)
	data2.rename(columns={' ITime':'ITime'},inplace=True)	   
	data2.rename(columns={' MTime':'MTime'},inplace=True)	   
	data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
	data2.rename(columns={' Received Time':'CTime'},inplace=True)

	data2['AMP']=pd.to_numeric(data2['AMP'],errors='coerce') #쓰레기값 여부 확인을 위해 datatype 변경
	data2['VOL']=pd.to_numeric(data2['VOL'],errors='coerce')
	data2['THD']=pd.to_numeric(data2['THD'],errors='coerce')
	data2['PF']=pd.to_numeric(data2['PF'],errors='coerce')
	data2['PH']=pd.to_numeric(data2['PH'],errors='coerce')
	data2['TEMP']=pd.to_numeric(data2['TEMP'],errors='coerce')
	   
	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	   
	for i in range(0,data6.MeterID.count()):
		for j in range(0,data7.CTime.count()):
			data8=data2[(data2.MeterID==data6.MeterID[i])] # 아래의 경우 2*o로 사용가능
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]
			k=data8.AMP.count() # 하루치 LP갯수
			#개수 분석부
			if k!=24: #일일 개수가 정상이 아닐경우 체크
				if k!=0:  
					printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)
						
			#MTime 분석부
			data9=data8[(data8.ITime==data8.MTime)] #MTime이 ITime과 같을때
			data9=data9+data8[(data8.CTime==data8.MTime)] #MTime이 Received time과 같을때
			o=data9.AMP.count()
			if k==o:
				printall(4,data6.MeterID[i],data7.CTime[j],str(k),tfile) 
				
			'''
			data10=data9[['MTime']] # 시간축 데이터만 잘라냄
			data10['MTime']=data10['MTime'].apply(lambda f:f.split()[0]) # MTime이 2000년으로 출력되는경우
			data10=data10[(data10.MTime=='2000')]
			if data10.empty==False:
				printall(4,data6.MeterID[i],data7.CTime[j],str(k),tfile) 
			'''
			#데이터 분석부
			check=data8['AMP'].isnull().sum()+data8['VOL'].isnull().sum()+data8['THD'].isnull().sum()+data8['PF'].isnull().sum()+data8['PH'].isnull().sum()+data8['TEMP'].isnull().sum()
			if check>0:
				printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			else :			
				data10=data8[data8['AMP']>10] #FEP의 쓰레기값 조건 범위 확인
				data10=data10+data8[data8['AMP']<0] #FEP의 쓰레기값 조건 범위 확인
				data10=data10+data8[data8['VOL']>240]
				data10=data10+data8[data8['VOL']<210]
				data10=data10+data8[data8['THD']>100]
				data10=data10+data8[data8['THD']<0]
				data10=data10+data8[data8['PF']>100]
				#data10=data10+data8[data8['PF']<0]
				data10=data10+data8[data8['PF']<-1]  #현재 역률 값이 -1로 출력되는 계기가 있음, 확인이 필요하며 코드 작성을 위해 -1로 고정해둠
				data10=data10+data8[data8['PH']>360]
				data10=data10+data8[data8['PH']<0]
				data10=data10+data8[data8['TEMP']>40]
				data10=data10+data8[data8['TEMP']<10]
				
			if data10.empty==False: #하나라도 쓰레기값 범위인 경우
				printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile) 		
						
def emax(fname,tfile): #E타입 최대부하전류
	data=pd.read_csv(fname)
	data=data.replace(['"','='],['',''],regex=True) # 특수문자 제거
	data2=data[[" Meter ID"," Received Time"," ITime"," Max Current"]]
	data2.rename(columns={' Max Current':'MC'},inplace=True) #이하 처리를 위한 행제목 변경
	data2.rename(columns={' ITime':'ITime'},inplace=True)	   
	data2.rename(columns={' MTime':'MTime'},inplace=True)	   
	data2.rename(columns={' Meter ID':'MeterID'},inplace=True)
	data2.rename(columns={' Received Time':'CTime'},inplace=True)

	data2['MC']=pd.to_numeric(data2['MC'],errors='coerce') #쓰레기값 여부 확인을 위해 datatype 변경
	   
	data6=data2.drop_duplicates('MeterID',keep='first') # 미터정보만 남김
	data6.MeterID.count() #전체 미터 갯수
	data6.MeterID.values #전체 미터 번호
	data6=data6.reset_index(drop=True)
	   
	data7=data2[['CTime']] # 시간축 데이터만 잘라냄
	data7['CTime']=data7['CTime'].apply(lambda e:e.split()[0]) # 블록단위로 자름
	data7=data7.drop_duplicates('CTime',keep='first')
	data7.sort_values('CTime')
	data7=data7.reset_index(drop=True)
	   
	for i in range(0,data6.MeterID.count()):
		for j in range(0,data7.CTime.count()):
			data8=data2[(data2.MeterID==data6.MeterID[i])] # 아래의 경우 2*o로 사용가능
			data8=data8[(data8['CTime'].str.contains(data7.CTime[j]))]
			k=data8.MC.count() # 하루치 LP갯수
			#개수 분석부
			if not(k==6 or k==12 or k==18 or k==24): #일일 개수가 정상이 아닐경우 체크
				if k!=0:  
					printall(1,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			#MTime은 오류가 나서 잠정적으로 비워둠, 추후 수정 요망
			'''						
			#MTime 분석부
			data9=data8[(data8.ITime==data8.MTime)] #MTime이 ITime과 같을때
			data9=data9+data8[(data8.CTime==data8.MTime)] #MTime이 Received time과 같을때
			o=data9.MC.count()
			if k==o:
				printall(4,data6.MeterID[i],data7.CTime[j],str(k),tfile) 


			data10=data9[['MTime']] # 시간축 데이터만 잘라냄
			data10['MTime']=data10['MTime'].apply(lambda f:f.split()[0]) # MTime이 2000년으로 출력되는경우
			data10=data10[(data10.MTime=='2000')]
			if data10.empty==False:
				printall(4,data6.MeterID[i],data7.CTime[j],str(k),tfile) 
			'''

			#데이터 분석부
			check=data8['MC'].isnull().sum()
			if check>0:
				printall(2,data6.MeterID[i],data7.CTime[j],str(k),tfile)
			else :			
				data10=data8[data8['MC']>100] #FEP의 쓰레기값 조건 범위 확인
				data10=data10+data8[data8['MC']<0] #FEP의 쓰레기값 조건 범위 확인
				
			if data10.empty==False: #하나라도 쓰레기값 범위인 경우
				printall(3,data6.MeterID[i],data7.CTime[j],str(k),tfile) 		