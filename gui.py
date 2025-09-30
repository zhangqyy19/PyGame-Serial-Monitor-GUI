import pygame
import pygame_gui
from collections import deque
import random

import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox

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
import event_functions

enable_serial_monitor = 1 # 0-disable 1-in app 2-in terminal

serial_msg_text = ""
joysticks = None


class Options:
    def __init__(self):
        self.resolution = (600, 800)
        self.fullscreen = False

class OptionsUIApp:
    def __init__(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100,45)
        pygame.init()
        pygame.display.set_caption("Options UI")
        self.options = Options()

        if self.options.fullscreen:
            self.window_surface = pygame.display.set_mode(self.options.resolution,
                                                          pygame.FULLSCREEN)
        else:
            self.window_surface = pygame.display.set_mode(self.options.resolution)

        self.background_surface = None

        self.ui_manager = UIManager(self.options.resolution,
                                    PackageResource(package='data.themes',
                                                    resource='theme_2.json'))
        self.ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 10, 'style': 'bold'},
                                       {'name': 'fira_code', 'point_size': 10, 'style': 'regular'},
                                       {'name': 'fira_code', 'point_size': 10, 'style': 'italic'},
                                       {'name': 'fira_code', 'point_size': 14, 'style': 'italic'},
                                       {'name': 'fira_code', 'point_size': 14, 'style': 'bold'}
                                       ])

        
        self.test_drop_down = None

        self.serial_monitor_mode_header_textbox = None
        self.serial_monitor_mode = None

        self.serial_select_dropdown = None
        self.serial_connect_button = None
        self.serial_refresh_button = None
        self.serial_baudrate_textbox = None
        self.serial_test_button = None #test button

        self.serial_msg_disp = None
        self.serial_msg_entry = None

        self.recreate_ui()

        self.clock = pygame.time.Clock()
        self.time_delta_stack = deque([])

        self.button_response_timer = pygame.time.Clock()
        self.running = True
        self.debug_mode = False

        self.all_enabled = True
        self.all_shown = True

    def recreate_ui(self):
        event_functions.recreate_ui_helperfunction(self)

    def create_message_window(self):
        self.button_response_timer.tick()
        self.message_window = UIMessageWindow(
            rect=pygame.Rect((random.randint(0, self.options.resolution[0] - 300),
                              random.randint(0, self.options.resolution[1] - 200)),
                             (300, 250)),
            window_title='Test Message Window',
            html_message='this is a message',
            manager=self.ui_manager)
        time_taken = self.button_response_timer.tick() / 1000.0
        # currently taking about 0.35 seconds down from 0.55 to create
        # an elaborately themed message window.
        # still feels a little slow but it's better than it was.
        print("Time taken to create message window: " + str(time_taken))

    def check_resolution_changed(self):
        print(self.test_drop_down.selected_option)
        resolution_string = self.test_drop_down.selected_option[0].split('x')
        resolution_width = int(resolution_string[0])
        resolution_height = int(resolution_string[1])
        if (resolution_width != self.options.resolution[0] or
                resolution_height != self.options.resolution[1]):
            self.options.resolution = (resolution_width, resolution_height)
            self.window_surface = pygame.display.set_mode(self.options.resolution)
            self.recreate_ui()



    def process_events(self):
        global enable_serial_monitor
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.ui_manager.process_events(event)


            if (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED):
                if (event.ui_object_id == '#main_text_entry'):
                    print("main: " + event.text)
                if (event.ui_object_id == '#serial_text_entry'):
                    try:
                        str_to_be_sent = event.text
                        utf8str = str_to_be_sent.encode('utf-8') + b'\n'
                        print("Sent: ", end="")
                        print(utf8str)
                        gvar_ctrl.mcu_serial_object.write(utf8str)
                        self.serial_msg_entry.set_text("")
                    except:
                        print("Send failed!")
                    

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.serial_connect_button:
                    try:
                        print("--Connecting to {}".format(self.serial_select_dropdown.selected_option[0]))
                        conn_baud = int(self.serial_baudrate_textbox.get_text())
                        gvar_ctrl.mcu_serial_object = serial.Serial(port=self.serial_select_dropdown.selected_option[0], baudrate=conn_baud, timeout=.1)
                    except:
                        print("--Connection failed")
                    else:
                        print("--Connected")

                if event.ui_element == self.serial_refresh_button:
                    try:
                        print(self.serial_select_dropdown.options_list)
                        self.serial_select_dropdown.options_list = [('not selected', 'not selected')]
                        ports = serial.tools.list_ports.comports()
                        for port, desc, hwid in sorted(ports):
                                self.serial_select_dropdown.add_options([str(port)])
                    except:
                        print("i don't know why but refresing failed")

                if event.ui_element == self.serial_test_button:
                    print("Test button pressed")
                    

            if (event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED):
                if (event.ui_element == self.test_drop_down):
                    self.check_resolution_changed()
                if (event.ui_element == self.serial_monitor_mode):
                    # ['In app', 'In terminal', 'Disable']
                    if self.serial_monitor_mode.selected_option == 'In app':
                        enable_serial_monitor = 1
                    elif self.serial_monitor_mode.selected_option == 'In terminal':
                        enable_serial_monitor = 2
                    elif self.serial_monitor_mode.selected_option == 'Disable':
                        enable_serial_monitor = 0
                    else:
                        enable_serial_monitor = 0

    def run(self):
        global joysticks
        global enable_serial_monitor
        global serial_msg_text

        global context

        serial_msg_text_size = 200

        while self.running:
            time_delta = self.clock.tick() / 1000.0
            self.time_delta_stack.append(time_delta)
            if len(self.time_delta_stack) > 2000:
                self.time_delta_stack.popleft()
            # check for input
            self.process_events()
            # respond to input
            self.ui_manager.update(time_delta)
            # draw graphics
            self.window_surface.blit(self.background_surface, (0, 0))
            self.ui_manager.draw_ui(self.window_surface)
            pygame.display.update()

            ###change this stuff bc created new serial_handler file^^
    
    class Slider:
        def __init__(self, pos: tuple, size: tuple, initial_val: float, min: int, max: int) -> None:
            self.pos = pos
            self.size = size

            self.slider_left_pos = self.pos[0] - (size[0] // 2)
            self.slider_right_pos = self.pos[0] - (size[0] // 2)
            self.slider_top_pos = self.pos[1] - (size[1] // 2)

            self.min = min
            self.max = max
            self.initial_val = (self.slider_right_pos - self.slider_left_pos) * initial_val


        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
        self.button_rect = pygame.Rect(self.slider_left_pos + self.initial_val - 5, self.slider_top_pos, 10, self.size[1])

        # label
        self.text = UI.fonts['m'].render(str(int(self.get_value())), True, "white", None)
        self.label_rect = self.text.get_rect(center = (self.pos[0], self.slider_top_pos - 15))
        
        def move_slider(self, mouse_pos):
            pos = mouse_pos[0]
            if pos < self.slider_left_pos:
                pos = self.slider_left_pos
            if pos > self.slider_right_pos:
                pos = self.slider_right_pos
            self.button_rect.centerx = pos

        def hover(self):
            self.hovered = True

        def render(self, app):
            pygame.draw.rect(app.screen, "darkgray", self.container_rect)
            pygame.draw.rect(app.screen, BUTTONSTATES[self.hovered], self.button_rect)
        
        def get_value(self):
            val_range = self.slider_right_pos - self.slider_left_pos - 1
            button_val = self.button_rect.centerx - self.slider_left_pos

            return (button_val/val_range)*(self.max-self.min)+self.min
        
        def display_value(self, app):
            self.text = UI.fonts['m'].render(str(int(self.get_value())), True, "white", None)
            app.screen.blit(self.text, self.label_rect)









