# pyserial
import pygame
import pygame_gui
from collections import deque
import random

import serial
import serial.tools.list_ports
import os
import re

from pygame_gui import UIManager, PackageResource

from pygame_gui.elements import UIButton
from pygame_gui.elements import UITextEntryLine
from pygame_gui.elements import UIDropDownMenu
from pygame_gui.elements import UILabel
from pygame_gui.elements.ui_text_box import UITextBox

from pygame_gui.windows import UIMessageWindow

import gvar_ctrl
import gui
            
if (enable_serial_monitor != 0) and (gvar_ctrl.mcu_serial_object is not None):
    numBytesToRead = gvar_ctrl.mcu_serial_object.in_waiting
    if(numBytesToRead > 0):
        line_readed = gvar_ctrl.mcu_serial_object.readline()
        gvar_ctrl.serial_log_file.write(str(line_readed)+'\n')
        if enable_serial_monitor == 1: # in app option
            serial_msg_text += (str(line_readed)+'\n')
            self.serial_msg_disp.appended_text += (str(line_readed)+'\n')
            self.serial_msg_disp.set_text(serial_msg_text)
        if self.serial_msg_disp.get_text_letter_count() > serial_msg_text_size:
            diff = self.serial_msg_disp.get_text_letter_count()
            serial_msg_text = serial_msg_text[diff:]
            if self.serial_msg_disp.scroll_bar is not None:
            # set the scroll bar to the bottom
                percentage_visible = (self.serial_msg_disp.text_wrap_rect[3] /self.serial_msg_disp.text_box_layout.layout_rect.height)
            self.serial_msg_disp.scroll_bar.start_percentage = 1.0 - percentage_visible
            self.serial_msg_disp.scroll_bar.scroll_position = (self.serial_msg_disp.scroll_bar.start_percentage * self.serial_msg_disp.scroll_bar.scrollable_height)
            self.serial_msg_disp.redraw_from_text_block()
        if enable_serial_monitor == 2: # in terminal option
            print(line_readed)