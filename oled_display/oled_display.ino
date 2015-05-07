#include "U8glib.h"
U8GLIB_SSD1306_132X64 u8g(10, 9, 12, 11, 8);
//                        D0, D1,CS, DC, RST

String string_buffer[7];
uint8_t matrix[16*64]; // 16*8 pixels per row, 64 rows
const int max_input = 128;
char input_buffer[max_input];

void u8g_prepare(void) {
	u8g.begin();
	u8g.setFont(u8g_font_lucasfont_alternate);
	u8g.setFontRefHeightExtendedText();
	u8g.setDefaultForegroundColor();
	u8g.setFontPosTop();
}

void clear_screen() {
	for (int i=0; i<7; i++){
		string_buffer[i] = String("");
	}

	for(int i=0; i<(16*64); i++) {
		matrix[i] = 0;
	}
}

void buffer_line(String new_string, int line) {
	// Buffer a line. Can either scroll existing lines if called with line == -1
	// or set a specific line.

	if (line == -1) {
		for (int i=1; i<7; i++){
			string_buffer[i-1] = string_buffer[i];
		}
		string_buffer[6] = new_string;
	} else {
		string_buffer[line] = new_string;
	}
}

void buffer_line(String new_string) {
	buffer_line(new_string, -1);
}

void scroll_text(String input){
	// Scrolls existing text content up, adding new lines at the bottom.
	// A single string is passed in, which is split into several lines if it's too long.

	String part = input;
	int length = 1;
	int start_pos = 0;
	int font_width = 0;

	while (true) {
		char char_buf[length+1];
		part.toCharArray(char_buf, length+1);
		font_width = u8g.getStrWidth(char_buf);

		if (length < part.length() && font_width < 123) {
			length += 1;
		} else {
			start_pos = start_pos + length;
			buffer_line(char_buf);

			part = input.substring(start_pos);
			length = 1;
		}
		if (!part.length()){
			break;
		}
	}
}

void handle_command(char *command, int length) {
	switch(command[0]) {
		case 'C':
			clear_screen();
			break;
		case 'U':
			draw_screen();
			break;
		case 'S':
			// Normal string. Simply scroll text
			scroll_text(String(command + 1));
			break;
		case 'L':
			// Specific line. arg: line number
			Serial.println(command[1], DEC);
			Serial.println(command[1]-'0', DEC);
			buffer_line(String(command + 2), command[1] - '0');
			break;
		case 'P':
			// Pixel data. Format is X, Y, 1/0, X, Y 1/0, ...
			// For example: P001101201301401501...
			// Note that here we're using byte values, not encoded strings.
			int data_len = length - 1;
			if (data_len % 3) {
				Serial.print("ERROR: Pixel data was of unexpected length ");
				Serial.println(data_len);
			} else {
				int matrix_index;
				byte matrix_bit;
				byte x;
				byte y;
				byte color;

				for(int i=1; i <= data_len-2; i+=3) {
					x = command[i];
					y = command[i+1];
					color = command[i+2];

					matrix_index = (x / 8) + 16*y;
					matrix_bit = 7 - x % 8;

					if(color) {
						bitSet(matrix[matrix_index], matrix_bit);
					} else {
						bitClear(matrix[matrix_index], matrix_bit);
					}
				}
			}
			break;
	}
}

void draw_screen() {
	u8g.firstPage();
	u8g.setColorIndex(1);
	do {
		u8g.drawBitmap(0, 0, 16, 64, matrix);

		for (int i=0; i<7; i++){
			char tmp[50];
			string_buffer[i].toCharArray(tmp, 50);
			int font_width = u8g.getStrWidth(tmp);
			u8g.drawStr(max(0, 64-font_width/2), i*9-1, tmp);
		}
	} while(u8g.nextPage());
}

void setup(void) {
	Serial.begin(9600);
	u8g_prepare();
	clear_screen();
	draw_screen();
}

void loop(void) {
	if (Serial.available()) {
		int bytes = Serial.readBytesUntil(0x7f, input_buffer, max_input);
		input_buffer[bytes] = 0;
		handle_command(input_buffer, bytes);
		Serial.println("ok");
	}

	// Wait for data
	while(!Serial.available()) {
	}
}


