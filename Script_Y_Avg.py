import arcpy
import datetime as dt
import numpy as np

''' Calcul de la moyenne des surface incendiées à l'instant T'''
##############################

arcpy.env.workspace = r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\ALERTE_INCENDIE_v2.sde"
IncendiesVIIRS = "ALERTE_INCENDIE_v2.dbo.DashboardVIIRSAdministratif"
champs = ["Debut", "SuperficieHa", "Nom"]

##############################

date_dbt = dt.datetime(2013, 1, 1)
annee_dbt = 2013
current_annee = dt.datetime.now().year
annees = range(annee_dbt, current_annee)
date_fin = dt.datetime(current_annee, 1, 1)

##############################



# def calcul_moy_par_jour(annees, sortedVIIRS_Prov_c, dates_c, initstr):
#     '''Calcul la valeur moyenne de la surface incendiée chaque jour de l'année'''
#     dico = [] 
#     som = 0
#     dates = dates_c  # .pop est impossible sur un argument
#     sortedVIIRS_Prov = sortedVIIRS_Prov_c
#     while len(sortedVIIRS_Prov) > 0 and len(dates) > 0:
#         if dt.datetime.strftime(sortedVIIRS_Prov[0][0], "%m%d") == initstr:
#             som += sortedVIIRS_Prov.pop(0)[1]  # La liste est classée par mois, puis par jour, puis par année
#         else:
#             dico.append([initstr, som/len(annees)])
#             init = dates.pop(0)
#             initstr = dt.datetime.strftime(init, "%m%d")
#             som = 0
#     while len(dates) > 0:
#         init = dates.pop(0)
#         initstr = dt.datetime.strftime(init, "%m%d")
#         dico.append([initstr, 0])
#         som = 0
#     while len(sortedVIIRS_Prov) > 0:
#         if dt.datetime.strftime(sortedVIIRS_Prov[0][0], "%m%d") == initstr:
#             som += sortedVIIRS_Prov.pop(0)[1]
#     if som != 0:
#         dico.append([initstr, som/len(annees)])
#     return dico

def calcul_moy_par_jour(annees, sortedVIIRS_Prov, dates):
    dico = [] 
    som = 0
    for date in dates:
        datestr = dt.datetime.strftime(date, "%m%d")
        surface_jour = [l[1] for l in sortedVIIRS_Prov if dt.datetime.strftime(l[0], "%m%d") == datestr]
        som = sum(surface_jour)
        dico.append([datestr, som/len(annees)])

def moyenne_cumulee(current_annee, dico, summedList, Province):
    for item in dico:
        datestr = item[0]
        surface = item[1]  # Sn
        lastS = summedList[-1][1]  # Un-1
        try:
            datestr += str(current_annee)
            date = dt.datetime.strptime(datestr, "%m%d%Y")
            npdate = np.datetime64(date)
            summedListSud.append((npdate, surface + lastS, Province))
        except:
            # Si l'année n'est pas bisextile, on saute le 29/02
            print("L'année actuelle n'est pas une année bissextile")
            pass
    return summedList

###################################
# On récupère les données dans la couche viirs pour chaque province
donneesVIIRS_Sud = [list(l) for l in arcpy.da.SearchCursor(IncendiesVIIRS, champs,\
    where_clause="Nom = 'Province Sud' AND Debut >= '2013-01-01' AND Debut < '" + dt.datetime.strftime(date_fin, "%Y-%m-%d") + "'")]
sortedVIIRS_Sud = sorted(donneesVIIRS_Sud, key= lambda x: int(dt.datetime.strftime(x[0], "%m%d%Y")))
donneesVIIRS_Nord = [list(l) for l in arcpy.da.SearchCursor(IncendiesVIIRS, champs,\
    where_clause="Nom = 'Province Nord' AND Debut >= '2013-01-01' AND Debut < '" + dt.datetime.strftime(date_fin, "%Y-%m-%d") + "'")]
sortedVIIRS_Nord = sorted(donneesVIIRS_Nord, key= lambda x: int(dt.datetime.strftime(x[0], "%m%d%Y")))
donneesVIIRS_Iles = [list(l) for l in arcpy.da.SearchCursor(IncendiesVIIRS, champs,\
    where_clause="Nom = 'Province des Iles' AND Debut >= '2013-01-01' AND Debut < '" + dt.datetime.strftime(date_fin, "%Y-%m-%d") + "'")]
sortedVIIRS_Iles = sorted(donneesVIIRS_Iles, key= lambda x: int(dt.datetime.strftime(x[0], "%m%d%Y")))

# Une liste des jours de l'année
dates = []
for jour in range(1, 367):
    dates.append(dt.datetime.strptime("{:03}".format(jour) + "/" + str(2020), "%j/%Y")) ## Année bissextile au hasard
    
print("Longueur de dates : {}\nLongueur de sortedVIIRS_Sud : {}\n".format(len(dates), len(sortedVIIRS_Sud)))
print("Longueur de dates : {}\nLongueur de sortedVIIRS_Nord : {}\n".format(len(dates), len(sortedVIIRS_Nord)))
print("Longueur de dates : {}\nLongueur de sortedVIIRS_Iles : {}\n".format(len(dates), len(sortedVIIRS_Iles)))


dico_Sud = calcul_moy_par_jour(annees, sortedVIIRS_Sud, dates)

dates = []
for jour in range(1, 367):
    dates.append(dt.datetime.strptime("{:03}".format(jour) + "/" + str(2020), "%j/%Y")) ## Année bissextile au hasard

print("Longueur de dates : {}".format(len(dates)))

dico_Nord = calcul_moy_par_jour(annees, sortedVIIRS_Nord, dates)

dates = []
for jour in range(1, 367):
    dates.append(dt.datetime.strptime("{:03}".format(jour) + "/" + str(2020), "%j/%Y")) ## Année bissextile au hasard

print("Longueur de dates : {}".format(len(dates)))

dico_Iles = calcul_moy_par_jour(annees, sortedVIIRS_Iles, dates)

# Un = Sn + Un-1, Sn étant la moyenne pour le jour n
# U0 = S0


        
temp = dico_Sud.pop(0)
summedListSud = [(np.datetime64(dt.datetime.strptime(temp[0] + str(current_annee), "%m%d%Y")), temp[1], "Province Sud")]
summedListSud = moyenne_cumulee(current_annee, dico_Sud, summedListSud, "Province Sud")

temp = dico_Nord.pop(0)
summedListNord = [(np.datetime64(dt.datetime.strptime(temp[0] + str(current_annee), "%m%d%Y")), temp[1], "Province Nord")]
summedListSud = moyenne_cumulee(current_annee, dico_Nord, summedListNord, "Province Nord")

temp = dico_Iles.pop(0)
summedListIles = [(np.datetime64(dt.datetime.strptime(temp[0] + str(current_annee), "%m%d%Y")), temp[1], "Province des Iles")]
summedListIles = moyenne_cumulee(current_annee, dico_Iles, summedListIles, "Province des Iles")


# On concatène les trois listes
npdt = np.dtype([('date', 'datetime64[us]'), ('S', np.float64), ('Province', 'a64')])
array = np.array(summedListSud + summedListNord + summedListIles, dtype=npdt)
# print("OK")
print(array)
arcpy.env.workspace = r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\Vulcain_DASHBOARD.gdb"
arcpy.Delete_management("Avg_Superficie")
arcpy.Delete_management(r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\Vulcain_DASHBOARD.gdb\Avg_Superficie")
arcpy.da.NumPyArrayToTable(array, r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\Vulcain_DASHBOARD.gdb\Avg_Superficie")
