import datetime
import numpy as np
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt

def read_trim(fdir):
    mn = 0;
    f = open(fdir, 'r')
    flines = f.readlines();

    #----------------------------------------------------------------------
    # read header

    fmap = np.empty([1,7]).astype(np.int);
    emap = np.empty([1,7]).astype(np.int);

    for i in range(0,6):
        fmap[0,i] = int(flines[3][i*6:(i+1)*6]);
    for i in range(0,6):
        emap[0,i] = int(flines[4][i*6:(i+1)*6]);   

    year = fmap[0,0]
    mo   = fmap[0,1]
    day  = fmap[0,2]
    hour = fmap[0,3]

    dt   = int(flines[5][0:6])
    nmap = int(flines[6][0:6])
    ecut = float(flines[7][0:7])
    nsta = int(flines[8][0:6])
    temp = flines[11].split()
    hght = float(temp[0])

    temp = flines[12].split()
    mLat = float(temp[0])
    MLat = float(temp[1])
    dLat = float(temp[2])
    nLat = int((MLat-mLat)/dLat+1);
    xLat = np.arange(mLat,MLat+dLat,dLat).astype(np.float)

    temp = flines[13].split()
    mLon = float(temp[0])
    MLon = float(temp[1])
    dLon = float(temp[2])
    nLon = int((MLon-mLon)/dLon+1);
    xLon = np.arange(mLon,MLon+dLon,dLon)

    #----------------------------------------------------------------------
    # read map

    lLon = int(np.ceil(nLon/16)); # lines of longitude data in *.i file
    lMap = int(((lLon+1)*nLat+1)+2); # lines of single map
    sMap = int(17+(mn/5)*lMap)

    TEC = np.empty([nLat,nLon])
    temp = flines[sMap].split();
    for i in range(0,nLat):
        temp = flines[sMap+1+i*3].split()
        for j in range(0,lLon):
            temp = flines[sMap+1+i*(lLon+1)+1+j].split()
            for k in range(0,len(temp)):
                TEC[i,j*16+k] = float(temp[k])/10

    return TEC, {'YEAR':year, 'MONTH':mo, 'DAY':day, 'HOUR':hour, 'INTERVAL':dt, 'NO_OF_MAP':nmap, 'ELEVATION_CUTOFF':ecut, 'NO_OF_STATIONS':nsta, 'HEIGHT':hght, 'LATITUDE':xLat, 'LONGITUDE':xLon}

def plot_trim(TEC, state, title, vmin, vmax, cmap):

    yr = state['YEAR']
    mo = state['MONTH']
    da = state['DAY']
    hr = state['HOUR']
    dt = state['INTERVAL']
    nsta = state['NO_OF_STATIONS']
    hght = state['HEIGHT']
    ecut = state['ELEVATION_CUTOFF']
    dLon = state['LONGITUDE'][1]-state['LONGITUDE'][0]
    mLon = np.min(state['LONGITUDE'])
    MLon = np.max(state['LONGITUDE'])
    dLat = state['LATITUDE'][1]-state['LATITUDE'][0]
    mLat = np.min(state['LATITUDE'])
    MLat = np.max(state['LATITUDE'])

    hdcoast = np.load('hdcoast.npy')

    fig = plt.figure()
    fig.set_size_inches(10,7)

    #----------------------------------------------------------------------
    # plot map            

    hdcoast = np.load('hdcoast.npy')

    fig = plt.figure()
    fig.set_size_inches(7,11)

    ax  = fig.add_axes([0.1,0.25,0.71,0.68])
    ext = [mLon,MLon,mLat,MLat]
    im  = ax.imshow(TEC,vmin=vmin,vmax=vmax,extent=ext,origin='lower',cmap=plt.get_cmap(cmap),interpolation='none')
    ax.plot(hdcoast[0,:],hdcoast[1,:],'k')

    ax.text(mLon+1.3,mLat-3,
            'INTERVAL(SEC) = '+str(dt)+'   | ',
            fontname="monospace",fontsize=12)

    ax.text(mLon+0.4*(MLon-mLon)+1.3,mLat-3,
            '# OF STATIONS = '+str(nsta),
            fontname="monospace",fontsize=12)

    ax.text(mLon+1.3,mLat-3.5,
            'HEIGHT   (KM) = '+str(hght)+' | ',
            fontname="monospace",fontsize=12)

    ax.text(mLon+0.4*(MLon-mLon)+1.3,mLat-3.5,
            'ELEVATION CUTOFF = '+str(ecut),
            fontname="monospace",fontsize=12)

    ax.text(mLon+1.3,mLat-4.0,
            'LONGITUDE(\u00b0E) MIN,MAX,INTERVAL = '+str(mLon)+', '+str(MLon)+', '+str(dLon),
            fontname="monospace",fontsize=12)

    ax.text(mLon+1.3,mLat-4.5,
            'LATITUDE (\u00b0N) MIN,MAX,INTERVAL = '+str(mLat)+', '+str(MLat)+', '+str(dLat),
            fontname="monospace",fontsize=12)

    ax.text(mLon+1.3,mLat-5.0,
            'TRIM   (TECU) MIN,MAX,MEDIAN   = '+str(np.min(TEC))+', '+str(np.max(TEC))+', '+str(np.median(TEC)),
            fontname="monospace",fontsize=12)

    ax.axis(ext)
    ax.set_title('TAIWAN REGIONAL IONOSPHERE MAPS'+title+' \n'+             
                 datetime.datetime(yr,mo,da,hr,0,0).strftime("%Y-%m-%d %H:%M")+' UT',
                 fontname="monospace",fontsize=18)
    ax.set_xlabel('GEOGRAPHIC LONGITUDE (\u00b0E)', fontname="monospace",fontsize=12)
    ax.set_ylabel('GEOGRAPHIC LATITUDE (\u00b0N)', fontname="monospace",fontsize=12)

    ax2 = ax.twiny()
    ax2.xaxis.set_ticks_position("bottom")
    ax2.xaxis.set_label_position("bottom")

    # Offset the twin axis below the host
    ax2.spines["bottom"].set_position(("axes", -0.1))

    # Turn on the frame for the twin axis, but then hide all 
    # but the bottom spine
    ax2.set_frame_on(True)
    ax2.patch.set_visible(False)
    ax2.spines["bottom"].set_visible(True)

    ax2.set_xticks(np.arange(-180,210,30)/15)
    ax2.set_xlim([mLon/15,(MLon+0.5)/15])
    ax2.set_xlabel("LOCAL TIME (LT)", fontname="monospace",fontsize=12)

    cax = fig.add_axes([0.86,0.25,0.04,0.68])
    clb = plt.colorbar(im, cax=cax, orientation="vertical")#, ticklocation='top')
    clb.set_label('TECU',fontsize=15)

    return fig

def movie_trim(TEC,state):

    yr = state['YEAR']
    mo = state['MONTH']
    da = state['DAY']
    hr = state['HOUR']
    dt = state['INTERVAL']
    nsta = state['NO_OF_STATIONS']
    hght = state['HEIGHT']
    ecut = state['ELEVATION_CUTOFF']
    dLon = state['LONGITUDE'][1]-state['LONGITUDE'][0]
    mLon = np.min(state['LONGITUDE'])
    MLon = np.max(state['LONGITUDE'])
    dLat = state['LATITUDE'][1]-state['LATITUDE'][0]
    mLat = np.min(state['LATITUDE'])
    MLat = np.max(state['LATITUDE'])

    #----------------------------------------------------------------------
    # plot map            

    hdcoast = np.load('hdcoast.npy')

    fig = plt.figure()
    fig.set_size_inches(8,5)

    ax  = fig.add_axes([0.1,0.1,0.7,0.78])
    ext = [115,127,18,30]
    im  = ax.imshow(TEC,vmin=0,vmax=50,extent=ext,origin='lower',cmap=plt.get_cmap('jet'),interpolation='none')
    ax.plot(hdcoast[0,:],hdcoast[1,:],'k')

    ax.axis(ext)
    ax.set_title('TAIWAN REGIONAL IONOSPHERE MAPS \n'+             
                 datetime.datetime(yr,mo,da,hr,0,0).strftime("%Y-%m-%d %H:%M")+' UT',
                 fontname="monospace",fontsize=18)
    ax.set_xlabel('GEOGRAPHIC LONGITUDE (\u00b0E)', fontname="monospace",fontsize=12)
    ax.set_ylabel('GEOGRAPHIC LATITUDE (\u00b0N)', fontname="monospace",fontsize=12)

    cax = fig.add_axes([0.75,0.1,0.02,0.78])
    clb = plt.colorbar(im, cax=cax, orientation="vertical")#, ticklocation='top')
    clb.set_label('TECU',fontsize=15)

    return fig
