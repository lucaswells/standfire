#!python2
###############################################################################
#-----------#
# lidar.py  #
#-----------#

'''
This module implements all LiDAR processing tasks for STANDFIRE. This
includes creating a fishnet with 64x64m cells to divide the lidar points into
one acre plots, calculating FVS input variables, running FVS for each plot
and collating the results.

Inputs:
1) Lidar shapefile. Projected in WGS 1984 UTM (any zone). This shapefile
    needs to have the following attributes:
    - X coordinates: name- 'X_UTM', units- meters, type- float
    - Y coordinates: name- 'Y_UTM', units- meters, type- float
    - Tree height: name- 'Height_m', units- meters, type- float
    - Crown Base Height: name 'CBH_m', units- meters, type- float
    - Diameter at Breast Height: name- 'DBH_cm', units- centimeters, type- float
    - Tree species: name- 'Species', units- 2 letter FVS species code, type- text
2) FVS keyword file.

Outputs:
1) Fishnet shapefile containing the plots (*_fishnet.shp)
2) Lidar shapefile containing the input and calculated attributes (*_out.shp)
3) Text file containing the calculated attributes (*_export.csv)
4) FVS (*.tre and *.key) files for each plot
5) Tree list for CAPSIS (*_trees.csv)
'''
# meta
__authors__ = "Team STANDFIRE"
__copyright__ = "Copyright 2017, STANDFIRE"
__credits__ = ["Greg Cohn", "Brett Davis", "Matt Jolly", "Russ Parsons", "Lucas Wells"]
__license__ = "GPL"
__maintainer__ = "Brett Davis"
__email__ = "bhdavis@fs.fed.us"
__status__ = "Development"
__version__ = "1.1.1a"

# Import some modules
import timeit
import os
#import sys
#from os.path import dirname as dirname
#import subprocess
import shutil
import csv

import pandas as pd
from osgeo import ogr
ogr.UseExceptions()

# Below error handling not necessary if compiled
# try:
    # import pandas as pd
# except: # can't sys.exit. find another way to handle errors
    # sys.exit("ERROR: cannot find Pandas modules. Please ensure Pandas \n"
    # "package for Python is installed")
# try:#not necessary if standfire distributed as a 'frozen' binary.
    # from osgeo import ogr
    # from osgeo.gdal import __version__ as gdal_ver
# except:
    # sys.exit("ERROR: cannot find GDAL/OGR modules. Please ensure GDAL package\n"
    # " for Python is installed.")

# pd_ver_no = int((pd.__version__).replace(".",""))
# ##if pd_ver_no < 191: # 0.19.1 Development version November 2016
# ##    sys.exit("ERROR: Python bindings of Pandas 0.19.1 or later required")

# gdal_ver_no = int((gdal_ver).replace(".",""))
# # Might be able to get away with a older version, haven't tested.
# ##if gdal_ver_no < 213: # 2.1.3 Devel version January 2017
# ##    sys.exit("ERROR: Python bindings of GDAL 2.1.3 or later required")

class ConvertLidar(object):
    '''
    The ConvertLidar class is used to generate a CAPSIS tree list of lidar
    tree attributes from a shapefile of lidar trees.

    :param lidarShp: name and path of input lidar shapefile.
    :type: string
    :param fishnetShp: name and path for output fishnet shapefile.
    :type: string
    :param newLidar: name and path for output lidar shapefile.
    :type: string

    Methods:
        verify_projection
        verify_input_fields
        calculate_extents
        create_fishnet
        copy_shapefile
        cleanup_lidar_fields
        fishnet_id
        cleanup_lidar_features
        add_attribute_fields
        calculate_attribute_fields
        number_trees
        export_attributes_to_csv
    '''
    def __init__(self, lidarShp, fishnetShp, newLidar):
        '''
        Constructor

        Defines local variables that will be used by various methods below
        '''
        self.lidarShp = lidarShp
        self.fishnetShp = fishnetShp
        self.newLidar = newLidar
        self.set_path = os.path.dirname(lidarShp)

    def verify_projection(self):
        '''
        Verifies that the input shapefile is projected and, if so, whether the
            projection is WGS 1984 UTM. Uses EPSG projection codes to verify.
        '''
        EPSG_UTM = range(32600, 32661) # EPSG codes for UTM North zones
        EPSG_UTM.extend(range(32700, 32761)) # EPSG codes for UTM South zones
        ds = ogr.Open(self.lidarShp)
        lyr = ds.GetLayer()
        srs = lyr.GetSpatialRef()
        if srs is None:
            prjOk = False
            msg = ("Shapefile appears to be unprojected. Please project to WGS "
                   "1984 UTM and retry.")
            print msg
            code = 2
            ds = None
            print "ERROR: Shapefile unprojected"
            return prjOk, msg, code
        else:
            err = srs.AutoIdentifyEPSG()
            if err != 0:
                prjOk = False
                msg = ("Unable to identify projection. (Unexpected results may "
                       "occur if the shapefile is in the wrong projection)")
                print msg
                code = 1
                ds = None
            else:
                EPSG = srs.GetAuthorityCode(None)
                print "EPSG Authority code: ", EPSG
                EPSG = int(EPSG)
                ds = None
                if EPSG in EPSG_UTM:
                    prjOk = True
                    msg = "Projection appears to be WGS 1984 UTM as required"
                    code = 0
                else:
                    prjOk = False
                    msg = ("This shapefile doesn\'t appear to be in a WGS 1984 "
                           "UTM projection as required. (Unexpected results "
                           "may occur if the shapefile is in the wrong "
                           "projection)")
                    print msg
                    code = 1
            return prjOk, msg, code

    def verify_input_fields(self):
        '''
        Verifies that the required input fields are in the input shapefile.
        '''
        reqFields = ["X_UTM", "Y_UTM", "Height_m", "CBH_m", "DBH_cm", "Species"]
        misFields = []
        ds = ogr.Open(self.lidarShp)
        lyr = ds.GetLayer()
        lyrDefn = lyr.GetLayerDefn()
        inFields = [lyrDefn.GetFieldDefn(i).GetName()
                    for i in range(lyrDefn.GetFieldCount())]
        ds = None
        for req in reqFields:
            if req not in inFields:
                misFields.append(req)
        if misFields:
            fieldsOk = False
            msg = ("The following fields seem to be missing from the input lidar"
                   " shapefile. Please ensure these fields exist and are named "
                   "as shown above. Missing fields: \n" + ', '.join(misFields))
            print msg
        else:
            fieldsOk = True
            msg = "Required input fields appear to be present."
            print msg
        return fieldsOk, msg

    def calculate_extents(self):
        '''
        Calculates the minimum and maximum x and y extents of the input
        shapefile.

        Returns extents of the input shapefile as a list of four floating point
        numbers
        '''
        ds = ogr.Open(self.lidarShp, 0)
        lyr = ds.GetLayer()
        extents = lyr.GetExtent()
        extents = [round(x, 3) for x in extents]
        ds = None
        return extents

    def create_fishnet(self, extents):
        '''
        Creates a fishnet polygon shapefile to be used to assign plot
        numbers to the lidar points. Fishnet cells are 64x64m (~1 acre). Feature
        ID numbers are used to number plots

        Returns xySize- the x and y dimensions of the fishnet as a list of two
        integers
        '''
        drv = ogr.GetDriverByName("ESRI Shapefile")
        # dimensions
        xMin, xMax, yMin, yMax = extents
        gridWidth = 64
        gridHeight = 64
        cols = int((xMax-xMin)/gridWidth)
        rows = int((yMax-yMin)/gridHeight)
        # start grid cell envelope
        ringXleftOrigin = xMin
        ringXrightOrigin = xMin + gridWidth
        ringYtopOrigin = yMin + gridHeight
        ringYbottomOrigin = yMin
        # get projection from in shapefile
        prjDs = ogr.Open(self.lidarShp, 0)
        prjLyr = prjDs.GetLayer()
        prj = prjLyr.GetSpatialRef()
        prjDs = None
        # create output file
        if os.path.exists(self.fishnetShp):
            drv.DeleteDataSource(self.fishnetShp)
        outDs = drv.CreateDataSource(self.fishnetShp)
        # add projection below
        outLyr = outDs.CreateLayer(self.fishnetShp, srs=prj, geom_type=ogr.wkbPolygon)
        featureDefn = outLyr.GetLayerDefn()
        # create grid cells
        countcols = 0
        while countcols < cols:
            countcols += 1
            # reset envelope for rows
            ringYtop = ringYtopOrigin
            ringYbottom = ringYbottomOrigin
            countrows = 0
            while countrows < rows:
                countrows += 1
                ring = ogr.Geometry(ogr.wkbLinearRing)
                ring.AddPoint(ringXleftOrigin, ringYtop)
                ring.AddPoint(ringXrightOrigin, ringYtop)
                ring.AddPoint(ringXrightOrigin, ringYbottom)
                ring.AddPoint(ringXleftOrigin, ringYbottom)
                ring.AddPoint(ringXleftOrigin, ringYtop)
                poly = ogr.Geometry(ogr.wkbPolygon)
                poly.AddGeometry(ring)
                # add new geom to layer
                outFtr = ogr.Feature(featureDefn)
                outFtr.SetGeometry(poly)
                outLyr.CreateFeature(outFtr)
                outFtr = None
                # new envelope for next poly
                ringYtop = ringYtop + gridHeight
                ringYbottom = ringYbottom + gridHeight
            # new envelope for next poly
            ringXleftOrigin = ringXleftOrigin + gridWidth
            ringXrightOrigin = ringXrightOrigin + gridWidth
        # Save and close DataSources
        outDs = None
        xySize = [cols*64, rows*64]
        print "Fishnet created"
        return xySize

    def copy_shapefile(self):
        '''
        Makes an exact copy of a shapefile.
        '''
        # set shapefile names
        in_shp = self.lidarShp
        out_shp = self.newLidar

        # start timer
        copy_start = timeit.default_timer()

        # get driver
        drv = ogr.GetDriverByName("ESRI Shapefile")

        # open input shapefile and extract information
        in_ds = drv.Open(in_shp, 0)
        in_lyr = in_ds.GetLayer()
        lyr_def = in_lyr.GetLayerDefn()
        lyr_geom = in_lyr.GetGeomType()
        prj = in_lyr.GetSpatialRef()

        # delete output shapefile if it exists
        if os.path.exists(out_shp):
            del_ok = drv.DeleteDataSource(out_shp) #returns flag
            if del_ok == 0:
                print "Deleted old LiDAR out shapefile"

        # create out shapefile
        out_ds = drv.CreateDataSource(out_shp)
        out_lyr = out_ds.CreateLayer(out_shp.split(".")[0], prj, lyr_geom)

        # add fields from input shapefile to output shapefile
        cfld_ok = 0
        field_cnt = lyr_def.GetFieldCount()
        for i in range(field_cnt):
            cfld_ok += out_lyr.CreateField(lyr_def.GetFieldDefn(i)) #returns flag
            if cfld_ok != 0:
                msg = ("Problems creating fields in out LiDAR shapefile. OGR "
                       "CreateField error = ", cfld_ok)
                copy_ok = False
                in_ds = None
                out_ds = None
                return copy_ok, msg
        out_lyr.ResetReading()

        # create output shapefile features
        for in_feat in in_lyr:
            out_feat = ogr.Feature(lyr_def)
            for i in range(field_cnt):
                out_feat.SetField(lyr_def.GetFieldDefn(i).GetNameRef(), in_feat.GetField(i))
            try:
                cftr_ok = out_lyr.CreateFeature(in_feat)
            except:
                msg = ("Problem creating features in out LiDAR shapefile. OGR "
                       "CreateFeatrure error = ", cftr_ok)
                copy_ok = False
                in_ds = None
                out_ds = None
                return copy_ok, msg
            out_feat = None # dereference feature
            in_feat = None

        # ogr cleanup and save shapefile
        in_lyr = None
        in_ds = None
        out_lyr = None
        out_ds = None

        # end timer
        copy_time = timeit.default_timer() - copy_start
        print "\nCreate output shapefile took ", copy_time, " to run."

        # return messages
        msg = "Created initial LiDAR out shapefile"
        copy_ok = True
        return copy_ok, msg

    def cleanup_lidar_fields(self):
        '''
        Deletes extraneous fields from output shapefile
        '''
        # define input shapefile
        pt_shp = self.newLidar

        # start timer
        cleanup_start = timeit.default_timer()

        # required input fields
        pt_req_in_flds = ["FID", "Shape", "X_UTM", "Y_UTM", "Height_m", "CBH_m",
                          "DBH_cm", "Species"]

        # get driver
        drv = ogr.GetDriverByName("ESRI Shapefile")

        # open lidar point shapefile
        pt_ds = drv.Open(pt_shp, 1)
        pt_lyr = pt_ds.GetLayer()

        # get lidar point field names
        pt_lyr_def = pt_lyr.GetLayerDefn()
        pt_nmbr_flds = range(pt_lyr_def.GetFieldCount())
        pt_fld_nms = [pt_lyr_def.GetFieldDefn(i).GetName() for i in pt_nmbr_flds]

        # delete extraneous lidar point fields
        for in_fld in pt_fld_nms:
            if in_fld not in pt_req_in_flds:
                del_fld_idx = pt_lyr_def.GetFieldIndex(in_fld)
                dflds_ok = pt_lyr.DeleteField(del_fld_idx) # returns flag
                if dflds_ok != 0:
                    clf_ok = False
                    msg = ("Problem deleting extraneous fields from output "
                           "shapefile. OGR DeleteField error: ", dflds_ok)
                    return clf_ok, msg

        # save and refresh data sources, layers and layer definitions
        pt_lyr_def = None
        pt_lyr = None
        pt_ds = None

        cleanup_time = timeit.default_timer() - cleanup_start
        print "\nCleanup lidar fields function took ", cleanup_time, " to run."
        msg = "Deleted extraneous fileds from output shapefile"
        clf_ok = True
        return clf_ok, msg

    def fishnet_id(self):
        '''
        Assigns a fishnet based plot ID number to each tree in the output
        shapefile
        '''
        # define input shapefiles
        pt_shp = self.newLidar
        poly_shp = self.fishnetShp

        # start timer
        fishID_start = timeit.default_timer()

        # get driver
        drv = ogr.GetDriverByName("ESRI Shapefile")

        # open lidar point shapefile
        pt_ds = drv.Open(pt_shp, 1)
        pt_lyr = pt_ds.GetLayer()

        # add fishnet ID field to lidar out shapefile
        fish_field = ogr.FieldDefn("Plot_ID", ogr.OFTInteger)
        pt_lyr.CreateField(fish_field)

        # set all initial fishnet ID values to -9999
        for feat in pt_lyr:
            feat.SetField("Plot_ID", -9999)
            pt_lyr.SetFeature(feat)
        pt_lyr.ResetReading() # prob not necessary now...

        # save and refresh data sources and layers
        pt_lyr = None
        pt_ds = None
        pt_ds = drv.Open(pt_shp, 1)
        pt_lyr = pt_ds.GetLayer()

        # open fishnet shapefile
        poly_ds = drv.Open(poly_shp, 0)
        poly_lyr = poly_ds.GetLayer()

        # get field index for fishnet FID field
        fish_id = poly_lyr.GetLayerDefn().GetFieldIndex("FID")
        fish_id_list = []

        for feat in pt_lyr:
            # get XY coordinates for points in the lidar shapefile
            geom = feat.GetGeometryRef()
            mx, my = geom.GetX(), geom.GetY()
            # create single point to filter fishnet
            pt = ogr.Geometry(ogr.wkbPoint)
            pt.AddPoint(mx, my)
            # filter fishnet features by point location
            poly_lyr.SetSpatialFilter(pt)
            # extract fishnet ID number and add to lidar point attributes
            # loop doesn't execute when the point falls outside fishnet
            for poly_feat in poly_lyr:
                FID = int(poly_feat.GetFieldAsInteger(fish_id))
                feat.SetField("Plot_ID", FID)
                pt_lyr.SetFeature(feat)
                fish_id_list.append(FID) #testing
            poly_lyr.SetSpatialFilter(None)
        pt_lyr.ResetReading() # prob not necessary now...

        # save and close layers and data sources
        pt_lyr = None
        pt_ds = None
        poly_lyr = None
        poly_ds = None

        # print some statistics
        print "\nLength of fish ID list is: " + str(len(fish_id_list))
        print "Unique values in fish ID list: "
        print sorted(set(fish_id_list))

        fishID_time = timeit.default_timer() - fishID_start
        print "Fishnet ID function took ", fishID_time, " to run."
        return

    def cleanup_lidar_features(self):
        '''
        Deletes features outside the fishnet area
        '''
        # get path and layer name for output shapefile
        pt_shp = self.newLidar
        lyr_name = os.path.basename(pt_shp)[:-4]

        # start timer
        del_features_start = timeit.default_timer()

        # get driver
        drv = ogr.GetDriverByName("ESRI Shapefile")

        # open lidar point shapefile
        pt_ds = drv.Open(pt_shp, 1)
        pt_lyr = pt_ds.GetLayer()

        # get number of input features
        pt_nmbr_in_ftrs = pt_lyr.GetFeatureCount()

        # delete features outside the fishnet
        pt_lyr.SetAttributeFilter("Plot_ID = '-9999'")
        for feat in pt_lyr:
            del_feats = feat.GetFID()
            pt_lyr.DeleteFeature(del_feats)
            feat = None

        # shapefile needs to be 'repacked' before the features will actually be deleted
        pt_lyr = None
        pt_ds = None
        pt_ds = drv.Open(pt_shp, 1)
        pt_ds.ExecuteSQL('repack ' + lyr_name)

        # calculate the numer of features deleted
        pt_lyr = pt_ds.GetLayer()
        pt_nmbr_out_ftrs = pt_lyr.GetFeatureCount()
        pt_nmbr_del_ftrs = pt_nmbr_in_ftrs - pt_nmbr_out_ftrs

        # save and close shapefile
        pt_lyr = None
        pt_ds = None

        # print deleted feature count
        print pt_nmbr_del_ftrs, " features fell outside the fishnet and were deleted."

        del_features_time = timeit.default_timer() - del_features_start
        print "Point file feature cleanup function took ", del_features_time, " to run."
        return

    def add_attribute_fields(self):
        '''
        Adds and defines new attribute fields
        '''
        newFields = {
            "POINT_X": ogr.OFTReal,
            "POINT_Y": ogr.OFTReal,
            "CR_code": ogr.OFTInteger,
            "DBH_in_x10": ogr.OFTInteger,
            "Height_ft": ogr.OFTInteger,
            "Tree_ID": ogr.OFTInteger
        }
        ds = ogr.Open(self.newLidar, update=True)
        lyr = ds.GetLayer()
        lyrDefn = lyr.GetLayerDefn()
        fieldNames = [lyrDefn.GetFieldDefn(i).GetName()
                      for i in range(lyrDefn.GetFieldCount())]
        for key in newFields:
            if key not in fieldNames:
                new = ogr.FieldDefn(key, newFields[key])
                lyr.CreateField(new)
            else:
                print key + " field already exists"
        ds = None
        return

    def calculate_attribute_fields(self):
        '''
        Calculates values for the attribute fields added in the
        'add_attribute_fields' method above.

        inOutCols contains input and output field names and conversion formulas
        inOutcols = {<outfield>: [<infield>, <formula>],
                      ...
                      }
            Height- converts from meters to feet and rounds to integer

            CR_code- calculates crown ratio while accounting for anomolous data
            where CBH is >= Height. Then classifies the crown ratio into FVS
            categories.
                crown ratio = (height - crown base height)/height)
                FVS crown ratio codes: 1: 0-10%; 2: 11-20%;...; 9: 81-100%

            DBH - converts from centimeters to inches*10 and rounds to integer
        '''
        inOutCols = {
            "POINT_X": ["X_UTM", "%s*1"],
            "POINT_Y": ["Y_UTM", "%s*1"],
            "Height_ft": ["Height_m", "int((%s*3.281)+0.5)"],
            "CR_code": ["Height_m", "CBH_m", "0.0001 if (%s-%t) <= 0 else "
                        "((%s-%t)/%s)", "9 if %s >= 0.8 else int((%s - "
                        "0.000001)*10)+1"],
            "DBH_in_x10": ["DBH_cm", "int((%s*3.937)+0.5)"]
        }
        ds = ogr.Open(self.newLidar, 1)
        lyr = ds.GetLayer()
        for ftr in lyr:
            for key in inOutCols:
                if key == "CR_code":
                    inVal0 = ftr.GetField(inOutCols[key][0]) #Height_m
                    inVal1 = ftr.GetField(inOutCols[key][1]) #CBH_m
                    inForm1 = inOutCols[key][2]
                    inForm2 = inOutCols[key][3]
                    cR = eval(inForm1.replace("%s", str(inVal0)).replace("%t", str(inVal1)))
                    val = eval(inForm2.replace("%s", str(cR)))
                    ftr.SetField(key, val)
                else:
                    inVal = ftr.GetField(inOutCols[key][0])
                    inForm = inOutCols[key][1]
                    val = eval(inForm.replace("%s", str(inVal)))
                    ftr.SetField(key, val)
            err = lyr.SetFeature(ftr)
            if err != 0:
                print "Calculate attribute fields problem. err, key, val", err, key, val
        ds = None
        return

    def number_trees(self):
        '''
        Numbers trees within each plot. The combination of plot ID and tree Id
        constitutes a unique identifier for each tree in the simulation.
        '''
        ds = ogr.Open(self.newLidar, 1)
        lyr = ds.GetLayer()
        field_vals = []
        for ftr in lyr:
            field_vals.append(ftr.GetFieldAsInteger("Plot_ID"))
        plots = list(set(field_vals))
        lyr.ResetReading()
        x = 1
        for p in plots:
            eq = "Plot_ID = " + str(p)
            err1 = lyr.SetAttributeFilter(eq)
            if err1 != 0:
                print "Set attribute feature problem. err1, p, eq, x", err1, p, eq, x
            for ftr in lyr:
                ftr.SetField("Tree_ID", x)
                err2 = lyr.SetFeature(ftr)
                if err2 != 0:
                    print "Set Tree_ID problem. err2, p, eq, x", err2, p, eq, x
                x += 1
            print str(x-1) + " trees numbered in plot " + str(p)
            x = 1
        ds = None
        return

    def export_attributes_to_csv(self, lidarCsv):
        '''
        Exports select attributes in the new lidar shapefile to a text (.csv)
        file. Exported attributes are listed in the 'outFields' variable
        assignment below.

        :param lidarCsv - name and path for output text file
        :type lidarCsv: string
        '''
        #Export select fields to csv file
        outFields = ["FID", "POINT_X", "POINT_Y", "Species", "CR_code",
                     "DBH_in_x10", "Height_ft", "Plot_ID", "Tree_ID"]
        with open(lidarCsv, "w") as lidarCsv:
            csvwriter = csv.writer(lidarCsv, delimiter=",", lineterminator="\n")
            csvwriter.writerow(outFields)
            outFields.remove("FID")
            ds = ogr.Open(self.newLidar, 0)
            lyr = ds.GetLayer()
            for ftr in lyr:
                attributes = []
                attributes.append(ftr.GetFID())
                for f in outFields:
                    attributes.append(ftr.GetField(f))
                csvwriter.writerow(attributes)
            lidarCsv.close()
            ds = None
        return
###End class 'ConvertLidar'###

class FVSFromLidar(object):
    '''
    Creates FVS tree lists (*.tre) and keyword files (*.key), runs FVS for
    each 64x64m (~1 acre) lidar plot and creates a tree list for CAPSIS.

    :param fuel: FVS fuels object. Specific to a single FVS variant.
    :type fuel: object
    :param lidarCsv: path and file name of input text file (generated by the
                    ConvertLidar class above (export_attributes_to_csv method)
    :type lidarCsv: string
    :param keywordFile: path and file name of the 'master' FVS keyword file.
    :type keywordFile: string

    Methods:
        run_FVS_lidar
        create_capsis_csv
    '''

    def __init__(self, fuel, lidarCsv, keywordFile):
        '''
        Constructor

        Defines local variables and objects that will be used by methods below
        '''
        self.fuel = fuel # fuels object
        self.lidarCsv = lidarCsv
        self.keywordFile = keywordFile
        self.set_path = os.path.dirname(lidarCsv)

    def run_FVS_lidar(self):
        '''
        Creates FVS input files (.key and .tre) from lidar tree list generated
        in the export_attributes_to_csv method in the ConvertLidar class. Uses
        these files to run FVS for each lidar subset/plot.

        :returns fvsCsv: filename and path for a collated (from subsets/plots)
            FVS results file. Only the filename is generated in this method.
            The file itself will be collated in the create_capsis_csv method.
        :type fvsCsv: string
        '''
        FVS_start = timeit.default_timer()
        workDir = os.path.dirname(self.keywordFile)
        # Read lidar data into pandas data frame
        df = pd.read_csv(self.lidarCsv)
        plots = sorted(df.Plot_ID.unique())
        # Empty or unchanging .tre variables
        prob = "".ljust(6) # Tree_count
        ith = "0" # Tree_history
        dg = "".ljust(3) # DBH_increment
        tht = "".ljust(3) # Height_to_top-kill
        htg = "".ljust(4) # Height_increment
        theRest = "".ljust(27) # All variables after Crown_ratio_code
        # Get column index by name. Safer than by index order if the order in
        #   the file changes...
        itreC = df.columns.get_loc("Plot_ID")
        idtreeC = df.columns.get_loc("Tree_ID")
        ispC = df.columns.get_loc("Species")
        dbhC = df.columns.get_loc("DBH_in_x10")
        htC = df.columns.get_loc("Height_ft")
        icrC = df.columns.get_loc("CR_code")
        # Loop through each subset/plot to create .tre files and run FVS
        for p in plots:
            dfSub = df[df.Plot_ID == p]
            numRecords = len(dfSub.index)
            treLines = [] # Initialize list variable to store FVS tree data
            treFileName = workDir+"/subset"+str(p)+".tre" # FVS subset tree file
            treFile = open(treFileName, "w")
            # Loop through records in subset's data frame and extract variables
            for y in range(0, numRecords):
                itre = str(dfSub.iat[y, itreC]).ljust(4) # Plot_ID
                idtree = str(dfSub.iat[y, idtreeC]).ljust(3) # Tree_ID
                isp = str(dfSub.iat[y, ispC]).ljust(3) # Species
                dbh = str(dfSub.iat[y, dbhC]).ljust(4) # DBH
                ht = str(dfSub.iat[y, htC]).ljust(3) # Live_height
                icr = str(dfSub.iat[y, icrC]) # Crown_ratio_code
                # Merge variables and spaces into one long string
                treLine = itre+idtree+prob+ith+isp+dbh+dg+ht+tht+htg+icr+theRest+"\n"
                treLines.append(treLine) # Add to list variable
            treFile.writelines(treLines) # Write all lines to subset's .tre file
            treFile.close() # .tre file for each subset
            # .key file for each subset (identical to master key)
            shutil.copy(self.keywordFile, treFileName[0:-4]+".key")
            keyFile = treFileName[0:-4]+".key"
            self.fuel.set_keyword(keyFile)
            # Start FVS simulation
            self.fuel.run_fvs() # FVS for each subset
            # Base name for output .csv file. e.g. STANDFIRE_ex. From .key file
            svs_base = self.fuel.get_standid()
            # Writes subset .csv file containg tree variables for CAPSIS
            self.fuel.save_trees_by_year(2010)
            fvsCsv = self.fuel.wdir+svs_base+"_2010_trees.csv"
            subOut = fvsCsv[0:-4]+"_subset"+str(p)+".csv"
            if os.path.exists(subOut):
                os.remove(subOut)
            os.rename(fvsCsv, subOut) # Renames .csv file with the subset name.
        FVS_elapsed = timeit.default_timer() - FVS_start
        print "FVS runs took: "+str(round(FVS_elapsed, 3))+" seconds."
        return fvsCsv

    def create_capsis_csv(self, xyOrig, fvsCsv):
        '''
        Creates a capsis input file from FVS subset/plot output files generated
        by the run_FVS_lidar method above. Calculates adjusted xy coordinates for
        each tree (i.e. each plot's coordinates need to be adjusted depending on
        its position amoungst all plots). For example, Each of the six 64x64m
        plots illustrated below were modeled seperately in FVS. As a
        consequence, they each have coordinates with a 0,0 origin in their lower
        left corners. This method adjusts the coordinates of plots 1-5 so their
        origin is now the lower left corner of plot 0 (original input lidar
        shapefile's origin location).

                         _____________________________
                     128|         |         |         |
                        |    3    |    4    |    5    |
                        |         |         |         |
                        |_________|_________|_________|
                      64|         |         |         |
                        |    0    |    1    |    2    |
                        |         |         |         |
                        |_________|_________|_________|
                       0          64       128       192

        :param xyOrig: xy origin of the original input lidar shapefile in UTM
            coordinates.
        :type xyOrig: list of two floats
        :param fvsCsv: filename and path for the collated (from subsets/plots)
            FVS results file.
        :type fvsCsv: string
        '''
        # Create merged _trees.csv with adjusted coordinates for input into CAPSIS
        colNames = ["xloc", "yloc", "species", "dbh", "ht", "crd", "cratio",
                    "crownwt0", "crownwt1", "crownwt2", "crownwt3"]
        #Create data frame from lidar data to obtain original UTM xy coordinates
        dfLidar = pd.read_csv(self.lidarCsv)
        df = pd.DataFrame(columns=colNames) # Initialize empty data frame
        plots = sorted(dfLidar.Plot_ID.unique())
        for p in plots:
            treeSubFile = fvsCsv[:-4]+"_subset"+str(p)+".csv"
            dfTrees = pd.read_csv(treeSubFile) # Data frame for subset
            dfLidarSub = dfLidar[dfLidar.Plot_ID == p]
            # Need index numbers for both data frames to match up
            dfLidarSub.reset_index(drop=True, inplace=True)
            # Subtract original UTM origin from original tree location to get xy
            # coordinate system whose origin is 0,0 and whose units are now feet
            dfTrees.xloc = ((dfLidarSub.POINT_X - xyOrig[0])*3.28)
            dfTrees.yloc = ((dfLidarSub.POINT_Y - xyOrig[1])*3.28)
            dfTrees.xloc = dfTrees.xloc.apply(lambda x: round(x, 3))
            dfTrees.yloc = dfTrees.yloc.apply(lambda x: round(x, 3))
            # Append subset data frame to set data frame
            df = df.append(dfTrees, ignore_index=True)
            # Convert set data frame to set *_trees.csv
        df.to_csv(fvsCsv, index=False, quoting=csv.QUOTE_NONNUMERIC)