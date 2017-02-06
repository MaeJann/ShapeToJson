# ---------------------------------------------------------------------------------------------------------------------
# Working titel: ShapeToJason
# Author: Jannik Märsch
# Version: 0.4
# Last changes: 01.02.2017
# ---------------------------------------------------------------------------------------------------------------------


import shapefile
import numpy as np
import random
import json
import uuid
import copy

input_var = int(
    input("For converting a shapefile to json, press 1! If you want to convert json to shapefiles instead, press 2. Confirm with enter."))
print()
print()

# ---------------------------------------------------------------------------------------------------------------------
# ------JSON TO SHAPEFILE----------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

if input_var == 1:

    # --- Read shapefile containg feature geometry:

    filename = input("Filename:")  # in final version change to input command to get filname

    SF = shapefile.Reader(filename)
    shapes = SF.shapes()

    fields = SF.fields
  

    # --- Generate feature data:

    Feature_type = "Feature"

    geometry_type = "Multipoint"  

    coordinates = {}  # extract coordinates; key = dictionairy index = feature index
    k = 0

    while k < len(shapes):
        key = k
        value = shapes[k].points
        coordinates[k] = value
        k += 1

    for i in range(len(shapes)):  # convert to list so it can be serialized by jason
        coordinates[i] = np.array(coordinates[i])
        coordinates[i] = coordinates[i].tolist()

    isClosed = np.empty(len(shapes))
    
    for i in range(len(coordinates)):  # convert coordinates to match tileviewer coordinate system and checking if features are closed
        
        if coordinates[i][0] == coordinates[i][-1]:
            isClosed[i] = True
        else:
            coordinates[i].append(coordinates[i][0])
            isClosed[i] = True

        for j in range(len(coordinates[i])):
            coordinates[i][j][0] = 4.00017073e+00 * coordinates[i][j][0] + 5.20006199e+04
            coordinates[i][j][1] = -4.00121315 * coordinates[i][j][1] - 82.60063378

    isClosed = np.array(isClosed, dtype=bool)
    isClosed = isClosed.tolist() # convert to list so it can be serialized by jason
    
    # --- Set feature ID to unique uuid:
    
    featureID = []
    for i in range(len(shapes)):
        featureID.append(str(uuid.uuid4()))

    # --- Set angle to default 

    angle = 27.095552493781793

    # --- Set some default groupinformation: 

    groupID = str(uuid.uuid4()) 
    groupName = filename[0:-4] 
    strokePaint = -3407872  
    fillPaint = 0  
    strokeWidth = 1 

    # --- Write Json file:

    all_features = []

    for i in range(len(shapes)):
        all_features.append({"properties": {"uid": featureID[i], "scale": 0.069442284018722882,
                                            "description": "", "name": "",
                                            "group": groupID, "isClosed": isClosed[i], "angle": angle},
                             "type": "Feature",
                             "geometry": {"type": "Multipoint", "coordinates": coordinates[i]}})

    group_information = [{"uid": groupID, "name": groupName, "strokePaint": strokePaint, "fillPaint": fillPaint,
                          "strokeWidth": strokeWidth}]

    
    root = {"features": all_features, "type": "FeatureCollection", "groups": group_information}

    finalFile = json.dumps(root)
    file = open("ConvertedShapefile.json", "w")
    file.write(finalFile)
    file.close()

    print("FINISHED")
    input("To close this window, press ENTER!")

# ---------------------------------------------------------------------------------------------------------------------
# ----JSON TO SHAPEFILE------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


elif input_var == 2:

    # --- Open Json file:

    filename = input("Filename:") 

    with open(filename) as data_file:
        data = json.load(data_file)

    # --- Extract feature and group data:
    
    features = data["features"]
    groups = data["groups"]

    # --- Define empty arrays to store individual data:
    
    featureID = []
    isClosed = []
    coordinates = []
    coordinates_corr = []
    featureGroup = []
    groupID = []
    groupName = []

    # --- Iterate through all features and extract data for each feature:

    for i in range(len(features)):
        featureID.append(features[i]["properties"]["uid"])
        featureGroup.append(features[i]["properties"]["group"])
        isClosed.append(features[i]["properties"]["isClosed"]) 
        coordinates.append(features[i]["geometry"]["coordinates"])

    # --- Convert coordinates to match ArcGis coordinate system:
        
    coordinates_corr = copy.deepcopy(coordinates) 
    for i in range(len(features)):
        for j in range(len(coordinates[i])):                                                               
            coordinates_corr[i][j][0] = (coordinates[i][j][0] -  5.20006199e+04) / 4.00017073e+00
            coordinates_corr[i][j][1] = (coordinates[i][j][1] + 82.60063378)     /-4.00121315

    # --- Create a shape file to all groups and add all features with the corresponding groupID:
    
    for k in range(len(groups)):
        groupID.append(groups[k]["uid"])
        groupName.append(groups[k]["name"])

        newShapeFile = shapefile.Writer()
        newShapeFile.autoBalance = 1
        newShapeFile.field('Id', 'N', 6, 0)

        for j in range(len(featureID)):
            if featureGroup[j] == groupID[k]:
                newShapeFile.poly(shapeType=5, parts=[coordinates_corr[j]])
                newShapeFile.record(j)

        newShapeFile.save(groupName[k])
        
    print("FINISHED")
    input("To close this window, press ENTER!")
