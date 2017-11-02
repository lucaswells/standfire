#!python2
################################################################################
#-----------#
# capsis.py #
#-----------#

"""
This module is a Python wrapper for the Capsis Standfire suite. Currently
Capsis' role in Standfire is to distribute the fuels present in
the files generated by Fvsfuels. Capsis uses a pre-generated FDS grid file (.xyz)
to place canopy and surface in a user defined domain. Capsis provides many options
for placing these fuels. The pertenant arguments can be controlled through
the Capsis RunConig class. The Execute class is used to run Capsis. An up-to-date
Java installation is required since Capsis runs on a Java Virtual Machine.

"""

# meta
__authors__ = "Team STANDFIRE"
__copyright__ = "Copyright 2015, STANDFIRE"
__credits__ = ["Greg Cohn","Brett Davis","Matt Jolly","Russ Parsons","Lucas Wells"]
__license__ = "GPL"
__maintainer__ = "Lucas Wells"
__email__ = "bluegrassforestry@gmail.com"
__status__ = "Development"
__version__ = "1.1.3a" # Previous version: '1.1.2a'

# module imports
import os
from shutil import copyfile, rmtree
from wfds import GenerateBinaryGrid
import subprocess
import platform
import random

class RunConfig(object):
    """
    The Capsis RunConfig class is used to configure a capsis run.

    :param run_directory: desired path for Capsis run
    :run_directory type: string

    *Example:#

    >>> import capsis
    >>> config = capsis.RunConfig('/path/to/capsis_run/')
    >>> config.set_xy_size(160,90,64,64)
    >>> config.set_svs_base('stand_0001')
    >>> config.set_crown_space(1.5)
    >>> config.set_show3d('true')
    >>> config.save_config()

    """

    def __init__(self, run_directory):
        """
        Constructor
        """

        self.run_directory = run_directory
        self.set_path = run_directory

        this_dir = os.path.dirname(os.path.abspath(__file__))
		# B -to run in python interpreter
        #this_dir = 'C:/Users/bhdavis/Documents/STANDFIRE/source_code/standfire-master/standfire'

        # default parameters
        self.params = {'path'                     : run_directory,
                       'speciesFile'              : '/speciesFile.txt',
                       'svsBaseFile'              : '',
                       'additionalProperties'     : '/additionalProperties.txt',
                       'sceneOriginX'             : 0.0,
                       'sceneOriginY'             : 0.0,
                       'sceneSizeX'               : 0, #B change from default 160
                       'sceneSizeY'               : 0,  # and 90 (64x64m run)
                       'sceneSizeZ'               : 100,
                       'show3d'                   : 'false',
					   #B change below to false. Dependent upon whether sample != scene
                       'extend'                   : 'false', #B Defaults for lidar
                       'xOffset'                  : 0.0, #B- change from default 83.0
                       'yOffset'                  : 0.0, # and 13.0 (64x64m run)
                       'spatialOpt'               : 0,
                       'respace'                  : 'false',
                       'respaceDistance'          : 0.0,
                       'prune'                    : 'false',
                       'pruneHeight'              : 0.0,
                       'format'                   : 86,
                       'litter'                   : 'true',
                       'leaveLive'                : 'true',
                       'leaveDead'                : 'true',
                       'twig1Live'                : 'false',
                       'twig1Dead'                : 'false',
                       'twig2Live'                : 'false',
                       'twig2Dead'                : 'false',
                       'twig3Live'                : 'false',
                       'twig3Dead'                : 'false',
                       'canopyGeom'               : 'CYLINDER', #B change from 'RECTANGLE'
                       'layerGeom'                : 'HET_RECTANGLE_TEXT', # B new - for heterogeneous surface fuels
                       'bdBin'                    : 0.01, #B change from '0.1'
                       'firstGridFile'            : 'grid.xyz',
                       'gridNumber'               : 1,
                       'gridResolution'           : 1.0,
                       'vegetation_cdrag'         : 0.5,
                       'vegetation_char_fraction' : 0.2,
                       'emissivity'               : 0.99,
                       'degrad'                   : 'false',
                       'mlr'                      : 0.35,
                       'init_temp'                : 30.0,
                       'veg_char_fraction'        : 0.25,
                       'veg_drag_coefficient'     : 0.125,
                       'burnRateMax'              : 0.4,
                       'dehydration'              : 0.4,
                       'rmChar'                   : 'true',
                       'outDir'                   : '/output/',
                       'fileName'                 : 'capsis_fuels.txt', # capsis out file
                       'srf_blocks': {1: [[0,0],[0,0],[0,0],[0,0]],
                                      2: [[0,0],[0,0],[0,0],[0,0]],
                                      3: [[0,0],[0,0],[0,0],[0,0]],
                                      4: [[0,0],[0,0],[0,0],[0,0]],
                                      5: [[0,0],[0,0],[0,0],[0,0]],
                                      6: [[0,0],[0,0],[0,0],[0,0]]},
                        #B changed to match mini-interface surface fuel parameter defaults
                       'srf_fuels' : {'shrub' : {'ht'        : 0.35,
                                                 'cbh'       : 0.0,
                                                 'cover'     : 0.5,
                                                 'width'     : 5.0,
                                                 'spat_group': 1,
                                                 'live' : {'load'    : 0.72,
                                                           'mvr'     : 500,
                                                           'svr'     : 5000,
                                                           'moisture': 100},
                                                 'dead' : {'load'    : 0.08,
                                                           'mvr'     : 500,
                                                           'svr'     : 5000,
                                                           'moisture': 40}},
                                       'herb' : {'ht'        : 0.35,
                                                 'cbh'       : 0.0,
                                                 'cover'     : 0.8,
                                                 'width'     : 1.0,
                                                 'spat_group': 1,
                                                 'live' : {'load'    : 0.0,
                                                           'mvr'     : 500,
                                                           'svr'     : 5000,
                                                           'moisture': 100},
                                                 'dead' : {'load'    : 0.8,
                                                           'mvr'     : 500,
                                                           'svr'     : 5000,
                                                           'moisture': 5}},
                                        'litter' : {'ht'        : 0.1,
                                                    'cbh'       : 0.0,
                                                    'cover'     :1.0,
                                                    'width'     : -1,
                                                    'spat_group': 0,
                                                    'load'      : 0.5,
                                                    'mvr'       : 500,
                                                    'svr'       : 2000,
                                                    'moisture'  : 10}}}


	#B not currently used (offsets calculated and set below)
    def set_x_offset(self, offset):
        """
        Set the x offset of the area of analysis

        :param offset: x offset of the AOA
        :offset type: integer
        """
        self.params['xOffset'] = offset

	#B not currently used (offsets calculated and set below)
    def set_y_offset(self, offset):
        """
        Set the y offset of the area of analysis

        :param offset: y offset of the AOA
        :offset type: integer
        """
        self.params['yOffset'] = offset

    def set_show3D(self, value):
        """
        Set the boolean value of the show3D parameter in the Capsis run file. If
        true, Capsis will open a 3D displaying the simulation domain.

        :param value: Truth value of the show3D parameter
        :value type: boolean
        """
        self.params['show3d'] = value

    def set_crown_space(self, space):
        """
        Set the distance between crown for Capsis intervention

        :param space: crown spacing in meters
        :space type: float
        """
        if space != 0:
            self.params['respace'] = 'true'
            self.params['respaceDistance'] = space

    def set_prune_height(self, prune):
        """
        Set the prunning height (vertical spacing between ground and crown)
        for a Capsis intervention

        :param prune: prunning height
        :prune type: float
        """

        if prune != 0:
            self.params['prune'] = 'true'
            self.params['pruneHeight'] = prune

    def set_srf_height(self, shrub_ht, herb_ht, litter_ht):
        """
        """
        self.params['srf_fuels']['shrub']['ht'] = shrub_ht
        self.params['srf_fuels']['herb']['ht'] = herb_ht
        self.params['srf_fuels']['litter']['ht'] = litter_ht

    def set_srf_cbh(self, shrub_cbh, herb_cbh):
        """
        """
        self.params['srf_fuels']['shrub']['cbh'] = shrub_cbh
        self.params['srf_fuels']['herb']['cbh'] = herb_cbh

    def set_srf_cover(self, shrub_cover, herb_cover, litter_cover):
        """
        """
        self.params['srf_fuels']['shrub']['cover'] = shrub_cover
        self.params['srf_fuels']['herb']['cover'] = herb_cover
        self.params['srf_fuels']['litter']['cover'] = litter_cover

    def set_srf_patch(self, shrub_patch, herb_patch, litter_patch): #B
        """
        """
        self.params['srf_fuels']['shrub']['width'] = shrub_patch
        self.params['srf_fuels']['herb']['width'] = herb_patch
        self.params['srf_fuels']['litter']['width'] = litter_patch

    def set_srf_live_svr(self, shrub_svr, herb_svr):
        """
        """
        self.params['srf_fuels']['shrub']['live']['svr'] = shrub_svr
        self.params['srf_fuels']['herb']['live']['svr'] = herb_svr

    def set_srf_dead_svr(self, shrub_svr, herb_svr, litter_svr):
        """
        """
        self.params['srf_fuels']['shrub']['dead']['svr'] = shrub_svr
        self.params['srf_fuels']['herb']['dead']['svr'] = herb_svr
        self.params['srf_fuels']['litter']['svr'] = litter_svr

    def set_srf_live_load(self, shrub_load, herb_load):
        """
        """
        self.params['srf_fuels']['shrub']['live']['load'] = shrub_load
        self.params['srf_fuels']['herb']['live']['load'] = herb_load

    def set_srf_dead_load(self, shrub_load, herb_load, litter_load):
        """
        """
        self.params['srf_fuels']['shrub']['dead']['load'] = shrub_load
        self.params['srf_fuels']['herb']['dead']['load'] = herb_load
        self.params['srf_fuels']['litter']['load'] = litter_load

    def set_srf_live_mc(self, shrub_mc, herb_mc):
        """
        """
        self.params['srf_fuels']['shrub']['live']['moisture'] = shrub_mc
        self.params['srf_fuels']['herb']['live']['moisture'] = herb_mc

    def set_srf_dead_mc(self, shrub_mc, herb_mc, litter_mc):
        """
        """
        self.params['srf_fuels']['shrub']['dead']['moisture'] = shrub_mc
        self.params['srf_fuels']['herb']['dead']['moisture'] = herb_mc
        self.params['srf_fuels']['litter']['moisture'] = litter_mc

    def set_path(self, path):
        """
        Sets path to Capsis run directory

        :param path: path to Capsis run directory
        :type path: string

        """

        if os.path.isdir(path):
            self.params['path'] = path
        else:
            print "ERROR: " + path + " is not a directory"

    def set_svs_base(self, base_name):
        """
        Sets the base file name for FVS/SVS fuel output files

        :param base_name: base file name for fuel output files
        :type base_name: string

        .. note:: Only the tree.csv file is required. If snags, cwd and scalar
                  files exist in the same directory they will be used by
                  Capsis when writing WFDS fuel inputs.

        """

        if os.path.isfile(os.path.join(self.params['path'], base_name + '_trees.csv')):
            self.params['svsBaseFile'] = base_name
        else:
            print "ERROR: " + base_name + "does not exist in " + self.params['path']

    def set_extend_FVS_sample(self, bExtend):
        """
        Resets CAPSIS extend to true. This will cause CAPSIS to add additional trees to
        its landscape based on the FVS input tree list pattern. This should only be
        implemented when the sample doesn't cover the whole scene (e.g. not for lidar
        data)

        :param bExtend: Truth value of the extend parameter
        :type bExtend: boolean
        """
        if bExtend:
            self.params['extend'] = 'true'
        else:
            self.params['extend'] = 'false'

    def set_xy_size(self, x_size, y_size, x_AOI_size, y_AOI_size):
        """
        Sets scene and Area Of Interest (AOI) dimensions. Calls methods to
        update offset and surface fuel block values

        :param x_size: size of scene in the x domain (meters)
        :type x_size: integer
        :param y_size: size of scene in the y domain (meters)
        :type y_size: integer
        :param x_AOI_size: area of interest size in the x domain
        :type x_AOI_size : integer
        :param y_AOI_size: area of interest size in the y domain
        :type y_AOI_size: integer

        .. note: `x_size` and 'y_size' must be greater than or equal to 64 meters
        .. note: 'x_AOI_size' and 'y_AOI_size' must be at least 2 meters less than
            x and y sizes

        """
        if x_size < 64:
            print "Scene X dimension must be greater than or equal to 64 meters"
            return -1
        else:
            self.params['sceneSizeX'] = x_size

        if y_size < 64:
            print "Scene Y dimension must be greater than or equal to 64 meters"
            return -1
        else:
            self.params['sceneSizeY'] = y_size

        if x_size - x_AOI_size < 2:
            #print "Scene X dimension: ",x_size,"; AOI X dimension: ",x_AOI_size
            x_AOI_size = x_size - 2
            #print "AOI X dimension must be at least 2 meters less than Scene X dimension\n"
            #print "Reset AOI X dimension to: ",x_AOI_size,"\n"

        if y_size - y_AOI_size < 2:
            #print "Scene Y dimension: ",y_size,"; AOI Y dimension: ",y_AOI_size
            y_AOI_size = y_size - 2
            #print "AOI Y dimension must be at least 2 meters less than Scene Y dimension\n"
            #print "Reset AOI Y dimension to: ",y_AOI_size,"\n"

        # update offset and block verts
        self._set_x_offset(x_AOI_size, y_AOI_size)
        self._set_y_offset(x_AOI_size, y_AOI_size)
        self._set_block_verts(x_AOI_size, y_AOI_size)

    def set_z_size(self, z_size):
        """
        Sets scene z dimension

        :param z_size: size of scene in the z domain (meters)
        :type z_size: integer

        .. note:: `z_size` must be greater than or equal to tallest tree in domain

        """

        self.params['sceneSizeZ'] = z_size

    def _set_x_offset(self, x_AOI_size, y_AOI_size):
        """
        Private method
        """

        x = self.params['sceneSizeX']
        y = self.params['sceneSizeY']
        self.params['xOffset'] = x - (x_AOI_size + int((y - y_AOI_size)/2.0))

    def _set_y_offset(self, x_AOI_size, y_AOI_size):
        """
        Private method
        """

        self.params['yOffset'] = int((self.params['sceneSizeY'] - y_AOI_size)/2.0)

    def _set_block_verts(self, x_AOI_size, y_AOI_size):
        """
        Auto-calculates verticies for 5 surface fuel blocks in the FDS domain

		Example 1:
        |----------------------|
        |           | b3  |    |
        |           |-----|    |
        |   b2      | b1  | b4 |
        |           |(AOI)|    |
        |           |-----|    |
        |           | b5  |    |
        |----------------------|

		Example 2:
		|----------------------|
		|  |       b3       |  |
		|  |----------------|  |
		|  |                |  |
		|b2|       b1       |b4|
		|  |      (AOI)     |  |
		|  |----------------|  |
		|  |       b5       |  |
		|----------------------|
        """

        x = self.params['sceneSizeX']
        y = self.params['sceneSizeY']
        xoff = self.params['xOffset']
        yoff = self.params['yOffset']
        xAOI = x_AOI_size
        yAOI = y_AOI_size

        b1 = [[xoff, yoff], [xoff+xAOI, yoff], [xoff+xAOI, yoff+yAOI], [xoff, yoff+yAOI]]
        b2 = [[0, 0], [xoff, 0], [xoff, y], [0, y]]
        b3 = [[xoff, yoff+yAOI], [xoff+xAOI, yoff+yAOI], [xoff+xAOI, y], [xoff, y]]
        b4 = [[xoff+xAOI, 0], [x, 0], [x, y], [xoff+xAOI, y]]
        b5 = [[xoff, 0], [xoff+xAOI, 0], [xoff+xAOI, yoff], [xoff, yoff]]
        b6 = [[0,0], [x,0], [x,y], [0,y]]

        self.params['srf_blocks'][1] = b1
        self.params['srf_blocks'][2] = b2
        self.params['srf_blocks'][3] = b3
        self.params['srf_blocks'][4] = b4
        self.params['srf_blocks'][5] = b5
        self.params['srf_blocks'][6] = b6

    def save_config(self):
        """
        This method uses the defined parameters to generate Capsis input files
        """

        # get the current location of this module
        this_dir = os.path.dirname(os.path.abspath(__file__))
		#B Below hardwired to run from interpreter
        #this_dir = 'C:/Users/bhdavis/Documents/STANDFIRE/source_code/standfire-master/standfire'

        # read the capsis input template
        with open(this_dir + '/data/capsis/input_template.txt', 'r') as f:
            input_params = f.read()

        # read the capsis additional properties template
        with open(this_dir + '/data/capsis/additionalProperties_template.txt', 'r') as f:
            properties = f.read()

        # copy species file from standfire directory to capsis run directory
        copyfile(this_dir + '/data/capsis/speciesFile.txt', self.run_directory + '/speciesFile.txt')

        # configure the input templates with user-defined parameters
        input_params = input_params.format(d=self.params)
        properties = properties.format(d=self.params)

        # and save the input files in the run directory specified on class instantiation
        with open(self.run_directory + '/capsis_run_file.txt', 'w') as f:
            f.write(input_params)

        with open(self.run_directory + '/additionalProperties.txt', 'w') as f:
            f.write(properties)

        with open(self.run_directory + '/' + self.params['svsBaseFile'] + '_scalars.csv', 'w') as f:
            f.write('"shrubwt", "herbwt", "litter", "duff"')

        # create an output director to store capsis fuels
        if os.path.isdir(self.run_directory + '/output/'):
            rmtree(self.run_directory + '/output')
            os.mkdir(self.run_directory + '/output/')
        else:
            os.mkdir(self.run_directory + '/output/')
        # write sim area to file for standfire analyze
        with open(self.run_directory + '/output/sim_area.txt', 'a') as f:
            f.write(str(self.params['sceneSizeX']*self.params['sceneSizeY']))

        # generate binary grid for fuel placement
        binGrid = GenerateBinaryGrid(self.params['sceneSizeX'],
                                     self.params['sceneSizeY'],
                                     self.params['sceneSizeZ'],
                                     self.params['gridResolution'],
                                     self.params['gridNumber'],
                                     self.run_directory + '/grid.txt')

class Execute(object):
    """
    This class executes capsis according to the configuration from RunConfig.
    Capsis execution is platform agnostic
    """

    def __init__(self, path_to_run_file, subset_percent):
        """
        Constructor
        """

        self.capsis_dir = os.path.dirname(os.path.abspath(__file__)) + '/bin/capsis/'
        #self.subset_percent = 0.01 # expose this to user at some point

        if platform.system().lower() == 'linux':
            self._exec_capsis_linux(path_to_run_file)
        if platform.system().lower() == 'windows':
            self._exec_capsis_win(path_to_run_file)

        if subset_percent != 1.0:
            self._subset_fuels(path_to_run_file, subset_percent)

        self._read_fuels(path_to_run_file)


    def _exec_capsis_linux(self, path_to_run_file):
        """
        Private method
        """

        subprocess.call(['sh', self.capsis_dir + 'capsis.sh', '-p', 'script','standfire.myscripts.SFScript', path_to_run_file])

    def _exec_capsis_win(self, path_to_run_file):
        """
        Private method
        """

        os.chdir(self.capsis_dir)
        subprocess.call([self.capsis_dir + 'capsis.bat', '-p', 'script','standfire.myscripts.SFScript', path_to_run_file])

    def _subset_fuels(self, path_to_run_file, subset_percent):
        """
        Private method

        Sets a user defined percentage of fuels (shrubs, herbs and trees) OUTPUT_TREE
        parameter to FALSE in the capsis_fuels.txt file. This effects what fuels
        WFDS tracks (not what it models) and should reduce the computing resources
        needed to run WFDS and SMOKEVIEW.

        :param path_to_run_file: Path and file name of capsis run file (capsis parameters)
        :type string
        :param subset_percent: Percentage of fuels to leave OUTPUT_TREE=.TRUE.
        :type float
        """
        cap_fuels = '/'.join(path_to_run_file.split('/')[:-1]) + '/output/capsis_fuels.txt'
        # read capsis_fuels.txt into the list variable 'lines'
        capsis_fuels = open(cap_fuels, 'r')
        lines = capsis_fuels.readlines()
        capsis_fuels.close()
        # create a list of indicies for those lines that contain "OUTPUT_TREE="
        tree_line_index = [index for index, x in enumerate(lines) if "OUTPUT_TREE=" in x]
        # generate a random sample of indicies
        sample_size = int(round(len(tree_line_index) * (1 - subset_percent)))
        rand_sample = sorted(random.sample(tree_line_index, sample_size))
        # set OUTPUT_TREE to FALSE for those lines indexed in the random sample
        line_num = 0
        lines_new = []
        for l in lines:
            if line_num not in rand_sample:
                lines_new.append(l)
            else:
                lines_new.append(l.replace("OUTPUT_TREE=.TRUE.", "OUTPUT_TREE=.FALSE."))
            line_num += 1
        # copy original version of capsis_fuels.txt to preserve it (for now)
        copyfile(cap_fuels, cap_fuels[:-4] + "_raw.txt")
        # overwrite capsis_fuels.txt with the new values
        out = open(cap_fuels, 'w')
        out.writelines(lines_new)
        out.close()


    def _read_fuels(self, path_to_run_file):
        """
        Private method
        """
		 #Below hardwired to run from interpreter
##        with open('C:/Users/bhdavis/Documents/STANDFIRE/STANDFIRE_v1.0/output/capsis_fuels.txt', 'r') as f:
##            lines = f.read()
        with open('/'.join(path_to_run_file.split('/')[:-1]) + '/output/capsis_fuels.txt', 'r') as f:
            lines = f.read()

        # creates and populates fuels variable. Becomes part of the object stored in 'capsis_execute' in the standfire_mini_interface script
        self.fuels = lines
