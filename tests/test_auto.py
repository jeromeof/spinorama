#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# A library to display spinorama charts
#
# Copyright (C) 2020-2021 Pierre Aubert pierreaubert(at)yahoo(dot)fr
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# import os
import unittest
import math
import numpy as np
import pandas as pd

from spinorama.filter_iir import Biquad
from spinorama.filter_peq import peq_build
from spinorama.auto_loss import loss
from spinorama.auto_biquad import find_best_peak, find_best_biquad


class BiquadRangeTests(unittest.TestCase):
    def setUp(self):
        self.data = np.zeros(200)
        self.freq = np.logspace(1 + math.log10(2), 4 + math.log10(2), len(self.data))
        self.config = {
            "target_min_freq": 80,
            "target_max_freq": 16000,
            "plus_and_minus": True,
            "curves": ["Listening Window"],
            "loss": "leastsquare_loss",
            "maxiter": 100,
        }

    def test_one_peak(self):
        cases = [
            (1000, 1, 3),
            (1000, 1.2, 2.5),
            (1000, 0.8, 3.2),
            (1000, 1, -3),
            (1000, 1.2, -2.5),
            (1000, 0.8, -3.2),
            (100, 1, 3),
            (100, 1.2, 2.5),
            (100, 0.8, 3.2),
            (100, 1, -3),
            (100, 1.2, -2.5),
            (100, 0.8, -3.2),
            (10000, 1, 3),
            (10000, 1.2, 2.5),
            (10000, 0.8, 3.2),
            (10000, 1, -3),
            (10000, 1.2, -2.5),
            (10000, 0.8, -3.2),
        ]
        for freq, Q, dbGain in cases:
            empty_peq = []
            test_peq = [
                (1.0, Biquad(typ=Biquad.PEAK, freq=freq, srate=48000, Q=Q, dbGain=dbGain)),
            ]
            auto_target = peq_build(self.freq, test_peq)

            init_fun = loss(None, self.freq, [auto_target], [], 0, self.config)

            # super guess
            freq_range = [test_peq[0][1].freq * 0.5, test_peq[0][1].freq / 0.5]
            Q_range = [0.5, 3]
            dbGain_range = [-4, 4]

            (auto_success, auto_biquad_type, auto_freq, auto_Q, auto_dB, auto_fun, auto_iter) = find_best_peak(
                df_speaker=None,
                freq=self.freq,
                auto_target=[auto_target],
                freq_range=freq_range,
                Q_range=Q_range,
                dbGain_range=dbGain_range,
                biquad_range=[3],
                count=0,
                optim_config=self.config,
                prev_best=init_fun,
            )

            last_peq = [(1.0, Biquad(3, auto_freq, 48000, auto_Q, auto_dB))]
            last_fun = loss(None, self.freq, [auto_target], last_peq, 0, self.config)

            # print(
            #     "{} {} {}Hz {:0.2f}Q {:0.2f}dB func=[init {:0.3f} algo {:0.3f} end {:0.3f}] iter={}".format(
            #         auto_success, auto_biquad_type, auto_freq, auto_Q, auto_dB, init_fun, auto_fun, last_fun, auto_iter
            #     )
            # )

            self.assertAlmostEqual(abs(auto_freq - freq) / freq, 0.0, places=2)
            self.assertAlmostEqual(abs(auto_Q - Q), 0, places=1)
            self.assertAlmostEqual(abs(auto_dB + dbGain), 0, places=1)


if __name__ == "__main__":
    unittest.main()
