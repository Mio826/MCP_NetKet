import netket as nk
import netket.experimental as nkx
from netket.experimental.operator.fermion import destroy as c
from netket.experimental.operator.fermion import create as cdag
from netket.experimental.operator.fermion import identity as ID

#fermion function
def nup(hi,i):
    return cdag(hi,i,1)*c(hi,i,1)
def ndown(hi,i):
    return cdag(hi,i,-1)*c(hi,i,-1)
def n(hi,i):
    return nup(hi,i)+ndown(hi,i)
def bond(hi,i,j):
    return sum(cdag(hi,j,s)*c(hi,i,s)+cdag(hi,i,s)*c(hi,j,s) for s in [1,-1])
def electron_spin(hi,i):
  Sx = 0.5*(cdag(hi,i,1)*c(hi,i,-1)+cdag(hi,i,-1)*c(hi,i,1))
  Sy = 0.5*(-1j*cdag(hi,i,1)*c(hi,i,-1)+1j*cdag(hi,i,-1)*c(hi,i,1))
  Sz = 0.5*(cdag(hi,i,1)*c(hi,i,1)-cdag(hi,i,-1)*c(hi,i,-1))
  return [Sx,Sy,Sz]
def Hop(hi,graph,t):
    H_t = 0.0
    for (i, j) in graph.edges():
        H_t -= t * sum((cdag(hi, i, s) * c(hi, j, s) + cdag(hi, j, s) * c(hi, i, s)) for s in [1, -1])
    return H_t
def Hubbard(hi,graph,v0):
    H_v0 = 0
    for i in graph.nodes():
        H_v0 += v0 * nup(hi, i) * ndown(hi, i)
    return H_v0
def Coulomb(hi,graph,v1):
    H_v1 = 0
    for (i, j) in graph.edges():
        H_v1 += v1 * (n(hi, i) * n(hi, j))
    return H_v1
def Zeeman(hi,graph,B):
    H_h = 0
    for i in graph.nodes():
        H_h += B * electron_spin(hi, i)[2]
    return H_h

#boson function

#spin function