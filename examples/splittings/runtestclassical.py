import numpy as np
import matplotlib.pyplot as plt

import expsolve as es
import expsolve.discretize.tensorgrid as ex
import expsolve.evolve.splittings.classical as split

from torch import exp

n = 200
L = 10
xr = [-L, L]
x = ex.grid1d(n, xr)

x0 = -2.0
u = exp(-(x-x0)**2/(2*0.25))
u = ex.normalize(u, xr)

V = x**4 - 10*x**2

eLu = lambda t, tauV, h, c, u: ex.diffopexp(0, 2, 1j*h*c, u, xr)
eVu = lambda t, tauL, h, c, u: exp(-1j*h*c*V)*u

trotteralpha, trotterbeta = split.consistent([],[])
strangalpha, strangbeta = split.symmetric([],[])
a = np.array([0.0792036964311957, 0.353172906049774, -0.0420650803577195])
b = np.array([0.209515106613362, -0.143851773179818])
blanesmoanalpha, blanesmoanbeta = split.symmetric(a, b)

trotterstep = lambda t, h, u0: split.stepper(t, h, u0, eVu, eLu, trotteralpha, trotterbeta)
strangstep = lambda t, h, u0: split.stepper(t, h, u0, eVu, eLu, strangalpha, strangbeta)
blanesmoanstep = lambda t, h, u0: split.stepper(t, h, u0, eVu, eLu, blanesmoanalpha, blanesmoanbeta)


observables = {'energy': lambda u: ex.observable(lambda psi: -ex.diffop(0, 2, psi, xr) + V*psi, u, xr), 
'position': lambda u: ex.observable(lambda psi: x*psi, u, xr), 
'momentum': lambda u: ex.observable(lambda psi: 1j*ex.diffop(0, 1, psi, xr), u, xr), 
'kinetic': lambda u: ex.observable(lambda psi: -ex.diffop(0, 2, psi, xr), u, xr), 
'potential':lambda u: ex.observable(lambda psi: V*psi, u, xr)}

T = 1
N = 1000
timegrid = es.timegrid(T, N)

trotterevolve = es.solvediffeq(u, timegrid, trotterstep, observables)
strangevolve = es.solvediffeq(u, timegrid, strangstep, observables)
blanesmoanevolve = es.solvediffeq(u, timegrid, blanesmoanstep, observables)

obsvalues_trotter = trotterevolve[1]
obsvalues_strang = strangevolve[1]
obsvalues_blanesmoan = blanesmoanevolve[1]

plt.figure()

E0 = obsvalues_trotter['energy'][0][0]

plt.semilogy(timegrid, np.abs(obsvalues_trotter['energy'][0]-E0))
plt.semilogy(timegrid, np.abs(obsvalues_strang['energy'][0]-E0))
plt.semilogy(timegrid, np.abs(obsvalues_blanesmoan['energy'][0]-E0))
plt.legend(['Trotter','Strang','Blanes-Moan'])
plt.ylabel('change in energy')
plt.xlabel('time')
plt.show()