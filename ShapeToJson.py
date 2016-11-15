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

input_var = int(
    input("For converting a shapefile to json, press 1! If you want to convert json to shapefiles instead, press 2"))
print()
print()

# ---------------------------------------------------------------------------------------------------------------------
# ------JSON TO SHAPEFILE----------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------

if input_var == 1:

    # ---------  Readig Shapefile containg feature geometry -----------------------------------------------------------

    filename = "coarse grained calcite.shp"  # in final version change to input command to get filname

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
            isClosed[i] = False

    isClosed = np.array(isClosed, dtype=bool)
    isClosed = isClosed.tolist()  # converting to list so it can be serialized by jason

    ID_index = range(len(shapes))  # s feature ID as combination of filename feature index & random numbers
    featureID = []

    for i in range(len(shapes)):
        ID = str(ID_index[i]) + "_" + str(int(random.uniform(1000, 9999))) + filename[0:4] + str(
            int(random.uniform(1000, 9999)))
        featureID.append(ID)

    # --------- Setting Groupinformation -- Discuss with Simon --------------------------------------------------------

    groupID = str(filename) + str(int(random.uniform(1000, 9999)))  # Discuss with Simon
    groupName = filename  # Discuss with Simon
    strokePaint = -3407872  # default value, shape files dont have visual information #Discuss with Simon
    fillPaint = 0  # default value, shape files dont have visual information #Discuss with Simon
    strokeWidth = 1  # default value, shape files dont have visual information #Discuss with Simon

    # --------- Writing the Json file ---------------------------------------------------------------------------------

    all_features = []

    for i in range(len(shapes)):
        all_features.append({"properties": {"uid": featureID[i], "scale": "not implemented yet",
                                            "description": "not implemented yet", "name": "not implemented yet",
                                            "group": groupID, "isClosed": isClosed[i], "angle": "not implemented yet"},
                             "type": "Feature",
                             "geometry": {"type": "Multipoint", "coordinates": coordinates[i]}})

    group_information = [{"uid": groupID, "name": groupName, "strokePaint": strokePaint, "fillPaint": fillPaint,
                          "strokeWidth": strokeWidth}]

    print(i)
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
