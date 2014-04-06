"""Small class for reading in subfind tables in HDF5 format"""
import h5py
import numpy as np
import glob
import os.path as path

class SubFindHDF5:
    """
    Class to read the subfind tables from a directory.
    Reads all arrays from all tables and concatenates them together.
    """
    def __init__(self, base, num):
        snap=str(num).rjust(3,'0')
        fofdir = path.join(base,"groups_"+snap)
        fofpatt = fofdir+"/fof_subhalo_tab_"+snap+"*.hdf5"
        #Get a list of the files
        self.foffiles = glob.glob(fofpatt)
        f = h5py.File(self.foffiles[0],'r')
        #Find out how many of each type of thing we have by reading the header
        self._sizes = {}
        self._sizes["Group"] = f["Header"].attrs["Ngroups_Total"]
        self._sizes["Subhalo"] = f["Header"].attrs["Nsubgroups_Total"]
        #This is not actually used yet
        self._sizes["IDs"] = f["Header"].attrs["Nids_Total"]
        #Find the group and subhalo array names
        self.Grpnames = f["Group"].keys()
        self.Subnames = f["Subhalo"].keys()
        f.close()
        self._cache = {}
        self._cache["Group"] = {}
        self._cache["Subhalo"] = {}

    def get_grp_names(self):
        """Get the names of all arrays attached to groups"""
        return self.Grpnames

    def get_sub_names(self):
        """Get the names of all arrays attached to subhalos"""
        return self.Subnames

    def _get_array(self, dset, name):
        """Get the array called 'name' from the array 'dset'"""
        try:
            return self._cache[dset][name]
        except KeyError:
            f = h5py.File(self.foffiles[0],'r')
            data = np.array(f[dset][name])
            f.close()
            for ii in xrange(1, np.size(self.foffiles)):
                f = h5py.File(self.foffiles[ii],'r')
                tmp = np.array(f[dset][name])
                f.close()
                data = np.concatenate([data, tmp])
        #Check we found everything
        assert(np.shape(data)[0] == self._sizes[dset])
        self._cache[dset][name] = data
        return data

    def get_sub(self, name):
        """Get the array called 'name' from the Subhalo arrays"""
        return self._get_array("Subhalo", name)

    def get_grp(self, name):
        """Get the array called 'name' from the Group arrays"""
        return self._get_array("Group", name)
