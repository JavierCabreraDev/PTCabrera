import arcpy

arcpy.env.workspace = r"C:\Users\Alumno\Documents\MapMatching\code\vincent\Portage\PortageRoads\portage.gdb"


dataDelete = []
dataKeep = []

for data in arcpy.ListFeatureClasses():
    if "2260168102" in data:
        print data
        arcpy.Delete_management(data)

##    if "data" in data:
##        num = data[5:15]
##        if num in dataset:
##            dataKeep.append(data)
##        else:
##            dataDelete.append(data)
##    else:
##        dataDelete.append(data)
##
##for data in dataDelete:
    
