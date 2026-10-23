import json,glob,statistics,collections,sys
base=sys.argv[1]
miles={}
for f in glob.glob(base+"/timeline_*.json"):
    for l in json.load(open(f)).get("loads",[]):
        if l.get("routeMiles") is not None: miles[l["loadId"]]=l["routeMiles"]
loads=[];rev=0;tw=0;tn=0;trw=0
for f in glob.glob(base+"/detail_*.json"):
    d=json.load(open(f)); fee=(d["derivedFeePercent"] or d["configuredFeePercent"])/100
    rev+=d["metrics"]["totalRevenue"]; t=d["timingMetrics"]
    tw+=t["avgPostedToDeliveredHours"]*t["sampleSize"]; trw+=t["avgTransitHours"]*t["sampleSize"]; tn+=t["sampleSize"]
    for l in d["loads"]:
        l["store"]=d["companyName"]; l["miles"]=miles.get(l["loadId"]); l["allin"]=l["price"]*(1+fee); loads.append(l)
vm=sum(l["miles"]*l["vinCount"] for l in loads)
vins=sum(l["vinCount"] for l in loads)
uv=len({v["vin"] for l in loads for v in l["vehicles"]})
print("loads",len(loads),"vins",vins,"unique vins",uv)
print("allin spend (metrics.totalRevenue)",round(rev,2),"veh-miles",vm,"=> $/veh-mi",round(rev/vm,3))
per=[l["allin"]/l["miles"]/l["vinCount"] for l in loads if l["miles"]]
print("median per-load $/veh-mi (approx allin)",round(statistics.median(per),3),"simple mean",round(statistics.mean(per),3))
print("avg posted->delivered days",round(tw/tn/24,2),"n",tn,"| avg transit days",round(trw/tn/24,2))
print("avg miles/load",round(statistics.mean(l["miles"] for l in loads)),"median",statistics.median(l["miles"] for l in loads))
states=collections.Counter()
for l in loads:
    for k in ("origin","destination"):
        states[l[k].split(", ")[-1].strip()]+=1
print("states",len(states),sorted(states))
lanes=collections.Counter((l["origin"],l["destination"]) for l in loads)
print("distinct lanes",len(lanes))
cities=collections.Counter()
for l in loads: cities[l["origin"]]+=l["vinCount"]; cities[l["destination"]]+=l["vinCount"]
print("top markets",cities.most_common(15))
first=min(l["orderedAt"] for l in loads); last=max(l["orderedAt"] for l in loads)
print("ordered range",first,last)
inbound=sum(1 for l in loads if l["destination"]!=l["origin"])
json.dump([{k:l[k] for k in ("store","origin","destination","vinCount","miles","orderedAt")} for l in loads],open(base+"/../baxter_loads.json","w"))
