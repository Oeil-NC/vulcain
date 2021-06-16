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



def calcul_moy_par_jour(annees, sortedVIIRS_Prov_c, dates_c, initstr):
    dico = [] 
    som = 0
    dates = dates_c  # .pop est impossible sur un argument
    sortedVIIRS_Prov = sortedVIIRS_Prov_c
    while len(sortedVIIRS_Prov) > 0 and len(dates) > 0:
        if dt.datetime.strftime(sortedVIIRS_Prov[0][0], "%m%d") == initstr:
            som += sortedVIIRS_Prov.pop(0)[1]
        else:
            dico.append([initstr, som/len(annees)])
            init = dates.pop(0)
            initstr = dt.datetime.strftime(init, "%m%d")
            som = 0
    return dico

###################################
# On récupère les données dans la couche viirs pour chaque province
donneesVIIRS_Sud = [list(l) for l in arcpy.da.SearchCursor(IncendiesVIIRS, champs,\
    where_clause="Nom = 'Province Sud' AND BegDate >= '2013-01-01' AND BegDate < '" + dt.datetime.strftime(date_fin, "%Y-%m-%d") + "'")]
sortedVIIRS_Sud = sorted(donneesVIIRS_Sud, key= lambda x: int(dt.datetime.strftime(x[0], "%m%d%Y")))
donneesVIIRS_Nord = [list(l) for l in arcpy.da.SearchCursor(IncendiesVIIRS, champs,\
    where_clause="Nom = 'Province Nord' AND BegDate >= '2013-01-01' AND BegDate < '" + dt.datetime.strftime(date_fin, "%Y-%m-%d") + "'")]
sortedVIIRS_Nord = sorted(donneesVIIRS_Nord, key= lambda x: int(dt.datetime.strftime(x[0], "%m%d%Y")))
donneesVIIRS_Iles = [list(l) for l in arcpy.da.SearchCursor(IncendiesVIIRS, champs,\
    where_clause="Nom = 'Province des Iles' AND BegDate >= '2013-01-01' AND BegDate < '" + dt.datetime.strftime(date_fin, "%Y-%m-%d") + "'")]
sortedVIIRS_Iles = sorted(donneesVIIRS_Iles, key= lambda x: int(dt.datetime.strftime(x[0], "%m%d%Y")))

# avgs = np.array([], np.dtype([("Date", np.datetime64), ("Valeur", np.int32), ("Province", np.string)]))
# Une liste des jours de l'année
dates = []
for jour in range(1, 367):
    dates.append(dt.datetime.strptime("{:03}".format(jour) + "/" + str(2020), "%j/%Y")) ## Année bissextile au hasard
    
print("Longueur de dates : {}\nLongueur de sortedVIIRS_Sud : {}\n".format(len(dates), len(sortedVIIRS_Sud)))

init = dates.pop(0)
initstr = dt.datetime.strftime(init, "%m%d")

dico_Sud = calcul_moy_par_jour(annees, sortedVIIRS_Sud, dates, initstr)
dico_Nord = calcul_moy_par_jour(annees, sortedVIIRS_Nord, dates, initstr)
dico_Iles = calcul_moy_par_jour(annees, sortedVIIRS_Iles, dates, initstr)

# Un = Sn + Un-1, Sn étant le moyenne pour le jour n
# U0 = S0
temp = dico_Sud.pop(0)
summedListSud = [(np.datetime64(dt.datetime.strptime(temp[0] + str(current_annee), "%m%d%Y")), temp[1], "Province Sud")]
for item in dico_Sud:
    datestr = item[0]
    surface = item[1]
    lastS = summedListSud[-1][1]
    if datestr != "0229":
        datestr+=str(current_annee)
        date=dt.datetime.strptime(datestr, "%m%d%Y")
        npdate = np.datetime64(date)
        summedListSud.append((npdate, surface + lastS, "Province Sud"))

temp = dico_Nord.pop(0)
summedListNord = [(np.datetime64(dt.datetime.strptime(temp[0] + str(current_annee), "%m%d%Y")), temp[1], "Province Nord")]
for item in dico_Nord:
    datestr = item[0]
    surface = item[1]
    lastS = summedListNord[-1][1]
    if datestr != "0229":
        datestr+=str(current_annee)
        date=dt.datetime.strptime(datestr, "%m%d%Y")
        npdate = np.datetime64(date)
        summedListNord.append((npdate, surface + lastS, "Province Sud"))

temp = dico_Iles.pop(0)
summedListIles = [(np.datetime64(dt.datetime.strptime(temp[0] + str(current_annee), "%m%d%Y")), temp[1], "Province des Iles")]
for item in dico_Iles:
    datestr = item[0]
    surface = item[1]
    lastS = summedListIles[-1][1]
    if datestr != "0229":
        datestr+=str(current_annee)
        date=dt.datetime.strptime(datestr, "%m%d%Y")
        npdate = np.datetime64(date)
        summedListIles.append((npdate, surface + lastS, "Province Sud"))

# On concatène les trois listes
npdt = np.dtype([('date', 'datetime64[us]'), ('S', np.float64), ('Province', np.string)])
array = np.array(summedListSud + summedListNord + summedListIles, dtype=npdt)
# print("OK")
# print(array.dtype)
arcpy.env.workspace = r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\Vulcain_DASHBOARD.gdb"
arcpy.Delete_management(r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\Vulcain_DASHBOARD.gdb\Avg_Superficie")
arcpy.Delete_management("Avg_Superficie")
arcpy.da.NumPyArrayToTable(array, r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\Vulcain_DASHBOARD.gdb\Avg_Superficie")
