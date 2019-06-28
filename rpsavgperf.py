import dd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

def rpsavgperf(shotnr, time=2.0, dt=0.005, side=1, experiment='AUGD'):
    """Returns an averaged radial density profile from O-mode Reflectometry

    Parameters
    ------------
    shotnr: int
            Number of the shot
    time: float
          Time instant for the profile
    dt: float
        Plus/Minus interval for averaging
    side: int
          1: LFS, 0: HFS
    experiment: string
                Default "AUGD", can be a user name

    Returns
    ------------
    raverage: np.array
              Array with average radial positions
    newdens: np.array
             Array with densities
    stddev: np.array
            One standard deviation in the radial dimension
    """
    ## Choose the objects for the vessel side
    if side:
        nld = "neb_LFS"
        rld = "RB_LFS"
    else:
        nld = "neb_HFS"
        rld = "RB_HFS"

    ti = time - dt
    tf = time + dt

    RPS = dd.shotfile("RPS", shotnr, experiment=experiment)
    ##Workaround the Area Base bug
    #nl = RPS(nld, tBegin=ti, tEnd=tf)    
    time = RPS("TIME")
    msk = ((time >= ti) & (time <=tf))
    nl = RPS(nld)
    dens = nl.data[msk,:]
    rl = RPS(rld)
    rad = rl.data[msk,:]
    RPS.close()

    maxne = min(dens[:,len(rad[1])-1])

    fitpts = 100

    newdens = np.linspace(0, maxne, fitpts)

    ravg = []

    for p in range(len(rad)):
        intp = interp1d(dens[p,:], rad[p,:])
        rra = intp(newdens)
        ravg.append(rra)
            
    raverage = np.average(ravg, axis=0)
    stddev = np.std(ravg, axis=0)
    stddev[stddev < 0.005] = 0.005

    class objview(object):
        def __init__(self, d):
            self.__dict__=d    
        
    return objview({'r': np.array(raverage),
                    'n': np.array(newdens),
                    'dr': np.array(stddev)})

#Standalone test function
if __name__ == "__main__":
    shotnr = 32349
    tperf = 2.895
    dt = 0.005
    side = 1

    perf = rpsavgperf(shotnr, time=tperf, dt=dt, side=side)

    plt.fill_betweenx(perf.d, perf.r-perf.dr, perf.r+perf.dr, color='#9999FF')
    plt.plot(perf.r, perf.d, color='b')

    plt.show()

