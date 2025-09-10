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
              
def open_serial_log(log_path="./serial_log"):
    try:
        dir_list = os.listdir(log_path)
    except Exception as e:
        print("open_serial_log: ", e)
        print("Creating a folder with name " + log_path)
        os.mkdir(log_path)
        dir_list = os.listdir(log_path)
    dir_list = [f for f in dir_list if os.path.isfile(log_path+'/'+f)]

    largest_index = 0

    for each_log in dir_list:
        # getting numbers from string 
        temp = re.findall(r'\d+', each_log)
        res = list(map(int, temp))
        largest_index = max([largest_index, res[0]])

    
    gvar_ctrl.serial_log_file = open(log_path + '/serial_log_' + str(largest_index+1) + '.txt', 'w')
        


if __name__ == '__main__':
    ports = serial.tools.list_ports.comports()
    open_serial_log()
    for port, desc, hwid in sorted(ports):
            print("{}: [{}]".format(port, hwid))

    app = gui.OptionsUIApp()
    app.run()
