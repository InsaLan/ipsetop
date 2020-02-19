import curses

class Screen:
    def __init__(self, scr):
        self.scr = scr
        self.scr.clear()
        curses.curs_set(0)
        curses.halfdelay(10)

    def draw_frame(self, data):
        self.scr.clear()
        start = self.print_header(data)
        end = self.print_footer(data)
        self.print_content(data, start, end)

        self.scr.refresh()

    def print_header(self, data):

        x = self.scr.getmaxyx()[1]
        marks = x//15
        unit = ""
        line = "└"
        for i in range(1, marks+1):
            l = int(x/marks*i)
            unit += pad(format_bw(data["max"]/marks*i), len(unit)-l)
            line += pad("┴", len(line)-l, "─")
        self.scr.addstr(0, 0, unit)
        self.scr.addstr(1, 0, line)
        return 2

    def print_footer(self, data):
        y,x = self.scr.getmaxyx()
        
        count = len(data["vpn"])
        self.scr.addstr(y-count-1, 0, "─"*x)
        self.scr.addstr(y-count-1, 10, "┬")
        self.scr.addstr(y-count-1, 10 + (x-10)//2, "┬")
        for i,vpn in enumerate(data["vpn"]):
            self.print_vpn(vpn, y-count+i)
        return y-count-1

    def print_content(self, data, start, end):
        for i,user in enumerate(data["users"][:(end-start)//2]):
            self.print_user(user, i*2+start)

    def print_vpn(self, vpn, line):
        y,x = self.scr.getmaxyx()
        name, (df, d1, d2, d3), (df, u1, u2 , u3) = vpn

        self.scr.addstr(line, 0, name)
        self.scr.addstr(line, 10, "│")
        self.scr.addstr(line, 10 + (x-10)//2, "│")

        down_bw = pad(format_bw(d1), -9) + pad(format_bw(d2), -9) + pad(format_bw(d3), -9)
        up_bw = pad(format_bw(u1), -9) + pad(format_bw(u2), -9) + pad(format_bw(u3), -9)
        down_text = " <="
        down_text += pad(down_bw , len(down_text)-(x-13)//2)
        up_text = " =>"
        up_text += pad(up_bw , len(up_text)-(x-13)//2)
        self.print_bar(line, 11, down_text, frac=df)
        self.print_bar(line, 11 + (x-10)//2, up_text, frac=df)


    def print_user(self, user, line):
        y,x = self.scr.getmaxyx()

        draw_width = x-27

        name, (df, d1, d2, d3), (uf, u1, u2 , u3) = user

        down_bw = pad(format_bw(d1), -9) + pad(format_bw(d2), -9) + pad(format_bw(d3), -9)
        up_bw = pad(format_bw(u1), -9) + pad(format_bw(u2), -9) + pad(format_bw(u3), -9)

        down_text = pad(pad(name, -draw_width//4), draw_width//2-1) + "<="
        down_text += pad("nothing yet", -draw_width//4)
        down_text += pad(down_bw, len(down_text)-x)
        up_text = pad("", draw_width//2-1) + "=>"
        up_text += pad(up_bw, len(up_text)-x)

        self.print_bar(line, 0, down_text, df)
        self.print_bar(line+1, 0, up_text, uf)

    def print_bar(self, y, x, text, frac=0):
        pos = int(len(text)*frac)
        self.scr.addstr(y, x, text[:pos], curses.A_REVERSE)
        self.scr.addstr(y, x+pos, text[pos:])


def format_bw(val):
    if val >= 1024**3*10:
        return "{:.1f}gb".format(val/1024**3)
    if val >= 1024**2*10:
        return "{:.1f}mb".format(val/1024**2)
    elif val >= 1024*10:
        return "{:.1f}kb".format(val/1024)
    else:
        return "{:.1f} b".format(val)

def pad(val, count, char=" "):
    if count > 0:
        return val + char*(count - len(val))
    else:
        return char*(-count - len(val)) + val
