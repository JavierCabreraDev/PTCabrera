from functions import *

arcpy.env.overwriteOutput = True        
#arcpy.env.workspace = r"C:\Users\Alumno\Documents\MapMatching\code\Portage\PortageRoads\portage.gdb"
arcpy.env.workspace = r"C:\TMMA\GeoBd_JCV\Routes\GeoBd_JCV.gdb"
roadway = r"VinaRoute\VinaRoads"
networkDataSet = r"VinaRoute\VinaRoute_ND"
#roadway = r"Geodatabase\Ubicacion_Javier"
#networkDataSet = r"Geodatabase\Ubicacion_Javier_ND"
snapData = "snapData"
tempData = "tempData"
assignData = "assignData"
tempTable = "tempTable"
currentRoute = "currentRoute"
currentRouteSearch = "currentRoute/Routes"
assignTable = "assignTable"

## dictionary with the results
d_res = {}
## dictionary with amount of gps points.
d_gps = {}
## speed tolerance range parameter (rs/2) (mile/hr).
tol_rs_List = [15] #15, 25, 35
## buffer parameter
searchRadius_List = [20] #20, 40, 60
## sampling frequency (temporal resolution)
samp_freq_List = [10]
## amount of points
n_points = 5
## feature class data 
fc_data = "4" 

for samp_freq in samp_freq_List:
    ## Create the geoprocessor object.
    gp = arcgisscripting.create(9.3)  # allow backward compatibility down to ArcGIS 9.3
    ## Set the necessary product code.
    gp.SetProduct("ArcInfo")
    ## Check out any necessary licenses.
    gp.CheckOutExtension("Network")

    serie_List = range(1,samp_freq/10 + 1)
        
    for serie in serie_List:
        
        #gpsData = "data_" + str(fc_data) + "_" + str(samp_freq) + "sec_" + str(serie)
        gpsData = "data_" + str(fc_data) + "_" + str(samp_freq) + "sec_" + str(serie)
        print "------"
        print gpsData
        print "------"
        for tol_rs in tol_rs_List:
            
            #print tol_rs
            #print tol_rs_List
            
            for sr in searchRadius_List:
                searchRadius = str(sr)
                print "SearchRadius -> " + searchRadius

 
                finalData = "Javier_final" + gpsData[4:] + '_' + str(tol_rs) + '_' + str(sr)
                print finalData

                start = time.clock()
                ## dictionary with near segments and corresponding snap points.
                snapDict = {}
                ## dictionary with the accepted snap points.
                acceptDict = {}
                
                ## the spatial reference from gpsData is obtained.
                spatial_reference = arcpy.Describe(gpsData).spatialReference
                
                ## dictionary with the gps points --> {objectID: "gpsPoint":(x,y),"time":str,"dSpeed":float}
                gpsDict = gpsDataDict(gpsData)
                
                
                #print len(gpsDict)
                if samp_freq not in d_gps:
                    d_gps[samp_freq] = {}
                if serie not in d_gps[samp_freq]:
                    d_gps[samp_freq][serie] = len(gpsDict)

                print "gps dictionary done..."

                x_mid,y_mid = getMidPoint(gpsDict)
                #print "midPoint : ({},{})".format(x_mid,y_mid)
                print
                ## a temporal feature class for a gps point.
                arcpy.CreateFeatureclass_management(arcpy.env.workspace, tempData, "POINT", "", "DISABLED", "DISABLED", spatial_reference)
                tempCursor = arcpy.da.InsertCursor(tempData,["SHAPE@XY"])
                tempCursor.insertRow([(x_mid,y_mid)])
                del tempCursor

                ## feature class for snap_i and snap_j.
                arcpy.CreateFeatureclass_management(arcpy.env.workspace, snapData, "POINT", "", "DISABLED", "DISABLED", spatial_reference)
                snapCursor = arcpy.da.InsertCursor(snapData,["SHAPE@XY"])
                snapCursor.insertRow([(x_mid,y_mid)])
                snapCursor.insertRow([(x_mid,y_mid)])
                del snapCursor

                ## a temporal feature class for snap assignment.
                arcpy.CreateFeatureclass_management(arcpy.env.workspace, assignData, "POINT", "", "DISABLED", "DISABLED", spatial_reference)
                assignCursor = arcpy.da.InsertCursor(assignData,["SHAPE@XY"])
                assignCursor.insertRow([(x_mid,y_mid)])
                del assignCursor

                ## assign first point to a route
                
                snapDict = near_segments(1,tempData,roadway,tempTable,searchRadius,gpsDict,snapDict)
                if snapDict[1] == []:
                    acceptDict[1] = (gpsDict[1]['gpsPoint'],0)
                    ## print "Accepted: {}({})\n".format(1,0)
                else:
                    fid = snapDict[1][0][1]
                    snap = (snapDict[1][0][2],snapDict[1][0][3])
                    acceptDict[1] = (snap,fid)
                    ## print "Accepted: {}({})\n".format(1,fid)
                    
                j = 2
                n = len(gpsDict)
                while j <= n:
                    ## print "map j:{}".format(j)
                    acceptDict = mapMatch(j,tol_rs,snapData,tempData,assignData,tempTable,assignTable,searchRadius,currentRoute,currentRouteSearch,networkDataSet,roadway,gpsDict,snapDict,acceptDict,gp,n_points,n)
                    j += 1

                acceptSnapPoints(n,finalData,acceptDict,spatial_reference) #layer final
                clean(snapData,tempData,assignData,tempTable,assignTable)
                res = compareFID(n,finalData,gpsDict)
                end = time.clock()
                time_elapsed = (end - start)/60
                if samp_freq not in d_res:
                    d_res[samp_freq] = {}
                if tol_rs not in d_res[samp_freq]:
                    d_res[samp_freq][tol_rs] = []
                d_res[samp_freq][tol_rs].append((searchRadius,serie,res,round(time_elapsed,3)))

print d_gps
print d_res
