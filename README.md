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

Output:

Extra in config: sigma usually between 2.5-3
