import sympy
from sympy.utilities.lambdify import lambdify
H = sympy.special.delta_functions.Heaviside
from sympy import sin, cos

from base_equation import SympyEquation

Zero = sympy.singleton.S.Zero
t = sympy.Symbol('t')
xi = sympy.Symbol('xi')
eta = sympy.Symbol('eta')
zeta = sympy.Symbol('zeta')
gamma = sympy.Rational(7,5)

#def H(S):
#    if S>0:
#        out = 1.
#    else:
#        if S<0:
#            out = 0.
#        else:
#            out = .5
#    return out

class Euler_UCS(SympyEquation):
    def setup(self,**kwargs):
        (self.pressure,self.density,                # 
         self.vels_x,self.vels_y,self.vels_z,       # u, v, w
         self.dx_dxi,self.dy_dxi,self.dz_dxi,       # A, B, C
         self.dx_deta,self.dy_deta,self.dz_deta,    # L, M, N
         self.dx_dzeta,self.dy_dzeta,self.dz_dzeta, # P, Q, R
         self.dx_dt,self.dy_dt,self.dz_dt,          # U, V, W
         self.x,self.y,self.z) = self.sol
        self.gamma = gamma
        self.jacobian = (
            self.dx_dxi*
            (self.dy_deta*self.dz_dzeta-self.dz_deta*self.dy_dzeta) + 
            self.dy_dxi*
            (self.dz_deta*self.dx_dzeta-self.dx_deta*self.dz_dzeta) +
            self.dz_dxi*
            (self.dx_deta*self.dy_dzeta-self.dy_deta*self.dx_dzeta) )
        self.dxi_dx = (self.dy_deta*self.dz_dzeta-self.dz_deta*self.dy_dzeta
                       )/self.jacobian
        self.dxi_dy = (self.dz_deta*self.dx_dzeta-self.dx_deta*self.dz_dzeta
                       )/self.jacobian
        self.dxi_dz = (self.dx_deta*self.dy_dzeta-self.dy_deta*self.dx_dzeta
                       )/self.jacobian
        self.deta_dx = (self.dz_dxi*self.dy_dzeta-self.dy_dxi*self.dz_dzeta
                        )/self.jacobian
        self.deta_dy = (self.dx_dxi*self.dz_dzeta-self.dz_dxi*self.dx_dzeta
                        )/self.jacobian
        self.deta_dz = (self.dy_dxi*self.dx_dzeta-self.dx_dxi*self.dy_dzeta
                        )/self.jacobian
        self.dzeta_dx = (self.dy_dxi*self.dz_deta-self.dz_dxi*self.dy_deta
                         )/self.jacobian
        self.dzeta_dy = (self.dz_dxi*self.dx_deta-self.dx_dxi*self.dz_deta
                         )/self.jacobian
        self.dzeta_dz = (self.dx_dxi*self.dy_deta-self.dy_dxi*self.dx_deta
                         )/self.jacobian
        self.Dxi_Dt_vec = (
            self.dot_product((self.vels_x-self.dx_dt,self.vels_y-self.dy_dt,
                               self.vels_z-self.dz_dt),
                             (self.dxi_dx,self.dxi_dy,self.dxi_dz)),
            self.dot_product((self.vels_x-self.dx_dt,self.vels_y-self.dy_dt,
                               self.vels_z-self.dz_dt),
                             (self.deta_dx,self.deta_dy,self.deta_dz)),
            self.dot_product((self.vels_x-self.dx_dt,self.vels_y-self.dy_dt,
                               self.vels_z-self.dz_dt),
                             (self.dzeta_dx,self.dzeta_dy,self.dzeta_dz)))
        self.vels_xi_vec = (
            self.dot_product((self.vels_x,self.vels_y,self.vels_z),
                             (self.dxi_dx,self.dxi_dy,self.dxi_dz)),
            self.dot_product((self.vels_x,self.vels_y,self.vels_z),
                             (self.deta_dx,self.deta_dy,self.deta_dz)),
            self.dot_product((self.vels_x,self.vels_y,self.vels_z),
                             (self.dzeta_dx,self.dzeta_dy,self.dzeta_dz)))
        self.energy = (sympy.Rational(1,2)*
                       (self.vels_x**2+self.vels_y**2+self.vels_z**2) + 
                       self.pressure/((self.gamma-1)*self.density))
        self.grad_xi_vec = ((self.dxi_dx,self.dxi_dy,self.dxi_dz),
                            (self.deta_dx,self.deta_dy,self.deta_dz),
                            (self.dzeta_dx,self.dzeta_dy,self.dzeta_dz))
        self.fluxes = [self.cons()]+[self.flux(n) for n in range(3)]
        self.source = self.source_func()
#        out = (self.cons(),self.flux(0),self.flux(1),self.flux(2),self.source_func())
#        return out
    def cons(self):
        return sympy.Matrix([
            self.density*self.jacobian,
            self.density*self.jacobian*self.vels_x,
            self.density*self.jacobian*self.vels_y,
            self.density*self.jacobian*self.vels_z,
            self.density*self.jacobian*self.energy,
            self.dx_dxi,self.dy_dxi,self.dz_dxi,
            self.dx_deta,self.dy_deta,self.dz_deta,
            self.dx_dzeta,self.dy_dzeta,self.dz_dzeta,
            self.dx_dt,self.dy_dt,self.dz_dt,
            self.x,self.y,self.z])
    def flux(self,n):
        out =  [self.jacobian*(self.density*self.Dxi_Dt_vec[n]),
                self.jacobian*(self.density*self.Dxi_Dt_vec[n]*self.vels_x+
                               self.grad_xi_vec[n][0]*self.pressure),
                self.jacobian*(self.density*self.Dxi_Dt_vec[n]*self.vels_y+
                               self.grad_xi_vec[n][1]*self.pressure),
                self.jacobian*(self.density*self.Dxi_Dt_vec[n]*self.vels_z+
                               self.grad_xi_vec[n][2]*self.pressure),
                self.jacobian*(self.density*self.Dxi_Dt_vec[n]*self.energy+
                          self.vels_xi_vec[n]*self.pressure),
                0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        out[5:8] = [item*sympy.Integer(-1*(1-n)*(1-n/2)) for item in 
                    (self.dx_dt,self.dy_dt,self.dz_dt)]
        out[8:11] = [item*sympy.Integer(-1*(n)*(2-n)) for item in 
                     (self.dx_dt,self.dy_dt,self.dz_dt)]
        out[11:14] = [item*sympy.Integer(-1*(n-1)*(n/2)) for item in 
                      (self.dx_dt,self.dy_dt,self.dz_dt)]
        return sympy.Matrix(out)
    def source_func(self):
        return sympy.Matrix([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                self.dx_dt,self.dy_dt,self.dz_dt])

def unsteady_Euler(case):
    cases = {'simple':simple_case,
             'two_shock':two_shock_case,
#             'one_shock':one_shock_case,
             'normal':normal_case,
             'riemann_problem':riemann_problem_case}
    out = {'vars':[t,xi,eta,zeta],'eqn_kwargs':{}}
    out.update(cases[case]())
    return out

def simple_case():
    return {'sol':sympy.Matrix([1,1,1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0]),
            'discontinuities':[]}

def normal_case():
    theta = sympy.pi*.25
    S = (sympy.cos(theta)*xi+sympy.sin(theta)*eta)/t
    shock_speed = .78931
    p1 = 460.894
    d1 = 5.99924
    umag1 = 19.5975
    M1rel = (umag1-shock_speed)/(gamma*p1/d1)**(.5)
    p2 = ((2.*gamma*M1rel**2-(gamma-1))/(gamma+1))*p1
    d2 = ((gamma+1.)*M1rel**2/((gamma-1.)*M1rel**2+2.))*d1
    umag2 = (1-d1/d2)*shock_speed+umag1*d1/d2
    print "p2,d2,u2 = ",p2,d2,umag2
    u1 = umag1*sympy.cos(theta)
    v1 = umag1*sympy.sin(theta)
    u2 = umag2*sympy.cos(theta)
    v2 = umag2*sympy.sin(theta)
    speeds = [shock_speed]
    states = [sympy.Matrix([p1,d1,u1,v1]),sympy.Matrix([p2,d2,u2,v2])]
    base_state = [0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0]
    out = {'sol':sympy.Matrix(list(states[0]+
                                   H(S-speeds[0])*(states[1]-states[0]))+
                              base_state),
           'discontinuities':[S-speed for speed in speeds]}
    return out

def two_shock_case():
    speeds = [0.78959391926443701,8.6897744116323814,12.250778123084338]
    phi, theta = 0.,sympy.pi*.1#sympy.pi*.5, sympy.pi*.25
    S = (sympy.cos(theta)*xi+
         sympy.sin(theta)*sympy.cos(phi)*eta+
         sympy.sin(theta)*sympy.sin(phi)*zeta)/t
    yz_rotation_matrix = sympy.Matrix(
        [[sympy.cos(theta),0,0],
         [sympy.sin(theta)*sympy.cos(phi),0,0],
         [sympy.sin(theta)*sympy.sin(phi),0,0]])
    
#    S = yz_rotation_matrix.dot(sympy.Matrix([xi,eta,zeta]))[0]/t
    states = [sympy.Matrix([460.89400000000001,5.99924000000000000004,
                            19.597500000000000,0.,0.]),
              sympy.Matrix([1691.6469553991260,14.282349951978405,
                            8.6897744116323814,0.,0.]),
              sympy.Matrix([1691.6469553991260,31.042601641619882,
                            8.6897744116323814,0.,0.]),
              sympy.Matrix([46.09499999999999,5.99242000000000001,
                            -6.19632999999997,0.,0.])]
    for state in states:
        vel = sympy.Matrix([state[2],state[3],state[4]])
        new_vel = yz_rotation_matrix.dot(vel)
        state[2],state[3],state[4] = new_vel
    base_state = [1.,0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.,0.,0.,0.]
    out = {'sol':sympy.Matrix(
            list(
#                (1-H(S-speeds[0]))*states[0]+
#                H(S-speeds[0])*states[1])+base_state),
                (1-H(S-speeds[0]))*states[0]+
                H(S-speeds[0])*(1-H(S-speeds[1]))*states[1]+
                H(S-speeds[1])*(1-H(S-speeds[2]))*states[2]+
                H(S-speeds[2])*states[3])+base_state),
           'discontinuities':[S-speed for speed in speeds]}
    return out

def riemann_problem_case():
    n = 4
    theta, phi = sympy.pi*.5, 0.
    tests = riemann_problem_init()
    states,speeds = ([sympy.Matrix(state) for state in tests[n]['states']],
                     tests[n]['speeds'])
    S = (sympy.cos(theta)*xi+
         sympy.sin(theta)*sympy.cos(phi)*eta+
         sympy.sin(theta)*sympy.sin(phi)*zeta)/t
    fan_state_L = inside_fan_state(states[0],speeds[1],speeds[0],S)
    fan_state_R = inside_fan_state(states[3],speeds[3],speeds[4],S)
    states.insert(1,fan_state_L)
    states.insert(-1, fan_state_R)
    yz_rotation_matrix = sympy.Matrix(
        [[sympy.cos(theta),0,0],
         [sympy.sin(theta)*sympy.cos(phi),0,0],
         [sympy.sin(theta)*sympy.sin(phi),0,0]])
    for state in states:
        vel = sympy.Matrix([state[2],state[3],state[4]])
        new_vel = yz_rotation_matrix.dot(vel)
        state[2],state[3],state[4] = new_vel
    base_state = [1.,0.,0.,0.,1.,0.,0.,0.,1.,0.,0.,0.,0.,0.,0.]
    
    prims = map(list,zip(*states))
    sol_list = []
    for i, prim in enumerate(prims):
        piecewise_args = []
        piecewise_args.append((prim[0],S<speeds[0]))
        if speeds[1] != speeds[0]: 
            piecewise_args.append((prim[1],S<speeds[1]))
        piecewise_args.append((prim[2],S<speeds[2]))
        piecewise_args.append((prim[3],S<speeds[3]))
        if speeds[4] != speeds[3]:
            piecewise_args.append((prim[4],S<speeds[4]))
        piecewise_args.append((prim[5],True))
        sol_list.append(sympy.Piecewise(*piecewise_args))
    solution_state = sol_list+base_state
    out = {'sol':sympy.Matrix(solution_state),
           'discontinuities':[S-speed for speed in speeds]}
#    import matplotlib.pyplot as plt
#    from mpl_toolkits.mplot3d import Axes3D
#    fig = plt.figure()
#    ax = fig.add_subplot(111,projection='3d')
#    Axes3D.plot_surface(X,Y,Z)
    return out

def inside_fan_state(upwind,head,tail,S):
    if head > tail: 
        plusminus = -1
    else:
        if head < tail:
            plusminus = 1
        else:
            return upwind
    
    p = upwind[0]*(2/(gamma+1)-plusminus*(gamma-1)/(
            (gamma+1)*sympy.sqrt(gamma*upwind[0]/upwind[1]))*(
            upwind[2]-S))**((2*gamma)/(gamma-1))
    d = upwind[1]*(2./(gamma+1)-plusminus*(gamma-1.)/(
            (gamma+1)*sympy.sqrt(gamma*upwind[0]/upwind[1]))*(upwind[2]-S)
            )**(2./(gamma-1.))
    u = 2/(gamma+1)*((gamma-1)*.5*upwind[2]+S
                     -plusminus*sympy.sqrt(gamma*upwind[0]/upwind[1]))
    return sympy.Matrix([p,d,u,upwind[3],upwind[4]])

def riemann_problem_init():
    tests = []
    tests.append({})
    tests[0]['states'] = [
        [1., 1., 0., 0., 0.],
        [0.30313017805064679, 0.42631942817849516, 0.92745262004894879, 0., 0.],
        [0.30313017805064679, 0.26557371170530708, 0.92745262004894879, 0., 0.],
        [.1, .125, 0., 0., 0.]]
    tests[0]['speeds'] = [-1.1832159566199232, -7.02728125611844501E-002,
                           0.92745262004894879, 1.7521557320301779,
                           1.7521557320301779]
    tests.append({})
    tests[1]['states'] = [
        [.4, 1., -2., 0., 0.],
        [1.89387342005476107E-003, 2.18521182068128102E-002, 0., 0., 0.],
        [1.89387342005476107E-003, 2.18521182068128102E-002, 0., 0., 0.],
        [.4, 1., 2., 0., 0.]]
    tests[1]['speeds'] = [-2.7483314773547880, -0.34833147735478825,
                           0., 0.34833147735478825, 2.7483314773547880]
    tests.append({})
    tests[2] = {}
    tests[2]['states'] = [
        [1000., 1., 0., 0., 0.],
        [460.89378749138365, 0.57506229847655554, 19.597451388723059, 0., 0.],
        [460.89378749138365, 5.9992407047962342, 19.597451388723059, 0., 0.],
        [.01, 1., 0., 0., 0.]]
    tests[2]['speeds'] = [-37.416573867739416, -13.899632201271743,
                           19.597451388723059, 23.517536966903236,
                           23.517536966903236]
    tests.append({})
    tests[3]['states'] = [
        [.01, 1., 0., 0., 0.],
        [46.095044248867971, 5.9924168635152260, -6.1963282497870367, 0., 0.],
        [46.095044248867971, 0.57511278978241231, -6.1963282497870367, 0., 0.],
        [100., 1., 0., 0., 0.]]
    tests[3]['speeds'] = [-7.4374762586943133, -7.4374762586943133,
                           -6.1963282497870367, 4.3965656664547872,
                           11.832159566199232]
    tests.append({})
    tests[4]['states'] = [
        [460.894, 5.99924, 19.5975, 0., 0.],
        [1691.6469553991260, 14.282349951978405, 8.6897744116323814, 0., 0.],
        [1691.6469553991260, 31.042601641619882, 8.6897744116323814, 0., 0.],
        [46.0950, 5.99242, -6.19633, 0., 0.]]
    tests[4]['speeds'] = [0.78959391926443701, 0.78959391926443701,
                           8.6897744116323814, 12.250778123084338,
                           12.250778123084338]
    return tests    

def MASA_with_pinned_bounds(ranges,nxes=(100,1,1),
                            dxis=(1.,1.,1.),x_origin=(0.,0.,0.)):
    ((x0,xn),(y0,yn),(z0,zn)) = ranges
    out = MASA_solution_full(ranges,nxes,dxis,x0=x_origin)
    out_vars = list(out['vars'])
    out_vars.remove(t)
    valmax = 2.
    pinning_eqn = (4.*valmax/(xn-x0)**2*
                   (-out_vars[0]**2+(xn+x0)*out_vars[0]-x0*xn))
    out['sol'] = sympy.Matrix(
        [sol*pinning_eqn + .01 for sol in out['sol'][0:5]]+out['sol'][5:])
    return out

def MASA_solution_full(ranges,nxes=(100,1,1),dxis=(1.,1.,1.),x0=(0.,0.,0.)):
    kwargs={'x0':1.1,
            'xx':-.5,'ax':2.,'fx':sympy.sin,'Lx':100.,
            'xy':0,'ay':2.,'fy':sympy.cos,'Ly':100.,
            'xz':0,'az':2.,'fz':sympy.cos,'Lz':100.,
            'xt':-.5,'at':2.,'ft':sympy.cos,'Lt':100.,
            'shock_strength':.1,'shock_position':50.}
    dxes = [1,1,1]
    for ind in range(3):
        try:
            dxes[ind] = float(ranges[ind][1]-ranges[ind][0])/(nxes[ind]-1)
        except(ZeroDivisionError):
            dxes[ind] = float(ranges[ind][1]-ranges[ind][0])/nxes[ind]
#    dxes = [float((range_[1]-range_[0]))/(nx-1)
#            for (range_,nx) in zip(ranges,nxes)]
    prims = [MASA_full_var(**kwargs) for var in range(5)]
    grid_vels = [0.*.25*vel for vel in prims[2:]]
    dx_dxi = dx_dxi_f(dx_dlambda=grid_vels,
                      dx_dxi_0=[dxes[0]/dxis[0],0.,0.,
                                0.,dxes[1]/dxis[1],0.,
                                0.,0.,dxes[2]/dxis[2]],t0=0.)
    xes = x_f(dx_dxi,grid_vels,x0,dxis)
    return {'vars':[t,xi,eta,zeta],
            'sol':sympy.Matrix(prims+dx_dxi+grid_vels+xes),
            'discontinuities':[],'eqn_kwargs':{}}

def dx_dxi_f(dx_dlambda,dx_dxi_0,t0):
    change = [0 for ind in range(9)]
    out = list(change)
    for inda in range(3):
        for indb in range(3):
            change[inda*3+indb] = sympy.integrate(sympy.diff(
                    dx_dlambda[indb],[xi,eta,zeta][inda]),t)
            out[inda*3+indb] = ( change[inda*3+indb] + dx_dxi_0[inda*3+indb] - 
                                 change[inda*3+indb].subs({t:t0}) )
    return out

def x_f(dx_dxi,dx_dlambda,x0,dxis):
    # Assumes a simple initial grid, where dx~dxi, dy~deta, dz~dzeta
    initial_xes = [dx_dxi[0]*xi+x0[0],dx_dxi[4]*eta+x0[1],dx_dxi[8]*zeta+x0[2]]
    initial_xes = [x.subs({t:0}) for x in initial_xes]
    out = [initial_xes[ind] + 
           sympy.integrate(dx_dlambda[ind],t) for ind in range(3)]
    return out


def MASA_full_var(x0,xx,ax,fx,Lx,xy,ay,fy,Ly,xz,az,fz,Lz,xt,at,ft,Lt,
                  shock_strength,shock_position):
    return (x0+
            xt*ft(at*sympy.pi*t/Lt)+
            xx*fx(ax*sympy.pi*xi/Lx)+
            xy*fy(ay*sympy.pi*eta/Ly)+
            xz*fz(az*sympy.pi*zeta/Lz)+
            shock_strength*(1 if xi > shock_position else 0))
            
if __name__ == "__main__":
    eqn = Euler_UCS(MASA_with_pinned_bounds([[0,1],[0,1],[0,1]],nxes=(100,1,1)))
    print eqn.balance_diff()[0]
    out = eqn.balance_lambda_init()
    import pdb;pdb.set_trace()
    
