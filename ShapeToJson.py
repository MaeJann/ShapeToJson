# ---------------------------------------------------------------------------------------------------------------------
# Working titel: ShapeyVsJason
# Author: Jannik Märsch
# Version: 0.2
# Last changes: 29.19.2016
# ---------------------------------------------------------------------------------------------------------------------

2
import shapefile
import numpy as np
import random
import json
import uuid

input_var = int(
    input("For converting a shapefile to json, press 1! If you want to convert json to shapefiles instead, press 2"))
print()
print()

# ---------------------------------------------------------------------------------------------------------------------
# ------JSON TO SHAPEFILE----------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

if input_var == 1:

    # ---------  Readig Shapefile containg feature geometry -----------------------------------------------------------

    filename = "duplex structure.shp"  # in final version change to input command to get filname

    SF = shapefile.Reader(filename)
    shapes = SF.shapes()

    fields = SF.fields
    print(fields)

    # ---------  Generating feature data ------------------------------------------------------------------------------

    Feature_type = "Feature"  # Default: "Feature"

    geometry_type = "Multipoint"  # Default: "Multipoint"

    coordinates = {}  # extracting coordinates; key = dictionairy index = feature index
    k = 0

    while k < len(shapes):
        key = k
        value = shapes[k].points
        coordinates[k] = value
        k += 1

    for i in range(len(shapes)):  # converting to list so it can be serialized by jason
        coordinates[i] = np.array(coordinates[i])
        coordinates[i] = coordinates[i].tolist()

    isClosed = np.empty(len(shapes))

    for i in range(len(coordinates)):  # checking if features are closed
        if coordinates[i][0] == coordinates[i][-1]:
            isClosed[i] = True
        else:
            coordinates[i].append(coordinates[i][0])
            isClosed[i] = True

    isClosed = np.array(isClosed, dtype=bool)
    isClosed = isClosed.tolist()  # converting to list so it can be serialized by jason
    
    # setting feature ID as unique uuid
    
    featureID = []
    for i in range(len(shapes)):
        featureID.append(str(uuid.uuid4()))

    # setting angle as default to 1

    angle = 1.

    # --------- Setting Groupinformation -- Discuss with Simon --------------------------------------------------------

    groupID = str(uuid.uuid4()) 
    groupName = filename[0:-4] 
    strokePaint = -3407872  
    fillPaint = 0  
    strokeWidth = 1 

    # --------- Writing the Json file ---------------------------------------------------------------------------------

    all_features = []

    for i in range(len(shapes)):
        all_features.append({"properties": {"uid": featureID[i], "scale": "not implemented yet",
                                            "description": "", "name": "",
                                            "group": groupID, "isClosed": isClosed[i], "angle": angle},
                             "type": "Feature",
                             "geometry": {"type": "Multipoint", "coordinates": coordinates[i]}})

    group_information = [{"uid": groupID, "name": groupName, "strokePaint": strokePaint, "fillPaint": fillPaint,
                          "strokeWidth": strokeWidth}]

    
    root = {"features": all_features, "type": "FeatureCollection", "groups": group_information}
    # print(json.dumps(root, sort_keys=False, indent = 4))

    finalFile = json.dumps(root)
    file = open("test.json", "w")
    file.write(finalFile)
    file.close()
    print("FINISHED")

# ---------------------------------------------------------------------------------------------------------------------
# ----JSON TO SHAPEFILE------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


elif input_var == 2:
    print("json to shapefile is not implemented yet")

    with open('annotations.json') as data_file:
        data = json.load(data_file)

    features = data["features"]
    groups = data["groups"]

    featureID = []
    isClosed = []
    coordinates = []
    featureGroup = []

    groupID = []
    groupName = []

    for i in range(len(features)):
        featureID.append(features[i]["properties"]["uid"])
        featureGroup.append(features[i]["properties"]["group"])
        isClosed.append(features[i]["properties"]["isClosed"])
        coordinates.append(features[i]["geometry"]["coordinates"])

    for k in range(len(groups)):
        groupID.append(groups[k]["uid"])
        groupName.append(groups[k]["name"])

        newShapeFile = shapefile.Writer()
        newShapeFile.autoBalance = 1
        newShapeFile.field('Id', 'N', 6, 0)

        for j in range(len(featureID)):
            if featureGroup[j] == groupID[k]:
                newShapeFile.poly(shapeType=5, parts=[coordinates[j]])
                newShapeFile.record(j)

        newShapeFile.save(groupName[k])

    print("FINISHED")
