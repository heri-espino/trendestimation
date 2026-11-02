"""Sparse, banded-LU and iterative *fit-only* PLS solvers.

The CHOLMOD backend requires optional scikit-sparse. SciPy splu is sparse
LU, not Cholesky. FFT and DST are approximate preconditioners only.
"""
from __future__ import annotations

from math import comb
import numpy as np
from scipy.fft import dst, idst
from scipy.linalg import solve_banded
from scipy.sparse import diags, eye as sparse_eye
from scipy.sparse.linalg import LinearOperator, cg, splu


def _sparse_difference(n, d):
    return diags(
        [np.full(n-d, (-1.0)**(d-j)*comb(d,j)) for j in range(d+1)],
        list(range(d+1)), shape=(n-d,n), format="csc",
    )


def _bytes(mat):
    return 0 if mat is None else int(
        mat.data.nbytes + mat.indices.nbytes + mat.indptr.nbytes
    )


class StructuredSystem:
    """Prepared matrices for multiple fits; never returns EDF or CV itself."""

    METHODS = ("banded_lu", "sparse_lu", "sparse_cholesky", "pcg")

    def __init__(self, n, d, method, *, preconditioner="fft",
                 cg_rtol=1e-9, cg_maxiter=None, factor_cache=False):
        if method not in self.METHODS:
            raise ValueError("Unknown structured method")
        if preconditioner not in ("fft","dst","jacobi","none"):
            raise ValueError("preconditioner must be fft, dst, jacobi or none")
        if not np.isfinite(cg_rtol) or not 0 < cg_rtol < 1:
            raise ValueError("cg_rtol must lie in (0,1)")
        if cg_maxiter is not None and (
                isinstance(cg_maxiter, (bool,np.bool_)) or
                not isinstance(cg_maxiter, (int,np.integer)) or cg_maxiter < 1):
            raise ValueError("cg_maxiter must be positive or None")
        if factor_cache and method not in ("sparse_lu","sparse_cholesky"):
            raise ValueError("factor_cache supports sparse direct methods only")
        self.n, self.d, self.method = n,d,method
        self.preconditioner, self.cg_rtol = preconditioner, cg_rtol
        self.cg_maxiter, self.factor_cache = cg_maxiter, factor_cache
        self._factors = {}
        self.last_iterations = None
        self.last_relative_residual = None
        self.D = _sparse_difference(n,d)
        self.Q = None
        self.bands = None
        self.diagonal_Q = None
        if method in ("sparse_lu","sparse_cholesky","banded_lu"):
            self.Q = (self.D.T @ self.D).tocsc()
            if method == "sparse_cholesky":
                try:
                    from sksparse.cholmod import cholesky
                except ImportError as exc:
                    raise ImportError(
                        "Sparse Cholesky requires optional scikit-sparse "
                        "(SuiteSparse CHOLMOD); SciPy sparse LU is different."
                    ) from exc
                self.cholmod = cholesky
            if method == "banded_lu":
                self.bands = np.zeros((2*d+1,n),float)
                coo = self.Q.tocoo()
                self.bands[d+coo.row-coo.col,coo.col] = coo.data
        else:
            self.diagonal_Q = np.asarray(self.D.power(2).sum(axis=0)).ravel()
        self.mean_shift = np.asarray(self.D.T @ np.ones(n-d)).ravel()

    @property
    def stored_bytes(self):
        # Excludes opaque factor allocations internal to SuperLU/CHOLMOD.
        return sum((_bytes(self.D),_bytes(self.Q),self.mean_shift.nbytes,
                    0 if self.bands is None else self.bands.nbytes,
                    0 if self.diagonal_Q is None else self.diagonal_Q.nbytes))

    @property
    def cached_factor_count(self):
        return len(self._factors)

    def solve(self, y, lam, mu):
        if not (np.isfinite(lam) and lam > 0):
            raise ValueError("Finite positive lambda required")
        rhs = y + (lam*mu)*self.mean_shift
        if not np.all(np.isfinite(rhs)):
            raise OverflowError("Nonfinite right-hand side")
        self.last_iterations = self.last_relative_residual = None
        if self.method == "banded_lu":
            ab = lam*self.bands.copy()
            ab[self.d] += 1.0
            x = solve_banded((self.d,self.d),ab,rhs,check_finite=False)
        elif self.method in ("sparse_lu","sparse_cholesky"):
            factor = self._factors.get(lam)
            if factor is None:
                A = sparse_eye(self.n,format="csc") + lam*self.Q
                if not np.all(np.isfinite(A.data)):
                    raise OverflowError("Sparse matrix overflow")
                factor = (splu(A,permc_spec="NATURAL")
                          if self.method == "sparse_lu" else self.cholmod(A))
                if self.factor_cache:
                    self._factors[lam] = factor
            x = factor.solve_A(rhs) if self.method=="sparse_cholesky" else factor.solve(rhs)
        else:
            D = self.D
            A = LinearOperator((self.n,self.n),
                matvec=lambda v: v + lam*(D.T @ (D @ v)),dtype=float)
            if self.preconditioner=="fft":
                k=np.arange(self.n)
                eig=(2*np.sin(np.pi*k/self.n))**(2*self.d)
                inv=1/(1+lam*eig)
                M=LinearOperator(A.shape,
                    matvec=lambda v:np.fft.ifft(np.fft.fft(v)*inv).real,
                    dtype=float)
            elif self.preconditioner=="dst":
                k=np.arange(1,self.n+1)
                eig=(2*np.sin(np.pi*k/(2*(self.n+1))))**(2*self.d)
                inv=1/(1+lam*eig)
                M=LinearOperator(A.shape,
                    matvec=lambda v:idst(dst(v,type=1,norm="ortho")*inv,
                                             type=1,norm="ortho"),dtype=float)
            elif self.preconditioner=="jacobi":
                inv=1/(1+lam*self.diagonal_Q)
                M=LinearOperator(A.shape,matvec=lambda v:inv*v,dtype=float)
            else:
                M=None
            it=[0]
            def cb(_):
                it[0]+=1
            maxiter = int(self.cg_maxiter) if self.cg_maxiter is not None else 10*self.n
            try:
                x, info=cg(A,rhs,M=M,rtol=self.cg_rtol,atol=0.0,
                           maxiter=maxiter,callback=cb)
            except TypeError:
                # Compatible with SciPy 1.9--1.11.
                x, info=cg(A,rhs,M=M,tol=self.cg_rtol,atol=0.0,
                           maxiter=maxiter,callback=cb)
            self.last_iterations=it[0]
            self.last_relative_residual=float(
                np.linalg.norm(rhs-A@x)/max(np.linalg.norm(rhs),1e-300))
            if info != 0 or self.last_relative_residual > max(5*self.cg_rtol,5e-13):
                raise ArithmeticError(
                    f"PCG did not converge: info={info}, iterations={it[0]}, "
                    f"relative_residual={self.last_relative_residual:.3e}")
        x=np.asarray(x,dtype=float).reshape(self.n)
        if not np.all(np.isfinite(x)):
            raise ArithmeticError("Nonfinite structured fit")
        return x
