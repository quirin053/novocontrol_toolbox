import numpy as np
import pandas as pd

def leitfaehigkeit_reihe(g, t):
    if not isinstance(g, list | tuple):
        raise TypeError(
            f"g: list or tuple expected, got '{type(g).__name__}'"
        )
    if not isinstance(t, list | tuple):
        raise TypeError(
            f"t: list or tuple expected, got '{type(t).__name__}'"
        )
    if len(g) != len(t):
        raise ValueError(
            f"Lists must have the same length, got g: {len(g)} and t: {len(t)}"
        )
    if isinstance(g[0], pd.Series):
        # g = [pd.Series, pd.Series, ...]
        for i in g:
            if not isinstance(i, pd.Series):
                raise TypeError(
                    f"g: list of Pandas.Series expected, got '{type(i).__name__}'"
                )
        gsout = pd.Series(index=g[0].index)
        for i in g[0].index:
            gsout[i] = sum(t)/(sum(np.array(t)/np.array([j[i] for j in g])))
        return gsout
    
    return sum(t)/(sum(np.array(t)/np.array(g)))

def leitwert_reihe(G):
    # G_ges = 1/(1/G1 + 1/G2 + 1/G3 + ...)
    if not isinstance(G, list | tuple):
        raise TypeError(
            f"list or tuple expected, got '{type(G).__name__}'"
        )
    if 0 in G:
        return 0
    return 1/np.sum(1/np.array(G))

def permittivity_series(e, t):
    # e_ges = tges/(t1/e1 + t2/e2 + t3/e3 + ...)
    if not isinstance(e, list | tuple):
        raise TypeError(
            f"e: list or tuple expected, got '{type(e).__name__}'"
        )
    if not isinstance(t, list | tuple):
        raise TypeError(
            f"t: list or tuple expected, got '{type(t).__name__}'"
        )
    if len(e) != len(t):
        raise ValueError(
            f"Lists must have the same length, got e: {len(e)} and t: {len(t)}"
        )
    if isinstance(e[0], pd.Series):
        # e = [pd.Series, pd.Series, ...]
        for i in e:
            if not isinstance(i, pd.Series):
                raise TypeError(
                    f"e: list of Pandas.Series expected, got '{type(i).__name__}'"
                )
        epsout = pd.Series(index=e[0].index)
        for i in e[0].index:
            epsout[i] = sum(t)/(sum(np.array(t)/np.array([j[i] for j in e])))
        return epsout



    return sum(t)/sum(np.array(t)/np.array(e))

if __name__ == "main":
    print("This is a module")