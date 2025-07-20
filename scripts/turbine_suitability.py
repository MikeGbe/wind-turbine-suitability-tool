"""
@author: Michael Adegbenro
@collaborators: NA
@python: Python 3.8
Date: July 14th, 2023
"""

import arcpy,os

#defining custom error exceptions 
class WeightError(Exception): # Define Custom Exception: "Incorrect weight parameter is entered"
	pass
	
class UnitError(Exception): # Define Custom Exception: "Wrong unit is passed by user"
	pass
try:
    
    ####################################################
    #Set the environment settings workspace property to the geodatabase
    #arcpy.env.workspace = workspace
    dem_path = arcpy.GetParameterAsText(0) #"E:\GEOG656\Final\DEM\downloaded_tifs"
    county_data_path = arcpy.GetParameterAsText(1) #E:\GEOG656\Final\Virginia.gdb\
    ws_path = arcpy.GetParameterAsText(2) #E:/GEOG656/Final/us-wind-data/
    work_path = arcpy.GetParameterAsText(3) #input - workspace

    VA_County = arcpy.GetParameterAsText(4) # input - shapefile of county
    county_name = arcpy.GetParameterAsText(5) #Select county from dropdown list #"Hanover" #"Pittsylvania" 

    w1 = float(arcpy.GetParameterAsText(6)) # input - 1st suitability weight
    slope_range = arcpy.GetParameterAsText(7) #input range for slope reclassify
    w2 = float(arcpy.GetParameterAsText(8)) # input - 2nd suitability weight

    ws_range = arcpy.GetParameterAsText(9)  #input range for windspeed reclassify
    area_units = arcpy.GetParameterAsText(10) #input - area calculation units (acres or hectares)
    final_output = arcpy.GetParameterAsText(11) #input - output name of the final table #"Parcel_Suitability"

    ########################################################

    #check the weights, raise error if not 0-1 or not add up to 1
    if(w1 < 0 or w1 > 1.0) or (w2 < 0 or w2 > 1.0) or (w1 + w2 != 1.0):
        raise WeightError
    
    #Checking area units, raise error if not “acres” or “hectares”
    if (area_units.lower() != 'acres') and (area_units.lower() != 'hectares'):
        raise UnitError

    def reclasrange(inrange):
            """
            Input
            Semicolon and space seperated string
            Output
            Range List of range for reclassification
            """
            inrange = inrange.split(';')# Split the input string by semicolons

            # Initialize an empty list to store the result
            reclass = []

            # Process each section and create nested lists
            for vrange in inrange:
                values = vrange.split()  #Split the section by spaces
                nested_list = [int(val) for val in values]  #Convert the values to integers
                reclass.append(nested_list)  #Append the nested list 
            arcpy.AddMessage(reclass) #Print reformatted value range
            return reclass

    #Define a where clause to select the state whose "NAME" is equal to the input state name.
    whereClause = "\"NAME_2\" = '%s'"% county_name #defining search parameter
    arcpy.AddMessage("County Name: %s"%county_name)
    #arcpy.AddMessage(whereClause) #checking clause

    #Read the first row of the feature class with Search Cursor
    #Creating search cursor using the where clause to filter the orws in the table
    searchCurs = arcpy.da.SearchCursor(VA_County, ["SHAPE@", "NAME_2"], where_clause=whereClause)
        
    #Access the Polygon geometry object (the "Shape" field)
    row = searchCurs.next()
    #Store Polygon geometry object and name as variables for later use
    county_geo = row[0].extent #row[0] 
    # name of the feature (the "Name" field)
    ft_name = row[1]

    #Spatial reference object
    ref = county_geo.spatialReference

    selected_rasters = []
    
    #############################
    arcpy.env.workspace = dem_path
    arcpy.env.overwriteOutput = True
    #############################
    
    # Iterate through each raster tile
    for raster_name in arcpy.ListRasters("*.tif", "TIF"):
        # Check if the raster intersects with the county shapefile
        raster = arcpy.Raster(raster_name)
        extent = raster.extent

        if county_geo.overlaps(extent): #extent.within(geo)
            selected_rasters.append(raster_name)
            #arcpy.AddMessage(raster_name)

    arcpy.AddMessage(selected_rasters) 


    px_type = "32_BIT_FLOAT" #"16_BIT_SIGNED"
    # Merging input rasters
    arcpy.AddMessage("Starting merge of input tiles")

    # Create a list to store the arcpy.Raster objects
    raster_obj_list = []

    # Create arcpy.Raster objects for each raster name in the list
    for raster_name in selected_rasters:
        #raster_name = raster_name.split('.')[0]
        raster_obj = arcpy.Raster(raster_name)
        raster_obj_list.append(raster_obj)

    #Merging selected rasters
    arcpy.AddMessage("Setting up raster tile merge")
    merged_raster = arcpy.ia.Merge(raster_obj_list, "FIRST")
    arcpy.AddMessage("Merge complete!")

    #Reprojecting input rasters to StatePlane_Virginia_North
    arcpy.AddMessage("Setting up raster reprojection and pixel size")
    proj = arcpy.SpatialReference("NAD_1983_2011_StatePlane_Virginia_North_FIPS_4501")
    #arcpy.AddMessage(proj)
    reprojected_raster = arcpy.ia.Reproject(merged_raster, {"wkid" : 6592}, 10, 10)
    arcpy.AddMessage("Reprojection complete")
    arcpy.AddMessage("Writing raster to file!")

    
    #############################
    arcpy.env.workspace = work_path
    arcpy.env.overwriteOutput = True
    #############################

    #Output name for the merged raster dataset
    output_raster = "_dem" #os.path.join(work_path,"%s_dem"%county_name) 
    reprojected_raster.save(output_raster)
    arcpy.AddMessage("Finished!")

    arcpy.AddMessage("***********************")
    #Clipping merged raster to extent of selected county
    in_raster = output_raster #cnanging name variable of merged + reprojected raster from above for clip input
    out_raster = "DEM_clip" #setting name of output clip DEM
    nodata_value = -9999

    # Create a feature layer from the feature class using the where clause
    feature_layer_name = "SelectedCountyLayer"
    arcpy.MakeFeatureLayer_management(VA_County, feature_layer_name, where_clause=whereClause)

    #Saving selected county as feature
    output_feature_class = "SelectedCounty"
    arcpy.CopyFeatures_management(feature_layer_name, output_feature_class)

    arcpy.AddMessage("Clipping raster to match extent of county")
    ##using polygon geometry from selected county to clip raster
    arcpy.management.Clip(in_raster, feature_layer_name, out_raster, output_feature_class,\
                          nodata_value, "ClippingGeometry", "NO_MAINTAIN_EXTENT")
    arcpy.AddMessage("Raster has been clipped!")

    #arcpy.AddMessage("Starting Suitability Model...") #Displaying completion message in black
    arcpy.AddMessage("Starting Suitability Model...")
    #Reclassifying rasters##
    arcpy.AddMessage("Deriving slope from 10m DEM")
    outSlope = arcpy.sa.Slope(out_raster, "PERCENTRISE", "1") #reading dem and converting to percent slope (note: flat surface has slope of 0%; 45-degree surface is 100%)
    slope = outSlope.save("slope") # Save to permeant location
    arcpy.AddMessage("Slope has been calculated for %s County"%county_name)

    #Reclassify the slope raster
    slopeRemapRange = arcpy.sa.RemapRange(reclasrange(slope_range)) #Assume relatively flat regions are preferred [[0, 5, 4], [5, 10, 3], [10, 15, 2],[15, 100, 1]]
    slopeReclass = arcpy.sa.Reclassify("slope", "VALUE", slopeRemapRange)
    slopeReclass.save("slope_Reclass")
    arcpy.AddMessage("Slope Raster Reclassified!")#Displaying completion message in black


    ###############################
    arcpy.AddMessage("***********************")
    #Reproject and clip 10m wind speed raster
    #arcpy.env.workspace = "E:\GEOG656\Final\work.gdb"
    #arcpy.env.overwriteOutput = True

    arcpy.AddMessage("Setting up Wind Speed Data")
    wind_raster = arcpy.Raster(os.path.join(ws_path,"USA_wind-speed_10m.tif"))#user input path to windspeed raster
    arcpy.AddMessage("Setting up raster reprojection")

    reprojected_raster = arcpy.ia.Reproject(wind_raster, {"wkid" : 6592}, 10, 10)
    arcpy.AddMessage("Reprojection complete")

    arcpy.AddMessage("Clipping windspeed raster to match extent of county")
    ##using polygon geometry from selected county to clip raster
    in_raster = reprojected_raster #wind_raster 
    out_raster = "windspeed_clip" #setting name of output windspeed clip
    arcpy.management.Clip(in_raster, feature_layer_name, out_raster, output_feature_class,\
                          nodata_value, "ClippingGeometry", "NO_MAINTAIN_EXTENT")
    arcpy.AddMessage("Raster has been clipped!")
    ###################################

    #Reclassify the windspeed raster
    """
    #Rank 1: 6 to 9 m/s (13 to 20 mph)
    #Rank 2: 5 to 10 m/s (11 to 22 mph)
    #Rank 3: 4 to 12 m/s (9 to 27 mph)
    #Rank 4: 3 to 15 m/s (7 to 34 mph)
    """

    windRemapRange = arcpy.sa.RemapRange(reclasrange(ws_range)) #Assume relatively windy regions are preferred [[3, 7, 4], [7, 11, 3], [11, 25, 2],[25, 100, 1]]
    windReclass = arcpy.sa.Reclassify(out_raster, "VALUE", windRemapRange)
    windReclass.save("wspd_Reclass")
    #arcpy.AddMessage("Wind Speed Raster Reclassified!") #Displaying completion message in black
    arcpy.AddMessage("Wind Speed Raster Reclassified!")

    #Calculate the final output suitability raster:
    output = "Suitability"
    Suitability = arcpy.sa.Int(w1 * slopeReclass + w2 * windReclass) #* landuseReclass
    Suitability.save(output)
    arcpy.AddMessage("Suitability Raster Created!") #Displaying completion message in black
    arcpy.AddMessage("Output Raster '%s' saved!"% output) #Displaying completion message in black


    ####Wetlands and Floodplains#####
    arcpy.AddMessage("***********************")
    #Clip/ mask out sutibility raster with vector of combined wetlands floodplains to exclude pixel values from area calculation

    # Create a feature layer from the feature class using the where clause
    feature_layer = "wetlandLayer"
    arcpy.MakeFeatureLayer_management(os.path.join(county_data_path,"VA_Wetlands"), feature_layer) #E:\GEOG656\Final\Virginia.gdb
    arcpy.AddMessage("Clipping wetland layer to extent of county: %s"% county_name)
    output_clip = "wetland_clip"
    wetland = arcpy.analysis.Clip(feature_layer, feature_layer_name, output_clip)

    #Disolving wetland layer
    outFeatureClass = "disolved_wetland"
    wetland = arcpy.management.Dissolve(wetland,outFeatureClass )


    #Creating symetric diffrence of wetlands and county of interest
    outdiff_name = "drymask"
    drymask = arcpy.analysis.SymDiff(feature_layer_name, wetland, outdiff_name, "ALL", 0.001)

    #Mask suitibility: using clip to remove wetland area from suitibility raster
    arcpy.AddMessage("Masking wetland area from suitability raster")

    ##using polygon geometry from selected county to clip raster
    out_raster = "new_suitability"
    new_suitability = arcpy.management.Clip(Suitability, drymask, out_raster, drymask,\
                          0, "ClippingGeometry", "NO_MAINTAIN_EXTENT")

    arcpy.AddMessage("Raster has been clipped!")


    arcpy.AddMessage("***********************")
    ######Read in parcel dataset as feature layer###
    #Define a where clause to select the state whose "NAME" is equal to the input state name.

    #Selecting parcels that intersect power constrains feature layer
    arcpy.AddMessage("Buffering power constrains: Transmission Lines, Power Plants, and Substations ")
    #Select parcels within user defined distance from transmission lines (0.5 miles)
    distanceField = "0.5 miles"
    transbuffer = arcpy.analysis.Buffer(os.path.join(county_data_path,"VA_TransmissionLines"), "transbuffer", distanceField, "", "", "ALL") #"E:\GEOG656\Final\Virginia.gdb\VA_TransmissionLines"

    #Select parcels within user defined distance from power plants (0.5 miles)
    distanceField = "0.5 miles"
    powerbuffer = arcpy.analysis.Buffer(os.path.join(county_data_path,"VA_PowerPlants"), "powerbuffer", distanceField, "", "", "ALL")

    #Select parcels within user defined distance from substations (3 miles)
    distanceField = "3 miles"
    stationsbuffer = arcpy.analysis.Buffer(os.path.join(county_data_path,"VA_Substations"), "stationsbuffer", distanceField, "", "", "ALL")
    arcpy.AddMessage("Merging and dissolving")
    #merging and disolving buffered power constraints
    output = "merged_power"
    power = arcpy.management.Merge([transbuffer,powerbuffer,stationsbuffer], output)
    #power = arcpy.management.Merge([transbuffer,powerbuffer,stationsbuffer], output)

    #Clip power lines to extent of selected county
    output_clip = "power_clip"
    feature_layer_name = "SelectedCountyLayer"
    power = arcpy.analysis.Clip(power, feature_layer_name, output_clip)

    #Disolving  layer
    outFeatureClass = "merged_power_disolved"
    power = arcpy.management.Dissolve(power,outFeatureClass)
    arcpy.AddMessage("Done")

    arcpy.AddMessage("***********************")
    #Create a feature layer from the feature class
    parcelLayer = "parcelLayer"
    arcpy.MakeFeatureLayer_management(os.path.join(county_data_path,"Parcels"), parcelLayer) #"E:\GEOG656\Final\Virginia.gdb\Parcels"
    parcelLayer = arcpy.management.SelectLayerByLocation(parcelLayer, 'INTERSECT', "SelectedCountyLayer")

    arcpy.AddMessage("Selecting parcels that intersect power constraints")
    out_feature_class = "selected"
    selected = arcpy.management.SelectLayerByLocation(parcelLayer, 'INTERSECT', power)
    selected = arcpy.management.CopyFeatures(selected,"selected_final")
    arcpy.AddMessage("DONE")

    #####Creating zonal histogram to calculate area of usable from assigned values (1 2 3 4) and total area in acres)##
    #Perform the intersection using Tabulate Intersection
    arcpy.AddMessage("Performing Zonal Histogram")
    intersect = final_output #output tabel 
    input_raster = "new_suitability" #input raster layer
    arcpy.sa.ZonalHistogram(selected, "PARCELID" , input_raster, intersect,"Count","ZONES_AS_ROWS")
    arcpy.AddMessage("Done")


    #Clearing up space after geoprocessing operation
    arcpy.management.Delete(["Wythe_dem","Wythe_DEM_clip","disolved_wetland", "Wythe_slope", "powerbuffer", "powerbuffer", "stationsbuffer"]) #intersect

    #Find the total usable area for the entire county / for each class
    if (area_units.lower() == 'acres'): # appling conversion formula based on input units
        cfactor = 0.000247105 #acres
        area_field = "Area_Ac"
    else:
        cfactor = 0.0001 #hectares
        # Add a new field to store calculated percentage
        area_field = "Area_Hc"
    arcpy.AddMessage("Cfactor: %s"%(cfactor)) #checking cfactor

    #Name of input table
    ps_table = final_output # "Parcel_Suitability"

    #Fields for calculated percent 
    class1_field = "class1_pr"
    class2_field = "class2_pr"
    class3_field = "class3_pr"
    class4_field = "class4_pr"

    #Adding new fields to table
    arcpy.management.AddField(ps_table, area_field, "DOUBLE")
    arcpy.management.AddField(ps_table, class1_field, "DOUBLE")
    arcpy.management.AddField(ps_table, class2_field, "DOUBLE")
    arcpy.management.AddField(ps_table, class3_field, "DOUBLE")
    arcpy.management.AddField(ps_table, class4_field, "DOUBLE")


    arcpy.AddMessage("Calculating area for each parcel class")	
    # Calculate the percentage of area with respect to the CLASS_1 field
    with arcpy.da.UpdateCursor(ps_table, [area_field, "CLASS_1", "CLASS_2", "CLASS_3", "CLASS_4",\
                                                     class1_field, class2_field, class3_field, class4_field,\
                                                     ]) as cursor:
        for row in cursor:
            #Calculate area in specified units
            total_area = (row[1] + row[2] + row[3] + row[4]) * 10**2 * cfactor #total area of parcel
            row[0] = total_area #updating area field
            if total_area != 0: #Skipping row field if area is 0 (small feature) 

                #Calculating percent of each class (1,2,3,4)
                row[5] = (((row[1] * 10**2) * cfactor) / total_area) * 100 #percent of total area for class 1
                row[6] = (((row[2] * 10**2) * cfactor) / total_area) * 100 #percent of total area for class 2
                row[7] = (((row[3] * 10**2) * cfactor) / total_area) * 100 #percent of total area for class 3
                row[8] = (((row[4] * 10**2) * cfactor) / total_area) * 100 #percent of total area for class 4
            
            cursor.updateRow(row)

except WeightError:
	arcpy.AddError("Incorrect weight parameter used")

except UnitError:
	#arcpy.AddWarning()
	arcpy.AddError("Incorrect unit parameter used")

