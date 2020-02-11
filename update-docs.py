#!/usr/bin/env python
#                                                  -*- coding: utf-8 -*-
# A library to display spinorama charts
#
# Copyright (C) 2020 Pierre Aubert pierreaubert(at)yahoo(dot)fr
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

"""
usage: update-docs.py [--version] 

"""
from mako.template import Template
from src.spinorama.load import parse_all_speakers
from src.spinorama.graph import print_graphs
from src.spinorama.analysis import estimates

from docopt import docopt

if __name__ == '__main__':
    args = docopt(__doc__,
                  version='update-docs.py version 1.0',
                  options_first=True)
    
    df = parse_all_speakers()

    meta = {}
    for k,v in df.items():
        try:
            spin = df[k]['CEA2034']
            onaxis = spin.loc[spin['Measurements']=='On Axis']
            meta[k] = estimates(onaxis)
        except ValueError:
            print('Computing estimates failed for speaker: '+k)

    index_html = Template(filename='templates/index.html')
    with open('docs/index.html','w') as f:
        f.write(index_html.render(speakers=df, meta=meta))
        f.close()

    speaker_html = Template(filename='templates/speaker.html')
    for speaker, measurements in df.items():
        with open('docs/'+speaker+'.html','w') as f:
            freq_filter = [
                "CEA2034", 
                "Early Reflections", 
                "Estimated In-Room Response", 
                "Horizontal Reflections", 
                "Vertical Reflections", 
                "SPL Horizontal", 
                "SPL Vertical"
                ]
            freqs={key: measurements[key] for key in freq_filter if key in measurements}
            contour_filter = [
                "SPL Horizontal_unmelted", 
                "SPL Vertical_unmelted"
                ]
            contours={key: measurements[key] for key in contour_filter if key in measurements}
            radar_filter = [
                "SPL Horizontal_unmelted", 
                "SPL Vertical_unmelted"
                ]
            radars={key: measurements[key] for key in radar_filter if key in measurements}
            f.write(speaker_html.render(speaker=speaker, 
                                        freqs=freqs, 
                                        contours=contours, 
                                        radars=radars, 
                                        meta=meta))
            f.close()

