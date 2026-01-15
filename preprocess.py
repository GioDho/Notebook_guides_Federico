# version 2.0

import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
import uproot
import cygno as cy
import pandas as pd

import midas.file_reader
from datetime import datetime
import time
from tqdm import tqdm

import GRANSAX


# --------------------------------------------------------------------- #


from tqdm import tqdm
import uproot
import numpy as np
import pandas as pd
import os


def pkl_reco(run, in_path, out_path):
    """
    Function to produce a .pkl file from a reconstruction output ROOT file.

    Parameters
    ----------
    run : int
        this is the index of the run
    in_path : string
        this is the path to the ROOT file
    out_path: string
        the path onto which to save the .pkl file
    """
    print('file exist check =', os.path.isfile(f'{in_path}reco_run{run}_3D.root'))
    try:
        file_url = f'{in_path}reco_run{run}_3D.root'
        file_out_name = f'{out_path}reco_run{run}_3D.pkl.gz'
        # Check if the ROOT file exists
        if not os.path.isfile(file_url):
            raise FileNotFoundError(f"ROOT file not found: {file_url}")
        tf = uproot.open(file_url)
        names = tf["Events"].keys()
        branch_data = {}
        for name in tqdm(names, desc=f"Processing run {run}", unit="branch"):
            var = tf["Events/" + name].array(library='np')
            if var[0].ndim == 0:
                branch_data[name] = np.hstack(var)
            else:
                branch_data[name] = var

        tf.close()
        df_all = pd.DataFrame(branch_data)
        df_all.to_pickle(file_out_name, compression={'method': 'gzip', 'compresslevel': 1})
        del df_all
        if not os.path.isfile(file_out_name):
            print('ERROR: File not created correctly.')
        else:
            with open('logbook.txt', 'a') as file:
                file.write('made pkl of run {:5d}\n'.format(run))
    except Exception as e:
        with open('logbook.txt', 'a') as file:
            file.write('run {:5d} ERROR >>> {}\n'.format(run, e))
    print('success check =', os.path.isfile(file_out_name))


# --------------------------------------------------------------------- #


def pkl_waveform(run, in_path, out_path):
    """
    Function to produce a .pkl file containing the waveform data imported form the raw MIDAS files.

    Parameters
    ----------
    run : int
        this is the index of the run
    in_path : string
        this is the path to the MIDAS files
    out_path: string
        the path onto which to save the .pkl file
    """
    # gets the info on the current chosen run
    runInfo = cy.read_cygno_logbook(sql=True, verbose=False, tag='lnf', start_run=13360)
    current_run = runInfo[runInfo['run_number'] == run]
    # the data we are interested in is the 'run_description' and 'HV_STATE'
    description = current_run['run_description']
    print(f'processing waveforms for run: {description}')
    HV = current_run['HV_STATE'].iloc[0]
    # first check if in the output path the filed does not exist already:
    if (HV == 1):
        print('The chosen run is not a pedestal')
        mfile = cy.open_mid(run=run, path=in_path, cloud=False, tag='LNF', verbose=False)
        odb = cy.get_bor_odb(mfile)
        corrected  = odb.data['Configurations']['DRS4Correction'] #currently false
        # channels offests gives the offset for each channel, it is a list of len 40
        channels_offsets  = odb.data['Configurations']['DigitizerOffset']
        header_environment = odb.data['Equipment']['Environment']['Settings']['Names Input']
        
        w0 = []
        w1 = []
        w2 = []
        w3 = []
        nevents = 0
        
        for event in tqdm(mfile, desc=f"Processing run {run}"):
            nevents +=1
            if event.header.is_midas_internal_event():
                #print("Saw a special event")
                continue
            bank_names = ", ".join(b.name for b in event.banks.values())
            
            for bank_name, bank in event.banks.items():
                    
                if ('DGH0' in bank_name): # PMTs wavform 
                    full_header= cy.daq_dgz_full2header(event.banks['DGH0'], verbose=False)
                    w_fast, w_slow = cy.daq_dgz_full2array(event.banks['DIG0'], full_header, verbose=False, 
                                                           corrected=corrected, ch_offset=channels_offsets)
                    w0.append(w_slow[0])
                    w1.append(w_slow[1])
                    w2.append(w_slow[2])
                    w3.append(w_slow[3])
        
        print(f"processed a total of {nevents} events")
        labels = ["pmt_up", "pmt_down", "pmt_1", "pmt_2"]
        df = pd.DataFrame({
            labels[0]: w0,
            labels[1]: w1,
            labels[2]: w2,
            labels[3]: w3
        })
        file_out_name = f'{out_path}waveforms_run{run}.pkl.gz'
        df.to_pickle(file_out_name, compression={'method': 'gzip', 'compresslevel': 1})
        del df, w0, w1, w2, w3
    else:
        print('ERROR: Cannot take waveforms of pedestal run. Try a different run number.')


# --------------------------------------------------------------------- #

