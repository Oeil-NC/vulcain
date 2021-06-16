import arcpy
import datetime as dt
import numpy as np

''' Calcul de la moyenne des surface incendiées à l'instant T'''
##############################

arcpy.env.workspace = r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\ALERTE_INCENDIE_v2.sde"
IncendiesVIIRS = "ALERTE_INCENDIE_v2.DBO.incendies_VIIRS"
champs = ["BegDate", "superf_ha"]

##############################

date_dbt = dt.datetime(2013, 1, 1)
annee_dbt = 2013
current_annee = dt.datetime.now().year
annees = range(annee_dbt, current_annee)
date_fin = dt.datetime(current_annee, 1, 1)

##############################
donneesVIIRS = [list(l) for l in arcpy.da.SearchCursor(IncendiesVIIRS, champs, where_clause="BegDate >= '2013-01-01' AND BegDate < '" + dt.datetime.strftime(date_fin, "%Y-%m-%d") + "'")]
sortedVIIRS = sorted(donneesVIIRS, key= lambda x: int(dt.datetime.strftime(x[0], "%m%d%Y")))
avgs = np.array([], np.dtype([("Date", np.datetime64), ("Valeur", np.int32)]))
dates = []
for jour in range(1, 367):
    dates.append(dt.datetime.strptime("{:03}".format(jour) + "/" + str(2020), "%j/%Y")) ## Année bissextile au hasard
    
print("Longueur de dates : {}\nLongueur de sortedVIIRS : {}\n".format(len(dates), len(sortedVIIRS)))

init = dates.pop(0)
initstr = dt.datetime.strftime(init, "%m%d")
dico = []
som = 0
while len(sortedVIIRS) > 0 and len(dates) > 0:
    if dt.datetime.strftime(sortedVIIRS[0][0], "%m%d") == initstr:
        som += sortedVIIRS.pop(0)[1]
    else:
        dico.append([initstr, som/len(annees)])
        init = dates.pop(0)
        initstr = dt.datetime.strftime(init, "%m%d")
        som = 0
temp = dico.pop(0)
summedList = [(np.datetime64(dt.datetime.strptime(temp[0] + str(current_annee), "%m%d%Y")), temp[1])]
for item in dico:
    datestr = item[0]
    surface = item[1]
    lastS = summedList[-1][1]
    if datestr != "0229":
        datestr+=str(current_annee)
        date=dt.datetime.strptime(datestr, "%m%d%Y")
        npdate = np.datetime64(date)
        summedList.append((npdate, surface + lastS))
npdt = np.dtype([('date', 'datetime64[us]'), ('S', np.float64)])
array = np.array(summedList, dtype=npdt)
# print("OK")
# print(array.dtype)
arcpy.env.workspace = r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\Vulcain_DASHBOARD.gdb"
arcpy.Delete_management(r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\Vulcain_DASHBOARD.gdb\Avg_Superficie")
arcpy.Delete_management("Avg_Superficie")
arcpy.da.NumPyArrayToTable(array, r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\Vulcain_DASHBOARD.gdb\Avg_Superficie")

