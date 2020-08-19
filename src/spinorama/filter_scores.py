#                                                  -*- coding: utf-8 -*-
import math
import logging
import numpy as np
import pandas as pd
import scipy.signal as sig
import altair as alt

from .load import graph_melt
from .graph import graph_spinorama, graph_freq
from .compute_scores import speaker_pref_rating, nbd
from .compute_cea2034 import compute_cea2034, estimated_inroom_HV, spl2pressure, pressure2spl, listening_window
from .load_parse import load_normalize
from .filter_iir import Biquad
from .filter_peq import peq_build, peq_apply_measurements, peq_print


def scores_apply_filter(df_speaker, peq):
    # get SPL H & V
    splH = df_speaker['SPL Horizontal_unmelted']
    splV = df_speaker['SPL Vertical_unmelted']
    # apply EQ to all horizontal and vertical measurements
    splH_filtered = peq_apply_measurements(splH, peq)
    splV_filtered = peq_apply_measurements(splV, peq)
    # compute filtered score
    spin_filtered = graph_melt(compute_cea2034(splH_filtered, splV_filtered))
    pir_filtered  = graph_melt(estimated_inroom_HV(splH_filtered, splV_filtered))
    score_filtered = speaker_pref_rating(spin_filtered, pir_filtered, rounded=False)
    if score_filtered is None:
        logging.info('computing pref score for eq failed')
        # max score is around 10
        return None, None, -10.0
    return spin_filtered, pir_filtered, score_filtered


def scores_graph(spin, spin_filtered, params):
    return graph_spinorama(spin, params) | graph_spinorama(spin_filtered, params)


def scores_print(score, score_filtered):
    print('         SPK FLT')
    print('-----------------')
    print('NBD  ON {0:0.2f} {1:0.2f}'.format(score['nbd_on_axis'], score_filtered['nbd_on_axis']))
    print('NBD  LW {0:0.2f} {1:0.2f}'.format(score['nbd_listening_window'], score_filtered['nbd_listening_window']))
    print('NBD PIR {0:0.2f} {1:0.2f}'.format(score['nbd_pred_in_room'], score_filtered['nbd_pred_in_room']))
    print('SM  PIR {0:0.2f} {1:0.2f}'.format(score['sm_pred_in_room'], score_filtered['sm_pred_in_room']))
    print('SM   SP {0:0.2f} {1:0.2f}'.format(score['sm_sound_power'], score_filtered['sm_sound_power']))
    print('LFX       {0}   {1:0.0f}'.format(score['lfx_hz'], score_filtered['lfx_hz']))
    print('LFQ     {0} {1:0.2f}'.format(score['lfq'], score_filtered['lfq']))
    print('-----------------')
    print('Score    {0:0.1f}  {1:0.1f}'.format(score['pref_score'], score_filtered['pref_score']))
    print('-----------------')


def scores_loss(df_speaker, peq):
    # optimise for score directly
    _, _, score_filtered = scores_apply_filter(df_speaker, peq)
    # optimize max score is the same as optimize min -score
    return -score_filtered['pref_score']


def lw_loss(df_speaker, peq):
    # optimise LW
    # get SPL H & V
    splH = df_speaker['SPL Horizontal_unmelted']
    splV = df_speaker['SPL Vertical_unmelted']
    # apply EQ to all horizontal and vertical measurements
    splH_filtered = peq_apply_measurements(splH, peq)
    splV_filtered = peq_apply_measurements(splV, peq)
    # compute LW
    lw_filtered = listening_window(splH_filtered, splV_filtered)
    # optimize nbd
    score = nbd(lw_filtered)
    print('LW score: {}'.format(score))
    return score


