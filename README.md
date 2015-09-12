# octoprint-monitor
An arduino-based display for a 3d-printer running on octoprint. Very much geared towards use with a printrbot simple/plus, as it doesn't come with its own display. Needs an arduino and a sainsmart 1.3 inch SPI OLED screen, but should be easily adaptable to other screens supported by u8g.
 
The script has no external dependencies. Just download, install the sketch to an arduino through the arduino app, copy the example settings (`cp settings.py.example settings.py`) and adjust them according to your server settings. Run the script with `python main.py /dev/<arduino-device>`.

You can look up the name of the arduino-device in the arduino app. On Linux it's usually ttyUSB0, on macos tty.usbmodemXXXX.
