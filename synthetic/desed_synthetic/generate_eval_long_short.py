# -*- coding: utf-8 -*-
#########################################################################
# Initial software
# Copyright Nicolas Turpault, Romain Serizel, Justin Salamon, Ankit Parag Shah, 2019, v1.0
# This software is distributed under the terms of the License MIT
#########################################################################
import time
import argparse
import os.path as osp
from pprint import pformat

from utils import create_folder, rm_high_polyphony, post_processing_annotations, generate_multi_common
from generate_eval_FBSNR import generate_new_bg_snr_files
from Logger import LOG

if __name__ == '__main__':
    LOG.info(__file__)
    t = time.time()
    absolute_dir_path = osp.abspath(osp.dirname(__file__))
    base_path_eval = osp.join(absolute_dir_path, '..', 'audio', 'eval')
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfolder', type=str, default=osp.join(base_path_eval, 'soundscapes_generated_ls'))
    parser.add_argument('--outcsv', type=str, default=osp.join(base_path_eval, "soundscapes_generated_ls", "XdB.csv"))
    parser.add_argument('--number', type=int, default=1000)
    parser.add_argument('--fgfolder', type=str, default=osp.join(base_path_eval, "soundbank", "foreground_short"))
    parser.add_argument('--bgfolder', type=str, default=osp.join(base_path_eval, "soundbank", "background_long"))
    args = parser.parse_args()
    pformat(vars(args))

    # General output folder, in args
    out_folder = args.outfolder
    create_folder(out_folder)

    # Default parameters
    n_soundscapes = args.number
    ref_db = -50
    duration = 10.0

    # ################
    # Long event as background, short events as foreground
    # ###########
    fg_folder = args.fgfolder
    bg_folder = args.bgfolder
    # Generate events same way as the training set
    min_events = 1
    max_events = 5

    event_time_dist = 'truncnorm'
    event_time_mean = 5.0
    event_time_std = 2.0
    event_time_min = 0.0
    event_time_max = 10.0

    source_time_dist = 'const'
    source_time = 0.0

    event_duration_dist = 'uniform'
    event_duration_min = 0.25
    event_duration_max = 10.0

    snr_dist = 'const'
    snr = 30

    pitch_dist = 'uniform'
    pitch_min = -3.0
    pitch_max = 3.0

    time_stretch_dist = 'uniform'
    time_stretch_min = 1
    time_stretch_max = 1

    out_folder_ls_30 = osp.join(out_folder, "ls_30dB")
    create_folder(out_folder_ls_30)
    generate_multi_common(n_soundscapes, ref_db, duration, fg_folder, bg_folder, out_folder_ls_30, min_events, max_events,
                          labels=('choose', []), source_files=('choose', []),
                          sources_time=(source_time_dist, source_time),
                          events_time=(event_time_dist, event_time_mean, event_time_std, event_time_min, event_time_max),
                          events_duration=(event_duration_dist, event_duration_min, event_duration_max),
                          snrs=('const', 30), pitch_shifts=('uniform', -3.0, 3.0), time_stretches=('uniform', 1, 1),
                          txt_file=False)

    rm_high_polyphony(out_folder_ls_30, 3)
    post_processing_annotations(out_folder_ls_30, output_folder=out_folder_ls_30, output_csv=args.outcsv,
                                background_label=True)

    # We create the same dataset with different background SNR
    # Be careful, 15 means the background SNR is 15,
    # so the foreground background snr ratio is between -9dB and 15dB
    out_folder_ls_15 = osp.join(out_folder, "ls_15dB")
    create_folder(out_folder_ls_15)
    generate_new_bg_snr_files(15, out_folder_ls_30, out_folder_ls_15)
    
    # Same for 30dB
    out_folder_ls_0 = osp.join(out_folder, "ls_0dB")
    create_folder(out_folder_ls_0)
    generate_new_bg_snr_files(30, out_folder_ls_30, out_folder_ls_0)
