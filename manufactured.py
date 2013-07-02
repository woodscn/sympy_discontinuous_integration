import sympy
from scipy.misc import derivative
from functools import partial

from heat_equation import MASA_solution, HeatEquation, MASA_source_lambda

class Error(Exception):
    pass

def recursive_derivative(func,x0_vec,dx_vec=None,n=1,args=(),order=3):
    if dx_vec is None:
        dx_vec = [1. for elem in x0_vec]
    return _RecursiveDerivative(func,x0_vec,dx_vec,n,order).differentiate(*args)

class _RecursiveDerivative(object):
    def __init__(self,func,x0_vec,dx_vec,n,order):
        self.func=func
        self.x0_vec=x0_vec
        self.dx_vec=dx_vec
        self.n=n
        self.order=order
        return None

    def differentiate(self, *args, **kwargs):
        depth = kwargs.pop('depth', 0)
        if kwargs:
            raise ValueError('unexpected kwargs')
        ind = -depth-1
        x0 = self.x0_vec[ind]
        dx = self.dx_vec[ind]
        if depth + 1 == len(self.x0_vec):
            f = self.func
        else:
            f = partial(self.differentiate, depth=depth+1)
        return derivative(f,x0,dx,self.n,args,self.order)


def RD_test(t,x,y,z):
    return t**2*x*y*z

if __name__=="__main__":
    print recursive_derivative(RD_test,(1,0,0,1))-2.0
    t = sympy.Symbol('t')
    x = sympy.Symbol('x')
    y = sympy.Symbol('y')
    z = sympy.Symbol('z')
    args = (.01,.01,.01,.01)
    kwargs = {
        'Ax':1,'At':0,'By':0,'Bt':0,'Cz':0,'Ct':0,'Dt':0,'rho':1,'cp':1,'k':1}
    eqn = HeatEquation(MASA_solution(**kwargs))
    junk = recursive_derivative(
        lambda x0,x1,x2,x3:eqn.balance_integrate(
            ((t,0,x0),(x,0,x1),(y,0,x2),(z,0,x3))),(1,1,1,1),args)
    import pdb;pdb.set_trace()
    check = MASA_source_lambda(**kwargs)(*args)
