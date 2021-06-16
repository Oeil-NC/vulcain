# -*- coding: utf8 -*-

import arcpy
import datetime as dt
from arcpy import env

''' Ce script permat la création des tables de données utilisées par les onglets 
- PPE
- PEM
- APP
de Vulcain
'''
############################ VARIABLES ############################

# Année
year = dt.date.today().year

# Workspace
sde = r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\ALERTE_INCENDIE_v2.sde"
gdb = r"D:\02_ServicesPublies\DASHBOARD_IncendiesVIIRS\Vulcain_DASHBOARD.gdb"
# Listes des couches de travail
couchePPE = "ALERTE_INCENDIE_v2.DBO.Perimetre_protection_eaux"
couchePEM = "ALERTE_INCENDIE_v2.DBO.EspecesMenaceesEndemia"
coucheAPP = "ALERTE_INCENDIE_v2.DBO.Aires_protegees_terrestres_1"
coucheVIIRS = "ALERTE_INCENDIE_v2.dbo.DashBoardVIIRSAdministratif"
PPE = "PPE"
PEM = "PEM"
APP = "APP"
VIIRS = "VIIRS"
whereRequete = "Nom <> 'Nouvelle-Calédonie' AND Debut >= '" + str(year) + "-01-01'"
majPerimetre = True

############################ PREPARATION ############################

if majPerimetre:
    env.workspace = gdb
    arcpy.Delete_management(PPE)
    arcpy.Delete_management(PEM)
    arcpy.Delete_management(APP)
    arcpy.Delete_management(VIIRS)

    env.workspace = sde
    arcpy.CopyFeatures_management(couchePPE, gdb + "/" + PPE)
    arcpy.CopyFeatures_management(couchePEM, gdb + "/" + PEM)
    arcpy.CopyFeatures_management(coucheAPP, gdb + "/" + APP)
    arcpy.MakeQueryLayer_management(sde, "viirs_query_layer",
                                    "select OBJECTID, SHAPE, SuperficieHa, Source, Debut, Fin, Nom, ID_INCENDIE from " + coucheVIIRS + " where " + whereRequete,
                                    "OBJECTID", shape_type="POLYGON", srid="3163")
    arcpy.CopyFeatures_management("viirs_query_layer", gdb + "/" + VIIRS)
    
env.workspace = gdb
# Suppression des tables et couches existantes
##arcpy.Delete_management("ALERTE_INCENDIE_v2.DBO.VIIRS_PPE_TEMP")
##arcpy.Delete_management("ALERTE_INCENDIE_v2.DBO.VIIRS_PEM_TEMP")
##arcpy.Delete_management("ALERTE_INCENDIE_v2.DBO.VIIRS_APP_TEMP")
##arcpy.Delete_management("ALERTE_INCENDIE_v2.DBO.PPE_VIIRS_TEMP")
##arcpy.Delete_management("ALERTE_INCENDIE_v2.DBO.PEM_VIIRS_TEMP")
##arcpy.Delete_management("ALERTE_INCENDIE_v2.DBO.APP_VIIRS_TEMP")

arcpy.DeleteRows_management("DashBoardVIIRS__PPE")
arcpy.DeleteRows_management("DashBoardVIIRS__PEM")
arcpy.DeleteRows_management("DashBoardVIIRS__APP")
arcpy.DeleteRows_management("DashBoardPPE__VIIRS")
arcpy.DeleteRows_management("DashBoardPEM__VIIRS")
arcpy.DeleteRows_management("DashBoardAPP__VIIRS")

arcpy.Delete_management("VIIRS_PPE_TEMP")
arcpy.Delete_management("VIIRS_PEM_TEMP")
arcpy.Delete_management("VIIRS_APP_TEMP")
arcpy.Delete_management("PPE_VIIRS_TEMP")
arcpy.Delete_management("PEM_VIIRS_TEMP")
arcpy.Delete_management("APP_VIIRS_TEMP")

############################ TRAVAIL ############################

# Spatial Join
arcpy.analysis.SpatialJoin(target_features=VIIRS, join_features=PPE, out_feature_class="VIIRS_PPE_TEMP",
                           join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON")
arcpy.analysis.SpatialJoin(target_features=VIIRS, join_features=PEM, out_feature_class="VIIRS_PEM_TEMP",
                           join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON")
arcpy.analysis.SpatialJoin(target_features=VIIRS, join_features=APP, out_feature_class="VIIRS_APP_TEMP",
                           join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON")

arcpy.analysis.SpatialJoin(target_features=PPE, join_features=VIIRS, out_feature_class="PPE_VIIRS_TEMP",
                           join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON")
arcpy.analysis.SpatialJoin(target_features=PEM, join_features=VIIRS, out_feature_class="PEM_VIIRS_TEMP",
                           join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON")
arcpy.analysis.SpatialJoin(target_features=APP, join_features=VIIRS, out_feature_class="APP_VIIRS_TEMP",
                           join_operation="JOIN_ONE_TO_ONE", join_type="KEEP_COMMON")

# Make Table View
arcpy.MakeTableView_management("VIIRS_PPE_TEMP", "Table_VIIRS_PPE")
arcpy.MakeTableView_management("VIIRS_PEM_TEMP", "Table_VIIRS_PEM")
arcpy.MakeTableView_management("VIIRS_APP_TEMP", "Table_VIIRS_APP")

arcpy.MakeTableView_management("PPE_VIIRS_TEMP", "Table_PPE_VIIRS")
arcpy.MakeTableView_management("PEM_VIIRS_TEMP", "Table_PEM_VIIRS")
arcpy.MakeTableView_management("APP_VIIRS_TEMP", "Table_APP_VIIRS")

# Remplissage des tables
arcpy.Append_management("Table_VIIRS_PPE", "DashBoardVIIRS__PPE", "NO_TEST")
arcpy.Append_management("Table_VIIRS_PEM", "DashBoardVIIRS__PEM", "NO_TEST")
arcpy.Append_management("Table_VIIRS_APP", "DashBoardVIIRS__APP", "NO_TEST")

arcpy.Append_management("Table_PPE_VIIRS", "DashBoardPPE__VIIRS", "NO_TEST")
arcpy.Append_management("Table_PEM_VIIRS", "DashBoardPEM__VIIRS", "NO_TEST")
arcpy.Append_management("Table_APP_VIIRS", "DashBoardAPP__VIIRS", "NO_TEST")
##arcpy.CopyRows_management("Table_VIIRS_PPE", "DashBoardVIIRS__PPE")
##arcpy.CopyRows_management("Table_VIIRS_PEM", "DashBoardVIIRS__PEM")
##arcpy.CopyRows_management("Table_VIIRS_APP", "DashBoardVIIRS__APP")
##arcpy.CopyRows_management("Table_PPE_VIIRS", "DashBoardPPE__VIIRS")
##arcpy.CopyRows_management("Table_PEM_VIIRS", "DashBoardPEM__VIIRS")
##arcpy.CopyRows_management("Table_APP_VIIRS", "DashBoardAPP__VIIRS")

############################ NETTOYAGE ############################

arcpy.Delete_management("VIIRS_PPE_TEMP")
arcpy.Delete_management("VIIRS_PEM_TEMP")
arcpy.Delete_management("VIIRS_APP_TEMP")
arcpy.Delete_management("PPE_VIIRS_TEMP")
arcpy.Delete_management("PEM_VIIRS_TEMP")
arcpy.Delete_management("APP_VIIRS_TEMP")
