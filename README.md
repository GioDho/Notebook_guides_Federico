# Notes during explaination

## Preprocess (python)
Preprocessing passing from mid.gz to pickle. One pickle for the waveforms, one pickle for images.

For the PMTs it taking only trigger 0 and saves only the slow digitizer.

Input: run number, path of midas input file, path where you want the pickle

Output_CAM: pickle with pandas with all reco variable of camera

Output_PMT: pickle with pandas with the 4 lists of waveforms (one list per PMT with the nevents of the run

## Waveform analysis

### Singlewaveform
Analyses one pkl at a time: Estimates trigger existance, where the signal is (convolution wth Gaussian), computes charge, min voltage, deltaz (remember usage with scintillators)

Input: run number, path pkl, configfile (has explaination)

Output: (given by get_data) dictionary with relevant infos. CARE: this is not meant to write things. It gives to other functions the info of a single waveform you selected to be analysed 

Extra in config: sigma usually between 2.5-3

Extra in cluster_finder: a waveform cluster id is defined as: start = above nsigma of baseline; end = if the previous 15 were under the nsigma. Then checks if the cluster has at least one sample below the hard cut threshold, if not cluster is deleted. Merge_channels joins cluster very close to one another

### PMT Analysis
Class which allows to store and then plot and make analysis the result of Singlewaveform class

Input: instance of Singlewaveform

Output: using get_data you have a dictionary of numpy array with the main things Singlewaveform computed, but for all events

## Camera analysis

### ExtractData
Prefilter of the camera variables of the recofile and reshapes the redpix 

Input: run number, pkl path, instance of Singlewaveform (optional), mode (muon, iron, custom, None), configfile

Output: from get_sc_data you get dictionary with the list of scalar variables of the survived clusters of an image; from get_redpix you get dictionary with the list of redpix of the survived clusters of an image;

Extra in __init__: the instance of Singlewaveform uses only booltrigger: if there is nothing useful, the image is skipped

Extra in config_file: contains cut on reco variables

Extra: plotfilteredimages(firstimage,lastimage) plots the clusters and highlights in blu what passed the filters

Extra: plotexplaintracks(firstimage,lastimage) plots the clusters and puts in the legend the variables (hardcoded) you chose

### TrackRestructurer
For tracks you do not want more analysis, you pass the output of ExtractData to this and you erase empty images and adds image and cluster indexes

Output format: list which contains a dictionary with the variable of reco and the added ones. The iteration is on each single cluster, not image

### TrackAnalyzer
Same as TrackRestructurer, but recomputes some reco variables (theta, length, width, tfullrms) and computes extra (like theta_fit and the long and trans projections) and place them in the output format as TrackRestructurer

Extra: plot(index_event)
