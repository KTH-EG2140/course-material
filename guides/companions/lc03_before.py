# zone report v3 (fixad)  -- what is wrong with this file? (LC3 live refactor)
import pandas as pd

def f(x):
    d = pd.read_csv("data/svedala/loads.csv",index_col=0)
    d2 = pd.read_csv("data/svedala/buses.csv",index_col=0)
    r = {}
    for i in d.index:
        try:
            z = d2.at[d.at[i,"bus"],"SubGeographicalRegion_name"]
            if z in r:
                r[z] = r[z]+d.at[i,"p_mw"]*x
            else:
                r[z] = d.at[i,"p_mw"]*x
        except:
            pass
    for k in r:
        print(k, r[k])
    return r

f(1)
