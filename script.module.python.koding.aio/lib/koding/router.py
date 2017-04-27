# -*- coding: utf-8 -*-

"""
    router.py --- functions implementing a routing function
    Copyright (C) 2017, Midraal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import koding
import xbmcgui

master_modes = {
    # Required for certain koding functions to work
    "populate_list": {'function': koding.Populate_List, 'args': ["url"]},
    "play_video": {'function': koding.Play_Video, 'args': ["url"]},
    "show_tutorial": {'function': koding.Show_Tutorial, 'args': ["url"]},
    "tutorials": {'function': koding.Grab_Tutorials, 'args': []},
}


def route(mode, args=[]):
    if mode not in master_modes:

        def _route(function):
            master_modes[mode] = {
                'function': function,
                'args': args
            }
            return function
        return _route
    else:
        xbmcgui.Dialog().ok('DUPLICATE MODE',
                            'The following mode already exists:',
                            '[COLOR=dodgerblue]%s[/COLOR]' % mode)


def run(default="main"):
    import urlparse
    import sys
    params = dict(urlparse.parse_qsl(sys.argv[2].replace('?', '')))
    mode = params.get("mode", default)
    if mode in master_modes:
        evaled_args = []
        for arg in master_modes[mode]["args"]:
            evaled_args.append(params[arg])
        try:
            master_modes[mode]["function"](*evaled_args)
        except:
            koding.Text_Box('ERROR IN CODE', koding.Last_Error())
    else:
        xbmcgui.Dialog().ok('MODE DOES NOT EXIST',
                            'The following mode does not exist in your\
                            master_modes dictionary:',
                            '[COLOR=dodgerblue]%s[/COLOR]' % mode)
