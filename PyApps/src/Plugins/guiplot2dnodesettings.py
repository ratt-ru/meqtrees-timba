#-*- coding: utf-8 -*-
# SciCraft - An interactive graphics front end to advanced data mining
# Copyright (C) 2002-2007 SciCraft Development Team
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# 
# As a special exception, SciCraft Development Team gives permission
# to link this program with  Qt non-commercial edition, and distribute
# the resulting executable, without including the source code for the
# Qt non-commercial edition in the source distribution.
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from qt import SIGNAL, Qt, QColorDialog

import os
import qt
import re
import sys
import types
from .dialog_window_config import *
#from tabdialog import *


connect = qt.QObject.connect

# helper functions to WidgetSettingsDialog
_grid_styles = [Qt.SolidLine, Qt.DashLine, Qt.DotLine, Qt.DashDotLine,
                Qt.DashDotDotLine]

def _item_to_style(item):
    """Returns what line-style is on item in style combo box."""
    return _grid_styles[item]

def _style_to_item(style):
    """Returns which item in line-style combo box holds style."""
    return _grid_styles.index(style)


class WidgetSettingsDialog:

    def __init__(self, actual_parent,gui_parent):
        self._widget = dialog_window_config(parent=gui_parent, mother=self)

        self._parent_widget = actual_parent

        # labels settings
        plot_parms = self._parent_widget.getPlotParms()
        self._widget.child('line_edit_window_title').setText(plot_parms['window_title'])
        self._widget.child('line_edit_x_axis_label').setText(plot_parms['x_title'])
        self._widget.child('line_edit_y_axis_label').setText(plot_parms['y_title'])

        # grid settings
#       gridsettings = self._parent_widget.get_grid_settings()
        self._maj_colour_button = self._widget.child('push_button_maj_grid_colour')
        self._min_colour_button = self._widget.child('push_button_min_grid_colour')
        self._maj_x_enabled = self._widget.child('check_box_x_grid_maj_enable')
        self._maj_y_enabled = self._widget.child('check_box_y_grid_maj_enable')
        self._min_x_enabled = self._widget.child('check_box_x_grid_min_enable')
        self._min_y_enabled = self._widget.child('check_box_y_grid_min_enable')
#       self._maj_x_enabled.setChecked(gridsettings[0])
#       self._maj_y_enabled.setChecked(gridsettings[1])
#       self._maj_colour_button.setPaletteBackgroundColor(gridsettings[2])
#       self._widget.child('spin_box_maj_grid_width').setValue(gridsettings[3])
#       self._widget.child('combo_box_maj_grid_style').setCurrentItem(_style_to_item(gridsettings[4]))
#       self._min_x_enabled.setChecked(gridsettings[5])
#       self._min_y_enabled.setChecked(gridsettings[6])
#       self._min_colour_button.setPaletteBackgroundColor(gridsettings[7])
#       self._widget.child('spin_box_min_grid_width').setValue(gridsettings[8])
#       self._widget.child('combo_box_min_grid_style').setCurrentItem(_style_to_item(gridsettings[9]))

        # set correct initial state on gui elements for grid settings
        self._slot_enable_major_grid()
        self._slot_enable_minor_grid() 

        # axes settings
#       axessettings = self._parent_widget.get_axes_settings()
#       self._widget.child('check_box_x_auto_scale').setChecked(axessettings[0])
        self._x_min = self._widget.child('line_edit_x_min')
        self._x_max = self._widget.child('line_edit_x_max')
        self._y_min = self._widget.child('line_edit_y_min')
        self._y_max = self._widget.child('line_edit_y_max')
        self._ratio = self._widget.child('line_edit_ratio')
        self._x_min.setText(str(plot_parms['axis_xmin']))
        self._x_max.setText(str(plot_parms['axis_xmax']))
#       self._widget.child('check_box_y_auto_scale').setChecked(axessettings[3])
        self._y_min.setText(str(plot_parms['axis_ymin']))
        self._y_max.setText(str(plot_parms['axis_ymax']))
#       self._widget.child('check_box_ratio').setChecked(axessettings[6])
#       self._ratio.setText(str(axessettings[7]))

        self._connect_signals()
        self._widget.show()



    def _connect_signals(self):
        connect(self._widget.child('buttonOk'), SIGNAL('clicked()'),
                self._slot_ok_pressed)
        
        # grid connections
        connect(self._maj_colour_button, SIGNAL('clicked()'),
                self._slot_major_grid_colour)
        connect(self._min_colour_button, SIGNAL('clicked()'),
                self._slot_minor_grid_colour)
        connect(self._maj_x_enabled, SIGNAL('clicked()'),
                self._slot_enable_major_grid)
        connect(self._maj_y_enabled, SIGNAL('clicked()'),
                self._slot_enable_major_grid)
        connect(self._min_x_enabled, SIGNAL('clicked()'),
                self._slot_enable_minor_grid)
        connect(self._min_y_enabled, SIGNAL('clicked()'),
                self._slot_enable_minor_grid)

    def _slot_ok_pressed(self):
        settings = {}
        
        # labels settings
        settings['window_title'] = str(self._widget.child('line_edit_window_title').text())
        settings['x_title'] = str(self._widget.child('line_edit_x_axis_label').text())
        settings['y_title'] = str(self._widget.child('line_edit_y_axis_label').text())

        # grid settings
        settings['x_grid_maj_enable'] = str(int(self._maj_x_enabled.isChecked()))
        settings['x_grid_min_enable'] = str(int(self._min_x_enabled.isChecked()))
        settings['y_grid_maj_enable'] = str(int(self._maj_y_enabled.isChecked()))
        settings['y_grid_min_enable'] = str(int(self._min_y_enabled.isChecked()))
        settings['maj_grid_style'] = str(self._widget.child('combo_box_maj_grid_style').currentItem())
        settings['min_grid_style'] = str(self._widget.child('combo_box_min_grid_style').currentItem())
        settings['maj_grid_width'] = str(self._widget.child('spin_box_maj_grid_width').value())
        settings['min_grid_width'] = str(self._widget.child('spin_box_min_grid_width').value())
        settings['maj_grid_colour'] = str(self._maj_colour_button.paletteBackgroundColor().name())
        settings['min_grid_colour'] = str(self._min_colour_button.paletteBackgroundColor().name())

        # axes settings
        settings['x_auto_scale'] = str(int(self._widget.child('check_box_x_auto_scale').isChecked()))
        settings['y_auto_scale'] = str(int(self._widget.child('check_box_y_auto_scale').isChecked()))
        settings['axis_xmin'] = str(self._x_min.text())
        settings['axis_xmax'] = str(self._x_max.text())
        settings['axis_ymin'] = str(self._y_min.text())
        settings['axis_ymax'] = str(self._y_max.text())

        # apply settings
        self._parent_widget.setPlotParms(settings)

    
    def _set_colour_on_button(self, button):
        """Asks the user to choose a colour, then sets it on button."""
        colour = QColorDialog.getColor(button.paletteBackgroundColor(),
                                       self._widget)
        if colour.isValid():
            button.setPaletteBackgroundColor(colour)

    def _slot_major_grid_colour(self):
        self._set_colour_on_button(self._maj_colour_button)
    
    def _slot_minor_grid_colour(self):
        self._set_colour_on_button(self._min_colour_button)

    def _set_grid_widgets_enabled(self, mode, enable):
        for child in ['push_button_%s_grid_colour'%mode,
                      'spin_box_%s_grid_width'%mode,
                      'combo_box_%s_grid_style'%mode,
                      'text_label_%s_grid_colour'%mode,
                      'text_label_%s_grid_width'%mode,
                      'text_label_%s_grid_style'%mode]:
            self._widget.child(child).setEnabled(enable)

    def _slot_enable_major_grid(self):
        if self._maj_x_enabled.isChecked() or self._maj_y_enabled.isChecked():
            self._set_grid_widgets_enabled('maj', True)
        else:
            self._set_grid_widgets_enabled('maj', False)

    def _slot_enable_minor_grid(self):
        if self._min_x_enabled.isChecked() or self._min_y_enabled.isChecked():
            self._set_grid_widgets_enabled('min', True)
        else:
            self._set_grid_widgets_enabled('min', False)

    def _ensure_valid_float_strings(self, string):
        """Returns a string which is parseable by float() from the given string"""
        try:
            return str(float(re.match('[+|-]?[0-9]+[\.[0-9]*]?', string).group()))
        except:
            return '0.0'

    def _slot_x_max(self):
        x_max = str(self._x_max.text())
        self._x_max.setText(self._ensure_valid_float_strings(x_max))

    def _slot_x_min(self):
        x_min = str(self._x_min.text())
        self._x_min.setText(self._ensure_valid_float_strings(x_min))

    def _slot_y_max(self):
        y_max = str(self._y_max.text())
        self._y_max.setText(self._ensure_valid_float_strings(y_max))

    def _slot_y_min(self):
        y_min = str(self._y_min.text())
        self._y_min.setText(self._ensure_valid_float_strings(y_min))

    def _slot_ratio(self):
        ratio = str(self._ratio.text())
        self._ratio.setText(self._ensure_valid_float_strings(ratio))


