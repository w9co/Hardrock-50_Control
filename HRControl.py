import serial
import sys
import time

import PySimpleGUI as sg

COM_PORT = 'COM3'
BAUD_RATE = 19200
SERIAL_TIMEOUT = 1

## HRMD - keying mode
#0=off
#1=ptt
#2=cor

## HRBN - band
#0=6M
#1=10M
#2=12M
#3=15M
#4=17M
#5=20M
#6=30M
#7=40M
#8=60M=UNK
#9=80M
#10=160M

bands = (
    ['0', '6M'],
    ['1', '10M'],
    ['2', '12M'],
    ['3', '15M'],
    ['4', '17M'],
    ['5', '20M'],
    ['6', '30M'],
    ['7', '40M'],
#   ['8', 'UNK'] #(60M?),
    ['9', '80M'],
    ['10', '160M'],
)

##HRTP - temp
#0=F
#1=C

temps = ['C', 'F']


##HRVT - volts

##HRRX - rx status - csv of rx status, keying mode, band, temp, voltage


ICON = b'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'
theme_dict = {'BACKGROUND': '#2B475D',
              'TEXT': '#FFFFFF',
              'INPUT': '#F2EFE8',
              'TEXT_INPUT': '#000000',
              'SCROLL': '#F2EFE8',
              'BUTTON': ('#000000', '#C2D4D8'),
              'PROGRESS': ('#FFFFFF', '#C7D5E0'),
              'BORDER': 1,'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0}

sg.theme_add_new('Dashboard', theme_dict)
sg.LOOK_AND_FEEL_TABLE['Dashboard'] = theme_dict
sg.theme('Dashboard')

POLL_FREQUENCY = 2000
BORDER_COLOR = '#C7D5E0'
DARK_HEADER_COLOR = '#1B2838'
BPAD_TOP = ((20,20), (20, 10))
BPAD_LEFT = ((20,10), (0, 10))
BPAD_LEFT_INSIDE = (0, 10)
BPAD_RIGHT = ((10,20), (10, 20))

curr_band = '-------'
curr_temp = '--------'
curr_voltage = '--------'
curr_keying = '-----'

def change_band(band_id):
    # make call to HRBN<band_id> to change band
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT)
    band_str = 'HRBN' + band_id + ';'
    ser.write(str.encode(band_str))
    ser.close()

def change_keying(keying):
    # make call to HRMD to change keying.    
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT)
    if keying == 'OFF':
        ser.write(b'HRMD0;')
    elif keying == 'PTT':
        ser.write(b'HRMD1;')
    elif keying == 'COR':
        ser.write(b'HRMD2;')
    ser.close()

def change_temp(cf):
    # make call to HRMD to change keying.
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT)
    if cf == 'F':
        ser.write(b'HRTP0;')
    elif cf == 'C':
        ser.write(b'HRTP1;')
    ser.close()

def update_display(window):
    # make call to HRRX to get updated display values.
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=SERIAL_TIMEOUT)
    ser.write(b'HRRX;')
    time.sleep(0.5)
    result = ser.readline()
    result = result.decode("utf-8").rstrip().replace(';', '')
    res_arr = result.split(',')
    if len(res_arr) < 2:
        return

    #update band display
    for band in bands:
        if res_arr[2] == band[1]:
            window[band[0]].update(button_color=('green', 'white'))
        else:
            window[band[0]].update(button_color=('white', 'black'))
    if res_arr[2] == '160':
        window['band_display'].update('160M')
    elif res_arr[2] == '6M':
        window['band_display'].update('  6M')
    else:
        window['band_display'].update(' ' + res_arr[2])

    #update keying display
    for keying in keyings:
        if res_arr[1] == keying:
            window[keying].update(button_color=('green', 'white'))
        else:
            window[keying].update(button_color=('gray', 'darkgrey'))

    #update temperature display
    window['temp_display'].update(' ' + res_arr[3])

    #update voltage display
    window['voltage_display'].update(' ' + res_arr[4])


band_row1 = []
band_row2 = []
for band in bands:
    if int(band[0]) < 5:
        band_row1.append(
            sg.Button(band[1], button_color=('white', 'black'), key=band[0])
        )
    else:
        band_row2.append(
            sg.Button(band[1], button_color=('white', 'black'), key=band[0])
        )

band_block  = [band_row1, band_row2]

keyings = ['PTT', 'COR', 'OFF']
ptt_btn = sg.Button('PTT', button_color=('gray', 'darkgrey'), key='PTT')
cor_btn = sg.Button('COR', button_color=('gray', 'darkgrey'), key='COR')
off_btn = sg.Button('OFF', button_color=('gray', 'darkgrey'), key='OFF')

band_disp = [
    [sg.Text(' ' + curr_band, font='Any 60', key='band_display')],
]

temp_disp = [
    [sg.Text(' ' + curr_temp, font='Any 20', key='temp_display')],
]

voltage_disp = [
    [sg.Text(' ' + curr_voltage, font='Any 20', key='voltage_display')],
]

keying_disp = [
    [sg.Text(' ' + curr_keying, font='Any 10')],
]

layout = [
    [sg.Column(band_block, size=(455, 70)),],
    [
        sg.Column(band_disp, size=(217,100)),
        sg.Column([
            [sg.Column(temp_disp, size=(125,40))],
            [sg.Column(voltage_disp, size=(125,40)),],
        ], size=(125, 100)),
        sg.Column([
            [ptt_btn],
            [cor_btn],
            [off_btn],
        ], size=(93, 100)),
    ],
]

window = sg.Window(
    'BDP Hardrock-50 Control', 
    layout,
    margins=(0,0),
    auto_size_buttons=False,
    default_button_element_size=(9,1),
    background_color=BORDER_COLOR,
    icon=ICON, 
)

while True:             # Event Loop
    event, values = window.read(timeout=POLL_FREQUENCY)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    elif event in [band[0] for band in bands]:
        band_id = event
        change_band(band_id)
        update_display(window)

    elif event in keyings:
        key_id = event
        change_keying(key_id)
        update_display(window)

    else:
        update_display(window)

window.close()
