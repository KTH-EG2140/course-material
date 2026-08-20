# n1 check skript v2 FINAL_new (funkar!!)  /L
# kör från repo root:  python awful_screener.py
from pandas import *
from pandapower import *
import pandapower as pp

L = []
d = "data/svedala"
b = read_csv(d+"/buses.csv",index_col=0)
l = read_csv(d+"/lines.csv",index_col=0)
t = read_csv(d+"/transformers.csv",index_col=0)
g = read_csv(d+"/generators.csv",index_col=0)
ld = read_csv(d+"/loads.csv",index_col=0)
n = pp.create_empty_network()
for i,r in b.iterrows():
    pp.create_bus(n,vn_kv=r.vn_kv,name=r["name"],zone=r.SubGeographicalRegion_name,in_service=r.in_service,index=i)
for i,r in l.iterrows():
    v = n.bus.at[r.from_bus,"vn_kv"]
    if v==400.0:
        m=2.0
    else:
        if v==220.0:
            m=1.0
        else:
            if v==135.0:
                m=0.9
            else:
                m=0.5
    if str(r.max_i_ka)!="nan":
        m=r.max_i_ka
    pp.create_line_from_parameters(n,from_bus=r.from_bus,to_bus=r.to_bus,length_km=r.length_km,r_ohm_per_km=r.r_ohm_per_km,x_ohm_per_km=r.x_ohm_per_km,c_nf_per_km=r.c_nf_per_km,max_i_ka=m,name=r["name"],in_service=r.in_service,index=i)
for i,r in t.iterrows():
    pp.create_transformer_from_parameters(n,hv_bus=r.hv_bus,lv_bus=r.lv_bus,sn_mva=r.sn_mva,vn_hv_kv=r.vn_hv_kv,vn_lv_kv=r.vn_lv_kv,vk_percent=r.vk_percent,vkr_percent=r.vkr_percent,pfe_kw=r.pfe_kw,i0_percent=r.i0_percent,shift_degree=r.shift_degree,name=r["name"],in_service=r.in_service,index=i)
for i,r in g.iterrows():
    pp.create_gen(n,bus=r.bus,p_mw=r.p_mw,vm_pu=r.vm_pu,sn_mva=r.sn_mva,min_q_mvar=r.min_q_mvar,max_q_mvar=r.max_q_mvar,slack=r.slack,name=r["name"],in_service=r.in_service,index=i)
for i,r in ld.iterrows():
    pp.create_load(n,bus=r.bus,p_mw=r.p_mw,q_mvar=r.q_mvar,name=r["name"],in_service=r.in_service,index=i)
print("natet klart", len(n.bus))
x = list(n.line.index)
for i in range(len(x)):
    j = x[i]
    if n.line.at[j,"in_service"]==True:
        n.line.at[j,"in_service"]=False
        try:
            pp.runpp(n)
            w = n.res_line.loading_percent.max()
            v2 = 0
            for k in n.res_line.index:
                if n.res_line.at[k,"loading_percent"]>100.0:
                    v2 = v2+1
            L.append((j,n.line.at[j,"name"],w,v2))
            if v2>0:
                print("DANGER!!",n.line.at[j,"name"],w,v2)
            else:
                print("ok",n.line.at[j,"name"],w)
            n.line.at[j,"in_service"]=True
        except:
            pass
print("klart, worst:")
tmp = 0
tmp2 = ""
for i in range(len(L)):
    if L[i][2]>tmp:
        tmp = L[i][2]
        tmp2 = L[i][1]
print(tmp2, tmp)
