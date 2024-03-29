import zipfile
import os
import glob
from datetime import datetime
import shutil

import pandas as pd
import numpy as np
from time import sleep
from autofunction import * # 실제 분석 함수 구현 test파일은 검침구분 나누고 지정하는용도

# 날짜값 정리
jumpcodem=""  # 월일값에 0이 들어갈때를 위한 jumpcode
jumpcoded=""
if int(datetime.today().month)<10:
	jumpcodem="0"
if int(datetime.today().day)<10:
	jumpcoded="0"
	
# 분석 결과 경로 만들고 결과파일 제작
path='C:\\AAA-NURI\\EmuAgent\\Result\\분석결과\\'+jumpcodem+str(datetime.today().month)+jumpcoded+str(datetime.today().day) 
os.makedirs(path)
filename=path+'\\'+str(datetime.today().year)+'-'+jumpcodem+str(datetime.today().month)+'-'+jumpcoded+str(datetime.today().day)+'-'+'분석 결과.txt'
tfile = open(filename, mode='wt', encoding='utf-8')

for i in range(0,18): # 파일 숫자 다시 집어넣어야함, for문안에 전체 기능 넣으면 될것같음, 현재 AE,G,E,S 파일 다해서 18개임 추후 보안계기 늘어나면 이부분 변경

	list_of_files = glob.glob('C:\\AAA-NURI\\EmuAgent\\Result\\'+jumpcodem+str(datetime.today().month)+jumpcoded+str(datetime.today().day)+'\\*') # Result 결과가 저장되는 폴더명
	#print(str(datetime.today().month)+jumpcode+str(datetime.today().day)+'\\*')
	latest_file = max(list_of_files, key=os.path.getctime) # 가장 최근 생성된 파일의 경로
#	print(latest_file)
#	glp(latest_file,tfile)

	if latest_file[33:38]=='Gtype' : # 파일명에 Gtype이 먼저 들어갈때
		if latest_file[39:41]=='LP' :
			tfile.write('\n************************************************G LP************************************************\n')
			glp(latest_file,tfile)
		elif latest_file[39:43]=='정기검침' :
			tfile.write('\n************************************************G 정기검침************************************************\n')
			grg(latest_file,tfile)
			print('G 정기검침')
		elif latest_file[39:45]=='정기최대수요' :
			tfile.write('\n************************************************G 정기수요************************************************\n')	
			grd(latest_file,tfile)
			print('G 정기최대수요')
		elif latest_file[39:45]=='현재최대수요' :
			tfile.write('\n************************************************G 현재최대수요************************************************\n')
			grd(latest_file,tfile)			
			print('G 현재최대수요')
		elif latest_file[39:45]=='순시전압전류' :
			tfile.write('\n************************************************G 순시전압전류************************************************\n')
			gva(latest_file,tfile)
			print('G 순시전압전류')
		elif latest_file[39:45]=='평균전압전류' :
			tfile.write('\n************************************************G 평균전압전류************************************************\n')
			avg(latest_file,tfile)
			print('G 평균전압전류')
		else :
			print(latest_file[33:])
			print('G타입 파일이름오류')
			break
			
	elif latest_file[33:39]=='AEtype' : # 파일명에 AE타입이 먼저 들어갈때
		if latest_file[40:42]=='LP' :
			tfile.write('\n************************************************AE LP************************************************\n')		
			glp(latest_file,tfile)		
			print('AE LP')
		elif latest_file[40:44]=='정기검침' :
			tfile.write('\n************************************************AE 정기검침************************************************\n')	
			grg(latest_file,tfile)
			print('AE 정기검침')
		elif latest_file[40:46]=='정기최대수요' :
			tfile.write('\n************************************************AE 정기최대수요************************************************\n')		
			grd(latest_file,tfile)
			print('AE 정기최대수요')
		elif latest_file[40:46]=='현재최대수요' :
			tfile.write('\n************************************************AE 현재최대수요************************************************\n')
			print('AE 현재최대수요')
			grd(latest_file,tfile)			
		elif latest_file[40:46]=='순시전압전류' :
			tfile.write('\n************************************************AE 순시전압전류************************************************\n')		
			gva(latest_file,tfile)
			print('AE 순시전압전류')
		elif latest_file[40:46]=='평균전압전류' :
			tfile.write('\n************************************************AE 평균전압전류************************************************\n')		
			avg(latest_file,tfile)
			print('AE 평균전압전류')
		else :
			print(latest_file[33:])
			print('AE타입 파일이름오류')
			break

	elif latest_file[33:38]=='Etype' : #파일명에 E타입이 먼저 들어갈때
		if latest_file[39:41]=='LP' :
			tfile.write('\n************************************************E LP************************************************\n')
			elp(latest_file,tfile)
			print('E LP')
		elif latest_file[39:43]=='정기검침' :
			tfile.write('\n************************************************E 정기검침************************************************\n')
			erg(latest_file,tfile)
			print('E 정기검침')
		elif latest_file[39:45]=='최대부하전류' :
			tfile.write('\n************************************************E 최대부하전류************************************************\n')
			emax(latest_file,tfile)
			print('E 최대부하전류')
		else :
			print(latest_file[33:])
			print('E타입 파일이름오류')
			break
			
	elif latest_file[33:38]=='Stype' : #파일명에 S타입이 먼저 들어갈때
		if latest_file[39:41]=='LP' :
			tfile.write('\n************************************************S LP************************************************\n')		
			glp(latest_file,tfile)
			print('S LP')
		elif latest_file[39:45]=='현재정기검침' :
			tfile.write('\n************************************************S 현재/정기검침************************************************\n')		
			srg(latest_file,tfile)
			print('S 정기검침')
		elif latest_file[39:43]=='최대수요' :
			tfile.write('\n************************************************S 최대수요************************************************\n')		
			sgd(latest_file,tfile)
			print('S 최대수요')
		else :
			print(latest_file[33:])
			print('S타입 파일이름오류')
			break
			
	else :
		print('파일이름 오류')
		break
	tfile.write('\n\n')
	shutil.move(latest_file,path+'\\'+latest_file[33:]) #분석내용을 결과폴더로 옮김