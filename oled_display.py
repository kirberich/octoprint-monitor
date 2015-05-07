import serial


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


class Display(object):
    """ Communicate with arduino running oled_display """

    def __init__(self, dev, speed=9600, timeout=1):
        try:
            self.ser = serial.Serial(dev, speed, timeout=timeout)
        except:
            print "Couldn't initialise serial"
            self.ser = None

        # Set up by sending a clear command and waiting until it's acknowledged
        while not self.send_command('C')[0]:
            pass

    def send_command(self, command, wait_for_reply=True, wait_for_empty_buffer=True):
        """ Send serial command to arduino
            Set wait_for_reply to wait and return reply
            wait_for_empty_buffer to continue reading until the buffer is empty
        """
        if not self.ser:
            print "No serial device, not sending data."
            return

        retval = []
        self.ser.write(command+chr(127))
        if wait_for_reply:
            retval.append(self.ser.readline().strip())

        if wait_for_empty_buffer:
            while self.ser.inWaiting():
                retval.append(self.ser.readline().strip())
        return retval

    def draw_text(self, text, line=None):
        """ Draw some text on the display
            If line is none, text will be wrapped and scroll from bottom to top, otherwise
            text is just written to one specific line
        """
        if line is None:
            self.send_command("S{}".format(text))
        else:
            self.send_command("L{}{}".format(line, text))

    def draw_pixel(self, x, y, color=1):
        self.send_command('P{}{}{}'.format(chr(x), chr(y), chr(color)))

    def draw_pixels(self, pixels):
        for chunk in chunks(pixels, 30):
            command = "P"
            for x, y, color in chunk:
                command += "{}{}{}".format(chr(x), chr(y), chr(color))
            self.send_command(command)

    def clear(self):
        self.send_command("C")

    def update(self):
        self.send_command("U")
