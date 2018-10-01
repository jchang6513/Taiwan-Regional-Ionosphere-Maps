import os
import glob
import datetime
import trim
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rimdir = '../TWRR/' # rim root directory, follow with year.doy directories
dates = pd.date_range(start='20180213 00:00',end='20180214 00:00', freq='H') # observation date range
K = 1.5 
mday = 15 # median day
fdir = 'img/'; # root directory of output image

TEC = np.empty([mday+1,31,25])
tec = np.empty([31,25])
ahr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
for date in dates:
	STATE = []
	for i in range(0,mday+1):
		da    = date-datetime.timedelta(mday-i)
		fName = da.strftime('TWRR%j'+ahr[da.hour]+'.%yI')
		fDir  = da.strftime(rimdir+'%Y.%j/')+fName
		print(da,date,fDir)
		try:
			tec, state = trim.read_trim(fDir)
		except Exception as e:
			print(e)
			tec = np.empty([31,25])
			tec[:] = np.nan
			state =  {'YEAR':date.year, 'MONTH':date.month, 'DAY':date.day, 'HOUR':date.hour, 'INTERVAL':np.nan, 'NO_OF_MAP':np.nan, 'ELEVATION_CUTOFF':np.nan, 'NO_OF_STATIONS':np.nan, 'HEIGHT':np.nan, 'LATITUDE':np.arange(17,32.5,0.5), 'LONGITUDE':np.arange(115,127.5,0.5)}

		TEC[i,:,:] = tec
		STATE = [STATE,state]
	
	oTEC   = TEC[-1,:,:]
	mTEC   = np.nanmedian(TEC[:-1,:,:],axis=0)
	p75TEC = np.nanpercentile(TEC[:-1,:,:],75,axis=0)
	p25TEC = np.nanpercentile(TEC[:-1,:,:],25,axis=0)
	uTEC   = mTEC+K*(p75TEC-mTEC)
	lTEC   = mTEC-K*(mTEC-p25TEC)
	ob     = oTEC-uTEC
	ob[ob<0] = 0 # location with (oTEC-uTEC)<0 are in bound, mark these location with 0
	ol     = oTEC-lTEC
	ob[ol<0] = ol[ol<0] # lcation with (oTEC-lTEC)<0 are negative anomaly

	if os.path.isdir(fdir+date.strftime('%Y.%j/')) == False:
		os.makedirs(fdir+date.strftime('%Y.%j/'))

	fig = trim.plot_trim(oTEC, state, '(O)', 0, 50, 'jet')
	fname = fdir+date.strftime('%Y.%j/')+fName+'.00.O.png'
	print(fname)
	fig.savefig(fname,dpi=150)
	fig.clf()
	
	fig = trim.plot_trim(mTEC, state, '(M)', 0, 50, 'jet')
	fname = fdir+date.strftime('%Y.%j/')+fName+'.00.M.png'
	print(fname)
	fig.savefig(fname,dpi=150)
	fig.clf()
	
#	fig = trim.plot_trim(oTEC-mTEC, state, '(O-M)', -20, 20, 'bwr')
#	fname = fdir+date.strftime('%Y.%j/')+fName+'.00.om.png'
#	print(fname)
#	fig.savefig(fname,dpi=150)
#	fig.clf()
	
#	fig = trim.plot_trim(oTEC-uTEC, state, '(O-UB)', 0, 20, 'Reds')
#	fname = fdir+date.strftime('%Y.%j/')+fName+'.00.OU.png'
#	print(fname)
#	fig.savefig(fname,dpi=150)
#	fig.clf()

#	fig = trim.plot_trim(oTEC-lTEC, state, '(O-LB)', 20, 0, 'Blues')
#	fname = fdir+date.strftime('%Y.%j/')+fName+'.00.OL.png'
#	print(fname)
#	fig.savefig(fname,dpi=150)
#	fig.clf()

	fig = trim.plot_trim(ob, state, '(O-B)', -20, 20, 'bwr')
	fname = fdir+date.strftime('%Y.%j/')+fName+'.00.OB.png'
	print(fname)
	fig.savefig(fname,dpi=150)
	fig.clf()
