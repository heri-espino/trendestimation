"""Small deterministic algebra regression for the manuscript's KKT derivation.

No numerical experiment, benchmark loop or smoothing-parameter selection.
These tests verify exact PLS identities for finite lambda values.
"""
from __future__ import annotations

import unittest
import numpy as np


class PLSOptimalityIdentity(unittest.TestCase):
    def setUp(self):
        n,d=8,3
        self.D=np.diff(np.eye(n),n=d,axis=0)
        self.y=np.array([.12,1.4,-.8,.9,.6,-.5,1.5,.2])
        self.mu=-.35
        self.ones=np.ones(n-d)

    def data(self,lam):
        D,y,mu=self.D,self.y,self.mu
        A=np.eye(y.size)+lam*(D.T@D)
        b=y+lam*mu*(D.T@self.ones)
        optimum=np.linalg.solve(A,b)
        return A,b,optimum

    def objective(self,tau,lam):
        return float(np.dot(self.y-tau,self.y-tau)
                     +lam*np.linalg.norm(self.D@tau-self.mu*self.ones)**2)

    def test_gradient_and_residual_are_exact_negatives(self):
        for lam in (0.,.2,1.0,1000.):
            with self.subTest(lam=lam):
                A,b,opt=self.data(lam)
                computed=opt+np.linspace(-.01,.03,len(opt))
                residual=(self.y-computed)-lam*self.D.T@(self.D@computed-self.mu*self.ones)
                gradient=2*((computed-self.y)
                            +lam*self.D.T@(self.D@computed-self.mu*self.ones))
                np.testing.assert_allclose(residual,b-A@computed,rtol=0,atol=3e-12)
                np.testing.assert_allclose(residual,-.5*gradient,rtol=0,atol=3e-12)

    def test_positive_definite_and_objective_gap_identity(self):
        for lam in (0.,.2,1.0,1000.):
            with self.subTest(lam=lam):
                A,b,opt=self.data(lam)
                self.assertGreaterEqual(np.linalg.eigvalsh(A).min(),1.-1e-12)
                computed=opt+np.linspace(-.01,.03,len(opt))
                r=b-A@computed
                gap=self.objective(computed,lam)-self.objective(opt,lam)
                np.testing.assert_allclose(gap,r@np.linalg.solve(A,r),rtol=1e-8,atol=1e-11)
                self.assertLessEqual(gap,np.linalg.norm(r)**2+1e-9)
                self.assertLessEqual(np.linalg.norm(computed-opt),np.linalg.norm(r)+1e-10)

    def test_scaled_acceptance_is_not_normwise_backward_error(self):
        A,b,opt=self.data(2.0)
        computed=opt+np.linspace(-.1,.1,len(opt))
        r=b-A@computed
        eta_opt=np.linalg.norm(r)/max(1.,np.linalg.norm(self.y),np.linalg.norm(b))
        eta_lin=np.linalg.norm(r)/(np.linalg.norm(A,2)*np.linalg.norm(computed)+np.linalg.norm(b))
        self.assertGreater(eta_opt,0)
        self.assertGreater(eta_lin,0)
        self.assertGreater(abs(eta_opt-eta_lin),1e-6)


if __name__=="__main__":
    unittest.main()
