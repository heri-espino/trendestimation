"""Exact selected inverse and conditional PLS scores for banded SPD systems.

For a finite penalty, factor A=I+lambda*D.T*D=L L.T with half-bandwidth d.
A Takahashi-style backward recursion obtains the *selected* inverse
entries (A^-1)[i,j], |i-j|<=d in O(n*d**2) arithmetic / O(n*d)
storage, without constructing A^-1. The diagonal is exactly the
conditional leverage h_ii for a fixed numerical mu.

This is a numerical algorithm, not an asymptotic/FFT approximation.
If finite precision invalidates the KKT or selected-inverse recurrence
the caller must mark the result invalid.
"""
from __future__ import annotations

from math import comb
from time import perf_counter

import numpy as np
from scipy.linalg import cho_solve_banded, cholesky_banded
from scipy.optimize import brentq
from scipy.sparse import diags

from trendestimation.solvers import _penalty_lower_bands


def selected_inverse(factor: np.ndarray) -> np.ndarray:
    """Selected upper inverse Z[k,i] = (A^-1)[i,i+k] from lower Cholesky.

    The factor has LAPACK lower-band storage factor[k,i]=L[i+k,i].
    No n-by-n dense matrix is formed; complexity O(n*d*d).
    """
    d = factor.shape[0]-1
    n = factor.shape[1]
    z = np.zeros((d+1,n),dtype=float)
    for i in range(n-1,-1,-1):
        end = min(n,i+d+1)
        inv_diag = 1.0 / factor[0,i]
        for j in range(i+1,end):
            total = 0.0
            for k in range(i+1,end):
                element = z[j-k,k] if k<=j else z[k-j,j]
                total += factor[k-i,i] * inv_diag * element
            z[j-i,i] = -total
        z[0,i] = inv_diag*inv_diag - sum(
            factor[k-i,i] * inv_diag * z[k-i,i]
            for k in range(i+1,end)
        )
    return z


def forward_difference(n:int,d:int):
    """Sparse D with the *same forward difference signs* as trendestimation."""
    return diags(
        [np.full(n-d,(-1.0)**(d-j)*comb(d,j)) for j in range(d+1)],
        list(range(d+1)),shape=(n-d,n),format="csc",
    )


class BandedTrace:
    """Data-independent structure for fixed (n,d), d=1..6 in this study."""

    def __init__(self,n:int,d:int):
        if not (isinstance(n,int) and isinstance(d,int) and
                n>=2 and 1<=d<=6 and d<n):
            raise ValueError("Require integer n>d with 1<=d<=6")
        self.n,self.d=n,d
        self.D=forward_difference(n,d)
        self.bands=_penalty_lower_bands(n,d)
        self.shift=np.asarray(self.D.T@np.ones(n-d)).reshape(n)
        self.factor_calls=0
        self.trace_calls=0

    def factor(self,lam:float):
        if not np.isfinite(lam) or lam<=0:
            raise ValueError("A finite positive lambda is required")
        ab=lam*self.bands.copy()
        ab[0]+=1.0
        if not np.all(np.isfinite(ab)):
            raise OverflowError("Penalty matrix overflow")
        L=cholesky_banded(ab,lower=True,check_finite=False,
                           overwrite_ab=True)
        self.factor_calls+=1
        return L

    def statistics(self,lam:float,*,factor=None,leverage:bool=False):
        """Return EDF and optionally exact diag(A^-1)."""
        L=self.factor(lam) if factor is None else factor
        z=selected_inverse(L)
        self.trace_calls+=1
        diagonal=z[0]
        if (not np.all(np.isfinite(diagonal)) or
                np.any(diagonal<=0) or np.any(diagonal>1+1e-7)):
            raise ArithmeticError("Selected inverse invalid")
        edf=float(np.sum(diagonal))
        if edf<self.d-1e-5 or edf>self.n+1e-5:
            raise ArithmeticError("EDF outside theoretical bounds")
        return edf,(diagonal if leverage else None)

    def smoothness(self,lam:float):
        if lam==0:
            return 0.0
        if np.isposinf(lam):
            return 1.0
        edf,_=self.statistics(lam)
        return float((self.n-edf)/(self.n-self.d))

    def lambda_for_s(self,s:float,tol:float=1e-8):
        """Invert normalized S numerically, with no dense eigensystem.

        A new bracket is needed for each inversion. This is O(k*n*d^2),
        which can be prohibitively expensive for very large grids.
        """
        s=float(s)
        if not 0<=s<=1 or not np.isfinite(s):
            raise ValueError("Smoothness must be in [0,1]")
        if s==0: return 0.0
        if s==1: return float("inf")
        def f(loglam):
            return self.smoothness(float(np.exp(loglam)))-s
        low,high=-16.,16.
        while f(low)>0 and low>-680:
            low-=16.
        while f(high)<0 and high<680:
            high+=16.
        if not f(low)<=0<=f(high):
            raise ArithmeticError("Could not bracket S: precision limit")
        root=brentq(f,low,high,xtol=tol,maxiter=100)
        lam=float(np.exp(root))
        recovered=self.smoothness(lam)
        if not np.isfinite(recovered) or abs(recovered-s)>max(5e-7,10*tol):
            raise ArithmeticError(f"Inaccurate S inversion: {s}, {recovered}")
        return lam

    def inverse_deficit_diagonal(self,lam:float,z:np.ndarray):
        """Evaluate 1-h_ii = lambda*(Q H)_ii without 1-diag(H) loss.

        Since Q has half-bandwidth d, only the selected inverse Z is used.
        """
        n,d=self.n,self.d
        b=np.zeros(n,float)
        for i in range(n):
            accum=self.bands[0,i]*z[0,i]
            for k in range(1,d+1):
                if i+k<n:
                    accum+=self.bands[k,i]*z[k,i]
                if i-k>=0:
                    accum+=self.bands[k,i-k]*z[k,i-k]
            b[i]=lam*accum
        return b

    def fit_stats(self,y:np.ndarray,lam:float,mu:float,criterion:str,*,
                  factor=None,selected=None):
        """Calculate actual criterion, including necessary fit and traces.

        Timing of the method-specific fit is separate in the experiment
        runner. Here the complete *banded* criterion pipeline is timed.
        Scores with data-dependent mu are deliberately unsupported except
        conditional plug-in MLE, matching the public library API.
        """
        y=np.asarray(y,dtype=float)
        if y.shape!=(self.n,) or not np.all(np.isfinite(y)):
            raise ValueError("Invalid observations")
        if criterion not in ("cv","gcv","aicc","bic","mle"):
            raise ValueError("Unknown criterion")
        if not np.isfinite(mu):
            raise ValueError("mu must be a finite scalar")
        if lam==0:
            return dict(score=float("inf"),valid=True,edf=float(self.n),
                        factor_s=0.,solve_s=0.,diagnostics_s=0.,
                        selected_s=0.0,backward_error=0.)
        if np.isposinf(lam):
            return self._limit(y,mu,criterion)
        t0=perf_counter()
        L=self.factor(lam) if factor is None else factor
        t1=perf_counter()
        rhs=y+(lam*mu)*self.shift
        tau=cho_solve_banded((L,True),rhs,check_finite=False)
        t2=perf_counter()
        dy=np.asarray(self.D@tau).ravel()
        residual=lam*np.asarray(self.D.T@(dy-mu)).ravel()
        diff=y-tau
        back=float(np.linalg.norm(diff-residual)/
                   max(1.,np.linalg.norm(y),np.linalg.norm(rhs)))
        if not np.all(np.isfinite(tau)) or not np.isfinite(back) or back>1e-7:
            raise ArithmeticError(f"PLS KKT failed: backward_error={back}")
        z=selected_inverse(L) if selected is None else selected
        if selected is None:
            self.trace_calls+=1
        edf=float(np.sum(z[0]))
        if not self.d-1e-5<=edf<=self.n+1e-5:
            raise ArithmeticError("Invalid banded EDF")
        s=float((self.n-edf)/(self.n-self.d))
        # Direct residual is less cancellation-sensitive at lambda~0 than y-tau.
        rss=float(residual@residual)
        n=self.n
        if criterion=="cv":
            denominator=self.inverse_deficit_diagonal(lam,z)
            if np.any(denominator<=0) or not np.all(np.isfinite(denominator)):
                raise ArithmeticError("LOOCV leverage denominator invalid")
            score=float(np.mean((residual/denominator)**2))
        elif criterion=="gcv":
            den=1-edf/n
            score=float((rss/n)/(den*den)) if den>1e-10 else float("inf")
        elif criterion in ("bic","aicc"):
            # Same finite-RSS convention as public library; note BIC is
            # mathematically unbounded below as S->0+, independently.
            eps=np.finfo(float).eps*max(1.,float(y@y))
            if rss<=eps:
                score=float("inf")
            else:
                base=float(np.log(rss/n))
                if criterion=="bic":
                    score=base+edf*np.log(n)/n
                else:
                    den=n-edf-2.
                    score=(base+(2*edf+1)/den
                           if den>0 else float("inf"))
        else:
            # Profiled marginal Gaussian likelihood up to the
            # lambda-INDEPENDENT constant -log det(D D.T).
            # The dual weighted quadratic avoids enormous p_mu(t).
            m=n-self.d
            gram=np.zeros((self.d+1,m),dtype=float)
            for k in range(self.d+1):
                gram[k,:m-k]=(-1)**k*comb(2*self.d,self.d-k)
            gram[0]+=1/lam
            fdual=cholesky_banded(gram,lower=True,check_finite=False)
            e=np.asarray(self.D@y).ravel()-mu
            v=cho_solve_banded((fdual,True),e,check_finite=False)
            weighted=float(e@v)
            if weighted<=0 or not np.isfinite(weighted):
                raise ArithmeticError("Marginal likelihood quadratic invalid")
            logdetA=2.*float(np.log(L[0]).sum())
            # omit logdet(D D.T), common across all positive lambdas.
            score=(m*np.log(weighted/m)+logdetA-m*np.log(lam))
        t3=perf_counter()
        if np.isnan(score):
            raise ArithmeticError("Criterion returned NaN")
        return dict(score=score,valid=True,edf=edf,factor_s=t1-t0,
                    solve_s=t2-t1,diagnostics_s=t3-t2,
                    selected_s=s,backward_error=back)


    def score_external(self,y,tau,lam,mu,criterion,*,factor=None,selected=None):
        """Score an external backend fit using exact banded conditional diagnostics.

        A hybrid method explicitly pays for its own fit *and* the banded
        Cholesky selected-inverse trace/leverage/likelihood diagnostics.
        No expensive computation is silently borrowed from the baseline.
        """
        y=np.asarray(y,dtype=float)
        tau=np.asarray(tau,dtype=float)
        if y.shape!=(self.n,) or tau.shape!=(self.n,):
            raise ValueError("Invalid external fit dimension")
        if lam==0:
            return float("inf")
        if np.isposinf(lam):
            return self._limit(y,mu,criterion)["score"]
        L=self.factor(lam) if factor is None else factor
        z=selected_inverse(L) if selected is None else selected
        edf=float(np.sum(z[0]))
        if not self.d-1e-5<=edf<=self.n+1e-5:
            raise ArithmeticError("External criterion invalid EDF")
        dy=np.asarray(self.D@tau).ravel()
        residual=lam*np.asarray(self.D.T@(dy-mu)).ravel()
        rhs=y+lam*mu*self.shift
        back=float(np.linalg.norm(y-tau-residual)/
                   max(1.,np.linalg.norm(y),np.linalg.norm(rhs)))
        if not np.isfinite(back) or back>1e-7:
            raise ArithmeticError(f"External fit fails PLS KKT: {back}")
        rss=float(residual@residual)
        n=self.n
        if criterion=="cv":
            denominator=self.inverse_deficit_diagonal(lam,z)
            if np.any(denominator<=0) or not np.all(np.isfinite(denominator)):
                raise ArithmeticError("External LOOCV diagonal invalid")
            score=float(np.mean((residual/denominator)**2))
        elif criterion=="gcv":
            den=1-edf/n
            score=(rss/n)/(den*den) if den>1e-10 else float("inf")
        elif criterion in ("bic","aicc"):
            eps=np.finfo(float).eps*max(1.,float(y@y))
            if rss<=eps:
                score=float("inf")
            else:
                base=float(np.log(rss/n))
                if criterion=="bic":
                    score=base+edf*np.log(n)/n
                else:
                    den=n-edf-2.
                    score=(base+(2*edf+1)/den
                           if den>0 else float("inf"))
        elif criterion=="mle":
            m=n-self.d
            gram=np.zeros((self.d+1,m),dtype=float)
            for k in range(self.d+1):
                gram[k,:m-k]=(-1)**k*comb(2*self.d,self.d-k)
            gram[0]+=1/lam
            fdual=cholesky_banded(gram,lower=True,check_finite=False)
            e=np.asarray(self.D@y).ravel()-mu
            v=cho_solve_banded((fdual,True),e,check_finite=False)
            weighted=float(e@v)
            if weighted<=0 or not np.isfinite(weighted):
                raise ArithmeticError("External MLE quadratic invalid")
            score=(m*np.log(weighted/m)+
                   2.*float(np.log(L[0]).sum())-m*np.log(lam))
        else:
            raise ValueError("Unknown criterion")
        if np.isnan(score):
            raise ArithmeticError("External criterion returned NaN")
        return float(score)

    def _limit(self,y,mu,criterion):
        """Analytical S=1 projection; validate numerical difference constraint."""
        n,d=self.n,self.d
        t=np.arange(n,dtype=float)
        from scipy.special import binom
        p=mu*binom(t,d)
        if not np.all(np.isfinite(p)):
            raise ArithmeticError("Infinite-penalty polynomial overflow")
        basis=np.polynomial.legendre.legvander(np.linspace(-1,1,n),d-1)
        U,_=np.linalg.qr(basis,mode="reduced")
        tau=p+U@(U.T@(y-p))
        residual=y-tau
        error=float(np.linalg.norm(self.D@tau-mu) /
                    max(1.,abs(mu)*np.sqrt(n-d)))
        if not np.isfinite(error) or error>1e-6:
            raise ArithmeticError(f"S=1 polynomial constraint inaccurate: {error}")
        rss=float(residual@residual)
        if criterion=="cv":
            b=1-np.sum(U*U,axis=1)
            score=float(np.mean((residual/b)**2))
        elif criterion=="gcv":
            score=(rss/n)/(1-d/n)**2
        elif criterion=="mle":
            score=((n-d)*np.log(rss/(n-d))
                   if rss>0 else float("inf"))
        elif criterion=="bic":
            score=(np.log(rss/n)+d*np.log(n)/n
                   if rss>0 else float("inf"))
        else:
            score=(np.log(rss/n)+(2*d+1)/(n-d-2)
                   if rss>0 and n-d>2 else float("inf"))
        return dict(score=float(score),valid=True,edf=float(d),
                    factor_s=0.,solve_s=0.,diagnostics_s=0.,
                    selected_s=1.0,backward_error=error)
