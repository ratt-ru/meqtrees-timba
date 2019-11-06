# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog_window_config.ui'
#
# Created: Tue Aug 30 11:19:40 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.13
#
# WARNING! All changes made in this file will be lost!

# A script to put up a GUI so that the user can modify plot settings
# Gratefully adapted by AGW from the SciCraft 'dialog_window_config.ui' 


#% $Id$ 

#
# Copyright (C) 2002-2007
# ASTRON (Netherlands Foundation for Research in Astronomy)
# and The MeqTree Foundation
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands, seg@astron.nl
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
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from qt import *
import sys

class dialog_window_config(QDialog):
    def __init__(self,parent = None,name = None, mother=None, modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)


# The following two lines seem wierd, but are necessary until I figure
# out why they are necessary! (or not!)
        self.mother = mother
        if not name:
            self.setName("dialog_window_config")

        self.setSizeGripEnabled(1)
        self.setModal(0)

        dialog_window_configLayout = QVBoxLayout(self,11,6,"dialog_window_configLayout")

        self.tab_widget_categories = QTabWidget(self,"tab_widget_categories")

        self.Widget2 = QWidget(self.tab_widget_categories,"Widget2")
        Widget2Layout = QGridLayout(self.Widget2,1,1,11,6,"Widget2Layout")

        self.group_box_window_labels = QGroupBox(self.Widget2,"group_box_window_labels")
        self.group_box_window_labels.setColumnLayout(0,Qt.Vertical)
        self.group_box_window_labels.layout().setSpacing(6)
        self.group_box_window_labels.layout().setMargin(11)
        group_box_window_labelsLayout = QGridLayout(self.group_box_window_labels.layout())
        group_box_window_labelsLayout.setAlignment(Qt.AlignTop)

        self.line_edit_x_axis_label = QLineEdit(self.group_box_window_labels,"line_edit_x_axis_label")

        group_box_window_labelsLayout.addWidget(self.line_edit_x_axis_label,1,1)

        self.text_label_y_axis_label = QLabel(self.group_box_window_labels,"text_label_y_axis_label")

        group_box_window_labelsLayout.addWidget(self.text_label_y_axis_label,2,0)

        self.text_label_window_title = QLabel(self.group_box_window_labels,"text_label_window_title")

        group_box_window_labelsLayout.addWidget(self.text_label_window_title,0,0)

        self.line_edit_window_title = QLineEdit(self.group_box_window_labels,"line_edit_window_title")

        group_box_window_labelsLayout.addWidget(self.line_edit_window_title,0,1)

        self.text_label_x_axis_label = QLabel(self.group_box_window_labels,"text_label_x_axis_label")

        group_box_window_labelsLayout.addWidget(self.text_label_x_axis_label,1,0)

        self.line_edit_y_axis_label = QLineEdit(self.group_box_window_labels,"line_edit_y_axis_label")

        group_box_window_labelsLayout.addWidget(self.line_edit_y_axis_label,2,1)

        Widget2Layout.addWidget(self.group_box_window_labels,0,0)
        self.tab_widget_categories.insertTab(self.Widget2,QString(""))

        self.TabPage = QWidget(self.tab_widget_categories,"TabPage")
        TabPageLayout = QHBoxLayout(self.TabPage,11,6,"TabPageLayout")

        self.group_box_major_grid = QGroupBox(self.TabPage,"group_box_major_grid")
        self.group_box_major_grid.setColumnLayout(0,Qt.Vertical)
        self.group_box_major_grid.layout().setSpacing(6)
        self.group_box_major_grid.layout().setMargin(11)
        group_box_major_gridLayout = QGridLayout(self.group_box_major_grid.layout())
        group_box_major_gridLayout.setAlignment(Qt.AlignTop)

        self.text_label_maj_grid_width = QLabel(self.group_box_major_grid,"text_label_maj_grid_width")
        self.text_label_maj_grid_width.setEnabled(0)

        group_box_major_gridLayout.addWidget(self.text_label_maj_grid_width,3,0)

        self.text_label_maj_grid_style = QLabel(self.group_box_major_grid,"text_label_maj_grid_style")
        self.text_label_maj_grid_style.setEnabled(0)

        group_box_major_gridLayout.addWidget(self.text_label_maj_grid_style,4,0)

        self.text_label_maj_grid_colour = QLabel(self.group_box_major_grid,"text_label_maj_grid_colour")
        self.text_label_maj_grid_colour.setEnabled(0)

        group_box_major_gridLayout.addWidget(self.text_label_maj_grid_colour,2,0)

        self.check_box_x_grid_maj_enable = QCheckBox(self.group_box_major_grid,"check_box_x_grid_maj_enable")
        self.check_box_x_grid_maj_enable.setChecked(0)

        group_box_major_gridLayout.addMultiCellWidget(self.check_box_x_grid_maj_enable,0,0,0,1)

        self.check_box_y_grid_maj_enable = QCheckBox(self.group_box_major_grid,"check_box_y_grid_maj_enable")
        self.check_box_y_grid_maj_enable.setChecked(0)

        group_box_major_gridLayout.addMultiCellWidget(self.check_box_y_grid_maj_enable,1,1,0,1)

        layout_maj_grid_colour = QHBoxLayout(None,0,6,"layout_maj_grid_colour")
        spacer_maj_grid_colour_left = QSpacerItem(27,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout_maj_grid_colour.addItem(spacer_maj_grid_colour_left)

        self.push_button_maj_grid_colour = QPushButton(self.group_box_major_grid,"push_button_maj_grid_colour")
        self.push_button_maj_grid_colour.setEnabled(0)
        self.push_button_maj_grid_colour.setPaletteBackgroundColor(QColor(0,0,0))
        layout_maj_grid_colour.addWidget(self.push_button_maj_grid_colour)
        spacer_maj_grid_colour_right = QSpacerItem(28,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout_maj_grid_colour.addItem(spacer_maj_grid_colour_right)

        group_box_major_gridLayout.addLayout(layout_maj_grid_colour,2,1)

        self.spin_box_maj_grid_width = QSpinBox(self.group_box_major_grid,"spin_box_maj_grid_width")
        self.spin_box_maj_grid_width.setEnabled(0)

        group_box_major_gridLayout.addWidget(self.spin_box_maj_grid_width,3,1)

        self.combo_box_maj_grid_style = QComboBox(0,self.group_box_major_grid,"combo_box_maj_grid_style")
        self.combo_box_maj_grid_style.setEnabled(0)

        group_box_major_gridLayout.addWidget(self.combo_box_maj_grid_style,4,1)
        TabPageLayout.addWidget(self.group_box_major_grid)

        self.group_box_minor_grid = QGroupBox(self.TabPage,"group_box_minor_grid")
        self.group_box_minor_grid.setColumnLayout(0,Qt.Vertical)
        self.group_box_minor_grid.layout().setSpacing(6)
        self.group_box_minor_grid.layout().setMargin(11)
        group_box_minor_gridLayout = QGridLayout(self.group_box_minor_grid.layout())
        group_box_minor_gridLayout.setAlignment(Qt.AlignTop)

        self.text_label_min_grid_colour = QLabel(self.group_box_minor_grid,"text_label_min_grid_colour")
        self.text_label_min_grid_colour.setEnabled(0)

        group_box_minor_gridLayout.addWidget(self.text_label_min_grid_colour,2,0)

        self.text_label_min_grid_width = QLabel(self.group_box_minor_grid,"text_label_min_grid_width")
        self.text_label_min_grid_width.setEnabled(0)

        group_box_minor_gridLayout.addWidget(self.text_label_min_grid_width,3,0)

        self.text_label_min_grid_style = QLabel(self.group_box_minor_grid,"text_label_min_grid_style")
        self.text_label_min_grid_style.setEnabled(0)
        self.text_label_min_grid_style.setFocusPolicy(QLabel.NoFocus)

        group_box_minor_gridLayout.addWidget(self.text_label_min_grid_style,4,0)

        self.check_box_y_grid_min_enable = QCheckBox(self.group_box_minor_grid,"check_box_y_grid_min_enable")
        self.check_box_y_grid_min_enable.setEnabled(0)

        group_box_minor_gridLayout.addMultiCellWidget(self.check_box_y_grid_min_enable,1,1,0,1)

        self.check_box_x_grid_min_enable = QCheckBox(self.group_box_minor_grid,"check_box_x_grid_min_enable")
        self.check_box_x_grid_min_enable.setEnabled(0)
        self.check_box_x_grid_min_enable.setChecked(0)

        group_box_minor_gridLayout.addMultiCellWidget(self.check_box_x_grid_min_enable,0,0,0,1)

        layout_min_grid_colour = QHBoxLayout(None,0,6,"layout_min_grid_colour")
        spacer_min_grid_colour_left = QSpacerItem(27,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout_min_grid_colour.addItem(spacer_min_grid_colour_left)

        self.push_button_min_grid_colour = QPushButton(self.group_box_minor_grid,"push_button_min_grid_colour")
        self.push_button_min_grid_colour.setEnabled(0)
        self.push_button_min_grid_colour.setPaletteBackgroundColor(QColor(0,0,0))
        layout_min_grid_colour.addWidget(self.push_button_min_grid_colour)
        spacer_min_grid_colour_right = QSpacerItem(28,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout_min_grid_colour.addItem(spacer_min_grid_colour_right)

        group_box_minor_gridLayout.addLayout(layout_min_grid_colour,2,1)

        self.spin_box_min_grid_width = QSpinBox(self.group_box_minor_grid,"spin_box_min_grid_width")
        self.spin_box_min_grid_width.setEnabled(0)

        group_box_minor_gridLayout.addWidget(self.spin_box_min_grid_width,3,1)

        self.combo_box_min_grid_style = QComboBox(0,self.group_box_minor_grid,"combo_box_min_grid_style")
        self.combo_box_min_grid_style.setEnabled(0)

        group_box_minor_gridLayout.addWidget(self.combo_box_min_grid_style,4,1)
        TabPageLayout.addWidget(self.group_box_minor_grid)
        self.tab_widget_categories.insertTab(self.TabPage,QString(""))

        self.Widget3 = QWidget(self.tab_widget_categories,"Widget3")
        Widget3Layout = QGridLayout(self.Widget3,1,1,11,6,"Widget3Layout")

        self.line_edit_ratio = QLineEdit(self.Widget3,"line_edit_ratio")
        self.line_edit_ratio.setEnabled(0)

        Widget3Layout.addWidget(self.line_edit_ratio,1,1)

        self.group_box_x_axis_range = QGroupBox(self.Widget3,"group_box_x_axis_range")
        self.group_box_x_axis_range.setColumnLayout(0,Qt.Vertical)
        self.group_box_x_axis_range.layout().setSpacing(6)
        self.group_box_x_axis_range.layout().setMargin(11)
        group_box_x_axis_rangeLayout = QGridLayout(self.group_box_x_axis_range.layout())
        group_box_x_axis_rangeLayout.setAlignment(Qt.AlignTop)

        self.check_box_x_auto_scale = QCheckBox(self.group_box_x_axis_range,"check_box_x_auto_scale")
        self.check_box_x_auto_scale.setChecked(1)

        group_box_x_axis_rangeLayout.addMultiCellWidget(self.check_box_x_auto_scale,0,0,0,1)

        self.text_label_x_min = QLabel(self.group_box_x_axis_range,"text_label_x_min")
        self.text_label_x_min.setEnabled(0)

        group_box_x_axis_rangeLayout.addWidget(self.text_label_x_min,1,0)

        self.line_edit_x_min = QLineEdit(self.group_box_x_axis_range,"line_edit_x_min")
        self.line_edit_x_min.setEnabled(0)
        self.line_edit_x_min.setAlignment(QLineEdit.AlignLeft)

        group_box_x_axis_rangeLayout.addWidget(self.line_edit_x_min,1,1)

        self.text_label_x_max = QLabel(self.group_box_x_axis_range,"text_label_x_max")
        self.text_label_x_max.setEnabled(0)

        group_box_x_axis_rangeLayout.addWidget(self.text_label_x_max,2,0)

        self.line_edit_x_max = QLineEdit(self.group_box_x_axis_range,"line_edit_x_max")
        self.line_edit_x_max.setEnabled(0)

        group_box_x_axis_rangeLayout.addWidget(self.line_edit_x_max,2,1)

        Widget3Layout.addWidget(self.group_box_x_axis_range,0,0)

        self.group_box_y_axis_range = QGroupBox(self.Widget3,"group_box_y_axis_range")
        self.group_box_y_axis_range.setColumnLayout(0,Qt.Vertical)
        self.group_box_y_axis_range.layout().setSpacing(6)
        self.group_box_y_axis_range.layout().setMargin(11)
        group_box_y_axis_rangeLayout = QGridLayout(self.group_box_y_axis_range.layout())
        group_box_y_axis_rangeLayout.setAlignment(Qt.AlignTop)

        self.text_label_y_max = QLabel(self.group_box_y_axis_range,"text_label_y_max")
        self.text_label_y_max.setEnabled(0)

        group_box_y_axis_rangeLayout.addWidget(self.text_label_y_max,2,0)

        self.text_label_y_min = QLabel(self.group_box_y_axis_range,"text_label_y_min")
        self.text_label_y_min.setEnabled(0)

        group_box_y_axis_rangeLayout.addWidget(self.text_label_y_min,1,0)

        self.check_box_y_auto_scale = QCheckBox(self.group_box_y_axis_range,"check_box_y_auto_scale")
        self.check_box_y_auto_scale.setChecked(1)

        group_box_y_axis_rangeLayout.addMultiCellWidget(self.check_box_y_auto_scale,0,0,0,1)

        self.line_edit_y_min = QLineEdit(self.group_box_y_axis_range,"line_edit_y_min")
        self.line_edit_y_min.setEnabled(0)
        self.line_edit_y_min.setAlignment(QLineEdit.AlignLeft)

        group_box_y_axis_rangeLayout.addWidget(self.line_edit_y_min,1,1)

        self.line_edit_y_max = QLineEdit(self.group_box_y_axis_range,"line_edit_y_max")
        self.line_edit_y_max.setEnabled(0)

        group_box_y_axis_rangeLayout.addWidget(self.line_edit_y_max,2,1)

        Widget3Layout.addWidget(self.group_box_y_axis_range,0,1)

        self.check_box_ratio = QCheckBox(self.Widget3,"check_box_ratio")
        self.check_box_ratio.setEnabled(1)

        Widget3Layout.addWidget(self.check_box_ratio,1,0)
        self.tab_widget_categories.insertTab(self.Widget3,QString(""))
        dialog_window_configLayout.addWidget(self.tab_widget_categories)

        Layout1 = QHBoxLayout(None,0,6,"Layout1")
        Horizontal_Spacing2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        Layout1.addItem(Horizontal_Spacing2)

        self.buttonOk = QPushButton(self,"buttonOk")
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
        Layout1.addWidget(self.buttonOk)

        self.buttonCancel = QPushButton(self,"buttonCancel")
        self.buttonCancel.setAutoDefault(1)
        Layout1.addWidget(self.buttonCancel)
        dialog_window_configLayout.addLayout(Layout1)

        self.languageChange()

        self.resize(QSize(544,303).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.check_box_y_auto_scale,SIGNAL("toggled(bool)"),self.line_edit_y_max.setDisabled)
        self.connect(self.check_box_y_auto_scale,SIGNAL("toggled(bool)"),self.line_edit_y_min.setDisabled)
        self.connect(self.check_box_y_auto_scale,SIGNAL("toggled(bool)"),self.text_label_y_min.setDisabled)
        self.connect(self.check_box_y_auto_scale,SIGNAL("toggled(bool)"),self.text_label_y_max.setDisabled)
        self.connect(self.check_box_x_auto_scale,SIGNAL("toggled(bool)"),self.line_edit_x_max.setDisabled)
        self.connect(self.check_box_x_auto_scale,SIGNAL("toggled(bool)"),self.line_edit_x_min.setDisabled)
        self.connect(self.check_box_x_auto_scale,SIGNAL("toggled(bool)"),self.text_label_x_max.setDisabled)
        self.connect(self.check_box_x_auto_scale,SIGNAL("toggled(bool)"),self.text_label_x_min.setDisabled)
        self.connect(self.buttonCancel,SIGNAL("clicked()"),self.reject)
        self.connect(self.buttonOk,SIGNAL("clicked()"),self.accept)
        self.connect(self.check_box_ratio,SIGNAL("toggled(bool)"),self.line_edit_ratio.setEnabled)
        self.connect(self.check_box_x_grid_maj_enable,SIGNAL("toggled(bool)"),self.check_box_x_grid_min_enable.setEnabled)
        self.connect(self.check_box_y_grid_maj_enable,SIGNAL("toggled(bool)"),self.check_box_y_grid_min_enable.setEnabled)

        self.setTabOrder(self.line_edit_window_title,self.line_edit_x_axis_label)
        self.setTabOrder(self.line_edit_x_axis_label,self.line_edit_y_axis_label)
        self.setTabOrder(self.line_edit_y_axis_label,self.check_box_x_grid_maj_enable)
        self.setTabOrder(self.check_box_x_grid_maj_enable,self.check_box_y_grid_maj_enable)
        self.setTabOrder(self.check_box_y_grid_maj_enable,self.push_button_maj_grid_colour)
        self.setTabOrder(self.push_button_maj_grid_colour,self.spin_box_maj_grid_width)
        self.setTabOrder(self.spin_box_maj_grid_width,self.combo_box_maj_grid_style)
        self.setTabOrder(self.combo_box_maj_grid_style,self.check_box_x_grid_min_enable)
        self.setTabOrder(self.check_box_x_grid_min_enable,self.check_box_y_grid_min_enable)
        self.setTabOrder(self.check_box_y_grid_min_enable,self.push_button_min_grid_colour)
        self.setTabOrder(self.push_button_min_grid_colour,self.spin_box_min_grid_width)
        self.setTabOrder(self.spin_box_min_grid_width,self.combo_box_min_grid_style)
        self.setTabOrder(self.combo_box_min_grid_style,self.check_box_x_auto_scale)
        self.setTabOrder(self.check_box_x_auto_scale,self.line_edit_x_min)
        self.setTabOrder(self.line_edit_x_min,self.line_edit_x_max)
        self.setTabOrder(self.line_edit_x_max,self.check_box_y_auto_scale)
        self.setTabOrder(self.check_box_y_auto_scale,self.line_edit_y_min)
        self.setTabOrder(self.line_edit_y_min,self.line_edit_y_max)
        self.setTabOrder(self.line_edit_y_max,self.check_box_ratio)
        self.setTabOrder(self.check_box_ratio,self.line_edit_ratio)
        self.setTabOrder(self.line_edit_ratio,self.buttonOk)
        self.setTabOrder(self.buttonOk,self.buttonCancel)

    def languageChange(self):
        self.setCaption(self.__tr("Window Configuration"))
        self.group_box_window_labels.setTitle(self.__tr("Window labels"))
        self.text_label_y_axis_label.setText(self.__tr("Y-axis label:"))
        self.text_label_window_title.setText(self.__tr("Window title:"))
        self.text_label_x_axis_label.setText(self.__tr("X-axis label:"))
        self.tab_widget_categories.changeTab(self.Widget2,self.__tr("Labels"))
        self.group_box_major_grid.setTitle(self.__tr("Major Grid"))
        self.text_label_maj_grid_width.setText(self.__tr("Width:"))
        self.text_label_maj_grid_style.setText(self.__tr("Style:"))
        self.text_label_maj_grid_colour.setText(self.__tr("Colour:"))
        self.check_box_x_grid_maj_enable.setText(self.__tr("Enable X Major Grid"))
        self.check_box_y_grid_maj_enable.setText(self.__tr("Enable Y Major Grid"))
        self.push_button_maj_grid_colour.setText(QString.null)
        self.combo_box_maj_grid_style.clear()
        self.combo_box_maj_grid_style.insertItem(self.__tr("Solid Line"))
        self.combo_box_maj_grid_style.insertItem(self.__tr("Dashed Line"))
        self.combo_box_maj_grid_style.insertItem(self.__tr("Dotted Line"))
        self.combo_box_maj_grid_style.insertItem(self.__tr("Dash Dot Line"))
        self.combo_box_maj_grid_style.insertItem(self.__tr("Dash Dot Dot Line"))
        self.group_box_minor_grid.setTitle(self.__tr("Minor Grid"))
        self.text_label_min_grid_colour.setText(self.__tr("Colour:"))
        self.text_label_min_grid_width.setText(self.__tr("Width:"))
        self.text_label_min_grid_style.setText(self.__tr("Style:"))
        self.check_box_y_grid_min_enable.setText(self.__tr("Enable Y Minor Grid"))
        self.check_box_x_grid_min_enable.setText(self.__tr("Enable X Minor Grid"))
        self.push_button_min_grid_colour.setText(QString.null)
        self.combo_box_min_grid_style.clear()
        self.combo_box_min_grid_style.insertItem(self.__tr("Solid Line"))
        self.combo_box_min_grid_style.insertItem(self.__tr("Dashed Line"))
        self.combo_box_min_grid_style.insertItem(self.__tr("Dotted Line"))
        self.combo_box_min_grid_style.insertItem(self.__tr("Dash Dot Line"))
        self.combo_box_min_grid_style.insertItem(self.__tr("Dash Dot Dot Line"))
        self.tab_widget_categories.changeTab(self.TabPage,self.__tr("Grid (presently ignored!)"))
        self.line_edit_ratio.setText(self.__tr("1.0"))
        self.group_box_x_axis_range.setTitle(self.__tr("X-axis range"))
        self.check_box_x_auto_scale.setText(self.__tr("Enable X-axis Auto Scale"))
        self.text_label_x_min.setText(self.__tr("Minimum X value:"))
        self.line_edit_x_min.setText(self.__tr("0.0"))
        self.text_label_x_max.setText(self.__tr("Maximum X value:"))
        self.line_edit_x_max.setText(self.__tr("1000.0"))
        self.group_box_y_axis_range.setTitle(self.__tr("Y-axis range"))
        self.text_label_y_max.setText(self.__tr("Maximum Y value:"))
        self.text_label_y_min.setText(self.__tr("Minimum Y value:"))
        self.check_box_y_auto_scale.setText(self.__tr("Enable Y-axis Auto Scale"))
        self.line_edit_y_min.setText(self.__tr("0.0"))
        self.line_edit_y_max.setText(self.__tr("1000.0"))
        self.check_box_ratio.setText(self.__tr("Keep aspect ratio:"))
        self.tab_widget_categories.changeTab(self.Widget3,self.__tr("Axes"))
        self.buttonOk.setText(self.__tr("&OK"))
        self.buttonOk.setAccel(QString.null)
        self.buttonCancel.setText(self.__tr("&Cancel"))
        self.buttonCancel.setAccel(QString.null)

    def accept(self):
     QDialog.accept(self)
     
    def __tr(self,s,c = None):
        return qApp.translate("dialog_window_config",s,c)


def main(args):
    app = QApplication(args)
    demo = dialog_window_config()
    demo.show()
#   app.setMainWidget(demo)
    app.exec_loop()

# Admire
if __name__ == '__main__':
    main(sys.argv)

