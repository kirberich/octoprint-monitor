import time
import sys
from datetime import datetime

from oled_display import Display
from octo_api import OctoApi

try:
    import settings
except ImportError:
    print "Couldn't load settings."
    print "Copy settings.py.example to settings.py and set your api key."
    sys.exit(1)

class Monitor(object):
    def __init__(self, dev):
        self.display = Display(dev)
        self.api = OctoApi(settings.OCTOPRINT_HOST+"/api", settings.API_KEY)

        self.night_start = settings.NIGHT_FROM_HOUR
        self.night_end = settings.NIGHT_UNTIL_HOUR
        self.cold_temp_threshold = settings.COLD_TEMPERATURE

        self.animation_frame = 0
        self.is_printing = False

    @property
    def is_night(self):
        now = datetime.now()
        if now.hour >= self.night_start or now.hour <= self.night_end:
            return True
        return False

    def draw_error(self, e):
        """ Simple error screen """
        self.display.clear()
        self.display.draw_text("Error:", 0)
        line = 1
        for message in e.message:
            self.display.draw_text(message, line)
            line += 1

        self.draw_animation()
        self.display.update()

    def draw_animation(self):
        """ Add a small animation in the bottom left corner of the display.
            This doesn't update the display as it's meant to included in the normal display views.
        """

        border = [
            (2, 61, 1), (2, 62, 1),
            (3, 60, 1), (4, 60, 1),
            (5, 61, 1), (5, 62, 1),
            (3, 63, 1), (4, 63, 1),
        ]

        frames = [
            (3, 61, 1),
            (4, 61, 1),
            (4, 62, 1),
            (3, 62, 1),
        ]
        self.display.draw_pixels(border + [frames[self.animation_frame]])

        self.animation_frame = (self.animation_frame + 1) % 4

    def draw_printing_status(self, job_status):
        file_name = job_status['job']['file']['name'].rsplit(".", 1)[0]

        try:
            estimated_total = int(job_status['job']['estimatedPrintTime'])/60
        except:
            estimated_total = "??"

        # printTime is an indicator for the actual print having started
        if job_status['progress']['printTime']:
            percent_finished = int(round(float(job_status['progress']['completion'])))

            estimated_left = int(job_status['progress']['printTimeLeft'])/60
            # Sometimes the estimation is completely borked and reports negative numbers.
            if estimated_left < 0:
                estimated_left = "??"

            time_elapsed = int(job_status['progress']['printTime'])/60
        else:
            percent_finished = 0
            estimated_left = estimated_total
            time_elapsed = 0

        self.display.draw_text(file_name, 0)
        self.display.draw_text("{}%".format(percent_finished), 1)

        self.display.draw_text("{} / {}".format(self.current_temp, self.target_temp), 3)
        self.display.draw_text("Total: {}m".format(estimated_total), 4)
        self.display.draw_text("Elapsed: {}m".format(time_elapsed), 5)
        self.display.draw_text("Remaining: {}m".format(estimated_left), 6)

        self.display.update()

    def draw_night_display(self):
        if self.current_temp > self.cold_temp_threshold or self.target_temp > self.cold_temp_threshold:
            self.display.draw_text("PRINTER IS HOT", 2)
            self.display.draw_text("{} / {}".format(self.current_temp, self.target_temp), 3)
        else:
            self.display.draw_text("", 2)
            self.display.draw_text("off", 3)

    def draw_idle_status(self):
        self.display.draw_text("Octoprint Monitor", 0)

        # Draw some decorative lines under the title
        lines = [(x,8,1) for x in range(15,112)] + [(x,9,1) for x in range(13,114)]
        self.display.draw_pixels(lines)

        self.display.draw_text("Status: {}".format(self.current_state), 2)
        self.display.draw_text("Temp: {} / {}".format(self.current_temp, self.target_temp), 3)

    def update(self):
        try:
            conn_status = self.api.connection_status()
            printer_status = self.api.printer_status()
            job_status = self.api.job_status()
        except Exception, e:
            # If anything at all goes wrong just dump it on the display and wait for this all to blow over
            print e
            self.draw_error(e)
            return

        self.current_state = printer_status['state']['text']
        self.current_temp = printer_status['temperature']['tool0']['actual']
        self.target_temp = printer_status['temperature']['tool0']['target']

        self.is_printing = self.current_state == 'Printing'

        self.display.clear()

        if self.is_printing:
            self.draw_printing_status(job_status)
        elif self.is_night:
            self.draw_night_display()
        else:
            self.draw_idle_status()

        self.draw_animation()
        self.display.update()

    def loop(self):
        while True:
            self.update()
            time.sleep(10 if self.is_night and not self.is_printing else 1)
