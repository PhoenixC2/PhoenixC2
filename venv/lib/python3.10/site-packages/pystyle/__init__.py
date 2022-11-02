# made by billythegoat356, loTus01, and BlueRed

# https://github.com/billythegoat356 https://github.com/loTus04 https://github.com/CSM-BlueRed

# Version : 2.0 (added Colorate.Format, added Banner.Arrow, added Anime.Move, added Center.GroupAlign, added Center.TextAlign, updated Box to Banner, updated Box.Lines))

# based on pyfade anc pycenter, R.I.P

# <3


from os import name as _name, system as _system, get_terminal_size as _terminal_size, terminal_size
from sys import stdout as _stdout
from time import sleep as _sleep
from threading import Thread as _thread


if _name == 'nt':
    from ctypes import c_int, c_byte, Structure, byref, windll

    class _CursorInfo(Structure):
        _fields_ = [("size", c_int),
                    ("visible", c_byte)]


class System:

    """
    1 variable:
        Windows      |      tells if the user is on Windows OS or not
    5 functions:
        Init()       |      initialize the terminal to allow the use of colors
        Clear()      |      clear the terminal
        Title()      |      set the title of terminal, only for Windows
        Size()       |      set the size of terminal, only for Windows
        Command()    |      enter a shell command
    """

    Windows = _name == 'nt'

    def Init():
        _system('')

    def Clear():
        return _system("cls" if System.Windows else "clear")

    def Title(title: str):
        if System.Windows:
            return _system(f"title {title}")

    def Size(x: int, y: int):
        if System.Windows:
            return _system(f"mode {x}, {y}")

    def Command(command: str):
        return _system(command)



class Cursor:

    """
    2 functions:
        HideCursor()      |      hides the white blinking in the terminal
        ShowCursor()      |      shows the white blinking in the terminal
    """

    def HideCursor():
        if _name == 'nt':
            Cursor._cursor(False)
        elif _name == 'posix':
            _stdout.write("\033[?25l")
            _stdout.flush()

    def ShowCursor():
        if _name == 'nt':
            Cursor._cursor(True)
        elif _name == 'posix':
            _stdout.write("\033[?25h")
            _stdout.flush()

    """ ! developper area ! """

    def _cursor(visible: bool):
        ci = _CursorInfo()
        handle = windll.kernel32.GetStdHandle(-11)
        windll.kernel32.GetConsoleCursorInfo(handle, byref(ci))
        ci.visible = visible
        windll.kernel32.SetConsoleCursorInfo(handle, byref(ci))


class _MakeColors:

    """ ! developper area ! """

    def _makeansi(col: str, text: str) -> str:
        return f"\033[38;2;{col}m{text}\033[38;2;255;255;255m"

    def _rmansi(col: str) -> str:
        return col.replace('\033[38;2;', '').replace('m','').replace('50m', '').replace('\x1b[38', '')

    def _makergbcol(var1: list, var2: list) -> list:
        col = list(var1[:12])
        for _col in var2[:12]:
            col.append(_col)
        for _col in reversed(col):
            col.append(_col)
        return col

    def _start(color: str) -> str:
        return f"\033[38;2;{color}m"

    def _end() -> str:
        return "\033[38;2;255;255;255m"

    def _maketext(color: str, text: str, end: bool = False) -> str:
        end = _MakeColors._end() if end else ""
        return color+text+end

    def _getspaces(text: str) -> int:
        return len(text) - len(text.lstrip())

    def _makerainbow(*colors) -> list:
        colors = [color[:24] for color in colors]
        rainbow = []
        for color in colors:
            for col in color:
                rainbow.append(col)
        return rainbow
    
    def _reverse(colors: list) -> list:
        _colors = list(colors)
        for col in reversed(_colors):
            colors.append(col)
        return colors
    
    def _mixcolors(col1: str, col2: str, _reverse: bool = True) -> list:
        col1, col2 = _MakeColors._rmansi(col=col1), _MakeColors._rmansi(col=col2)
        fade1 = Colors.StaticMIX([col1, col2], _start=False)      
        fade2 = Colors.StaticMIX([fade1, col2], _start=False)
        fade3 = Colors.StaticMIX([fade1, col1], _start=False)
        fade4 = Colors.StaticMIX([fade2, col2], _start=False)
        fade5 = Colors.StaticMIX([fade1, fade3], _start=False)    
        fade6 = Colors.StaticMIX([fade3, col1], _start=False)
        fade7 = Colors.StaticMIX([fade1, fade2], _start=False)
        mixed = [col1, fade6, fade3, fade5, fade1, fade7, fade2, fade4, col2]
        return _MakeColors._reverse(colors=mixed) if _reverse else mixed 

class Colors:

    """
    54 variables (colors)
    
    3 lists:
        static_colors      |      colors that are static, ex: 'red' (can't be faded)
        dynamic_colors     |      colors that are dynamic, ex: 'blue_to_purple' (can be faded)
        all_colors         |      every color of static_colors and dynamic_colors
        
    3 functions:
        StaticRGB()        |      create your own fix/static color
        DynamicRGB()       |      create your own faded/dynamic color (soon...)
        StaticMIX()        |      mix two or more static colors
        DynamicMIX()       |      mix two or more dynamic colors
        Symbol()           |      create a colored symbol, ex: '[!]'
    """

    def StaticRGB(r: int, g: int, b: int) -> str:
        return _MakeColors._start(f"{r};{g};{b}")

    def DynamicRGB(r1: int, g1: int, b1: int, r2: int,
                   g2: int, b2: int) -> list: ...

    def StaticMIX(colors: list, _start: bool = True) -> str:
        rgb = []
        for col in colors:
            col = _MakeColors._rmansi(col=col)
            col = col.split(';')
            r = int(int(col[0]))
            g = int(int(col[1]))
            b = int(int(col[2]))
            rgb.append([r, g, b])
        r = round(sum(rgb[0] for rgb in rgb) / len(rgb))
        g = round(sum(rgb[1] for rgb in rgb) / len(rgb))
        b = round(sum(rgb[2] for rgb in rgb) / len(rgb))
        rgb = f'{r};{g};{b}'
        return _MakeColors._start(rgb) if _start else rgb

    def DynamicMIX(colors: list):
        _colors = []
        for color in colors:
            if colors.index(color) == len(colors) - 1:
                break
            _colors.append([color, colors[colors.index(color) + 1]])
        colors = [_MakeColors._mixcolors(col1=color[0], col2=color[1], _reverse=False) for color in _colors]

        final = []
        for col in colors:
            for col in col:
                final.append(col)
        return _MakeColors._reverse(colors=final)
            


    """ symbols """

    def Symbol(symbol: str, col: str, col_left_right: str, left: str = '[', right: str = ']') -> str:
        return f"{col_left_right}{left}{col}{symbol}{col_left_right}{right}{Col.reset}"


    """ dynamic colors """

    black_to_white = ["m;m;m"]
    black_to_red = ["m;0;0"]
    black_to_green = ["0;m;0"]
    black_to_blue = ["0;0;m"]

    white_to_black = ["n;n;n"]
    white_to_red = ["255;n;n"]
    white_to_green = ["n;255;n"]
    white_to_blue = ["n;n;255"]

    red_to_black = ["n;0;0"]
    red_to_white = ["255;m;m"]
    red_to_yellow = ["255;m;0"]
    red_to_purple = ["255;0;m"]

    green_to_black = ["0;n;0"]
    green_to_white = ["m;255;m"]
    green_to_yellow = ["m;255;0"]
    green_to_cyan = ["0;255;m"]

    blue_to_black = ["0;0;n"]
    blue_to_white = ["m;m;255"]
    blue_to_cyan = ["0;m;255"]
    blue_to_purple = ["m;0;255"]

    yellow_to_red = ["255;n;0"]
    yellow_to_green = ["n;255;0"]

    purple_to_red = ["255;0;n"]
    purple_to_blue = ["n;0;255"]

    cyan_to_green = ["0;255;n"]
    cyan_to_blue = ["0;n;255"]


    red_to_blue = ...
    red_to_green = ...

    green_to_blue = ...
    green_to_red = ...

    blue_to_red = ...
    blue_to_green = ...

    rainbow = ...

    """ static colors """

    red = _MakeColors._start('255;0;0')
    green = _MakeColors._start('0;255;0')
    blue = _MakeColors._start('0;0;255')

    white = _MakeColors._start('255;255;255')
    black = _MakeColors._start('0;0;0')
    gray = _MakeColors._start('150;150;150')

    yellow = _MakeColors._start('255;255;0')
    purple = _MakeColors._start('255;0;255')
    cyan = _MakeColors._start('0;255;255')

    orange = _MakeColors._start('255;150;0')
    pink = _MakeColors._start('255;0;150')
    turquoise = _MakeColors._start('0;150;255')

    light_gray = _MakeColors._start('200;200;200')
    dark_gray = _MakeColors._start('100;100;100')

    light_red = _MakeColors._start('255;100;100')
    light_green = _MakeColors._start('100;255;100')
    light_blue = _MakeColors._start('100;100;255')

    dark_red = _MakeColors._start('100;0;0')
    dark_green = _MakeColors._start('0;100;0')
    dark_blue = _MakeColors._start('0;0;100')

    reset = white

    """ ! developper area ! """

    col = (list, str)

    dynamic_colors = [
        black_to_white, black_to_red, black_to_green, black_to_blue,
        white_to_black, white_to_red, white_to_green, white_to_blue,

        red_to_black, red_to_white, red_to_yellow, red_to_purple,
        green_to_black, green_to_white, green_to_yellow, green_to_cyan,
        blue_to_black, blue_to_white, blue_to_cyan, blue_to_purple,

        yellow_to_red, yellow_to_green,
        purple_to_red, purple_to_blue,
        cyan_to_green, cyan_to_blue
    ]

    for color in dynamic_colors:
        _col = 20
        reversed_col = 220

        dbl_col = 20
        dbl_reversed_col = 220

        content = color[0]
        color.pop(0)

        for _ in range(12):

            if 'm' in content:
                result = content.replace('m', str(_col))
                color.append(result)

            elif 'n' in content:
                result = content.replace('n', str(reversed_col))
                color.append(result)

            _col += 20
            reversed_col -= 20

        for _ in range(12):

            if 'm' in content:
                result = content.replace('m', str(dbl_reversed_col))
                color.append(result)

            elif 'n' in content:
                result = content.replace('n', str(dbl_col))
                color.append(result)

            dbl_col += 20
            dbl_reversed_col -= 20

    red_to_blue = _MakeColors._makergbcol(red_to_purple, purple_to_blue)
    red_to_green = _MakeColors._makergbcol(red_to_yellow, yellow_to_green)

    green_to_blue = _MakeColors._makergbcol(green_to_cyan, cyan_to_blue)
    green_to_red = _MakeColors._makergbcol(green_to_yellow, yellow_to_red)

    blue_to_red = _MakeColors._makergbcol(blue_to_purple, purple_to_red)
    blue_to_green = _MakeColors._makergbcol(blue_to_cyan, cyan_to_green)

    rainbow = _MakeColors._makerainbow(
        red_to_green, green_to_blue, blue_to_red)

    for _col in (
        red_to_blue, red_to_green,
        green_to_blue, green_to_red,
        blue_to_red, blue_to_green
    ): dynamic_colors.append(_col)

    dynamic_colors.append(rainbow)

    static_colors = [
        red, green, blue,
        white, black, gray,
        yellow, purple, cyan,
        orange, pink, turquoise,
        light_gray, dark_gray,
        light_red, light_green, light_blue,
        dark_red, dark_green, dark_blue,
        reset
    ]

    all_colors = [color for color in dynamic_colors]
    for color in static_colors:
        all_colors.append(color)


Col = Colors


class Colorate:

    """
    6 functions:
        Static colors:
            Color()                 |            color a text with a static color
            Error()                 |            make an error with red text and advanced arguments
            Format()                |            set different colors for different parts of a text
        Dynamic colors:
            Vertical()              |           fade a text vertically
            Horizontal()            |           fade a text horizontally
            Diagonal()              |           fade a text diagonally
            DiagonalBackwards()     |           fade a text diagonally but backwards
    """

    """ fix/static colors """

    def Color(color: str, text: str, end: bool = True) -> str:
        return _MakeColors._maketext(color=color, text=text, end=end)

    def Error(text: str, color: str = Colors.red, end: bool = False, spaces: bool = 1, enter: bool = True, wait: int = False) -> str:
        content = _MakeColors._maketext(
            color=color, text="\n" * spaces + text, end=end)
        if enter:
            var = input(content)
        else:
            print(content)
            var = None

        if wait is True:
            exit()
        elif wait is not False:
            _sleep(wait)

        return var

    """ faded/dynamic colors"""

    def Vertical(color: list, text: str, speed: int = 1, start: int = 0, stop: int = 0, cut: int = 0, fill: bool = False) -> str:
        color = color[cut:]
        lines = text.splitlines()
        result = ""

        nstart = 0
        color_n = 0
        for lin in lines:
            colorR = color[color_n]
            if fill:
                result += " " * \
                    _MakeColors._getspaces(
                        lin) + "".join(_MakeColors._makeansi(colorR, x) for x in lin.strip()) + "\n"
            else:
                result += " " * \
                    _MakeColors._getspaces(
                        lin) + _MakeColors._makeansi(colorR, lin.strip()) + "\n"  

            if nstart != start:
                nstart += 1
                continue

            if lin.rstrip():
                if (
                    stop == 0
                    and color_n + speed < len(color)
                    or stop != 0
                    and color_n + speed < stop
                ):
                    color_n += speed
                elif stop == 0:
                    color_n = 0
                else:
                    color_n = stop

        return result.rstrip()

    def Horizontal(color: list, text: str, speed: int = 1, cut: int = 0) -> str:
        color = color[cut:]
        lines = text.splitlines()
        result = ""

        for lin in lines:
            carac = list(lin)
            color_n = 0
            for car in carac:
                colorR = color[color_n]
                result += " " * \
                    _MakeColors._getspaces(
                        car) + _MakeColors._makeansi(colorR, car.strip())
                if color_n + speed < len(color):
                    color_n += speed
                else:
                    color_n = 0
            result += "\n"
        return result.rstrip()

    def Diagonal(color: list, text: str, speed: int = 1, cut: int = 0) -> str:

        color = color[cut:]
        lines = text.splitlines()
        result = ""
        color_n = 0
        for lin in lines:
            carac = list(lin)
            for car in carac:
                colorR = color[color_n]
                result += " " * \
                    _MakeColors._getspaces(
                        car) + _MakeColors._makeansi(colorR, car.strip())
                if color_n + speed < len(color):
                    color_n += speed
                else:
                    color_n = 1
            result += "\n"

        return result.rstrip()

    def DiagonalBackwards(color: list, text: str, speed: int = 1, cut: int = 0) -> str:
        color = color[cut:]

        lines = text.splitlines()
        result = ""
        resultL = ''
        color_n = 0
        for lin in lines:
            carac = list(lin)
            carac.reverse()
            resultL = ''
            for car in carac:
                colorR = color[color_n]
                resultL = " " * \
                    _MakeColors._getspaces(
                        car) + _MakeColors._makeansi(colorR, car.strip()) + resultL
                if color_n + speed < len(color):
                    color_n += speed
                else:
                    color_n = 0
            result = result + '\n' + resultL
        return result.strip()

    def Format(text: str, second_chars: list, mode, principal_col: Colors.col, second_col: str):
        if mode == Colorate.Vertical:
            ctext = mode(principal_col, text, fill=True)
        else:
            ctext = mode(principal_col, text)
        ntext = ""
        for x in ctext:
            if x in second_chars:
                x = Colorate.Color(second_col, x)
            ntext += x
        return ntext


class Anime:

    """
    2 functions:
        Fade()                  |            make a small animation with a changing color text, using a dynamic color
        Move()                  |            make a small animation moving the text from left to right
        Bar()                   |            a fully customizable charging bar
        Anime()                 |            a mix between Fade() and Move(), available soon
    """

    def Fade(text: str, color: list, mode, time=True, interval=0.05, hide_cursor: bool = True, enter: bool = False):
        if hide_cursor:
            Cursor.HideCursor()

        if type(time) == int:
            time *= 15

        global passed
        passed = False

        if enter:
            th = _thread(target=Anime._input)
            th.start()

        if time is True:
            while True:
                if passed is not False:
                    break
                Anime._anime(text, color, mode, interval)
                ncolor = color[1:]
                ncolor.append(color[0])
                color = ncolor

        else:
            for _ in range(time):
                if passed is not False:
                    break
                Anime._anime(text, color, mode, interval)
                ncolor = color[1:]
                ncolor.append(color[0])
                color = ncolor

        if hide_cursor:
            Cursor.ShowCursor()

    def Move(text: str, color: list, time = True, interval = 0.01, hide_cursor: bool = True, enter: bool = False):
        if hide_cursor:
            Cursor.HideCursor()

        if type(time) == int:
            time *= 15

        global passed
        passed = False

        columns = _terminal_size().columns

        if enter:
            th = _thread(target = Anime._input)
            th.start()

        count = 0
        mode = 1

        if time is True:
            while not passed:
                if mode == 1:
                    if count >= (columns - (max(len(txt) for txt in text.splitlines()) + 1)):
                        mode = 2
                    count += 1
                elif mode == 2:
                    if count <= 0:
                        mode = 1
                    count -= 1
                Anime._anime('\n'.join((' ' * count) + line for line in text.splitlines()), color or [], lambda a, b: b, interval)
        else:
            for _ in range(time):
                if passed:
                    break
                if mode == 1:
                    if count >= (columns - (max(len(txt) for txt in text.splitlines()) + 1)):
                        mode = 2
                elif mode == 2:
                    if count <= 0:
                        mode = 1
                Anime._anime('\n'.join((' ' * count) + line for line in text.splitlines()), color or [], lambda a, b: b, interval)

                count += 1

        if hide_cursor:
            Cursor.ShowCursor()


    def Bar(length, carac_0: str = '[ ]', carac_1: str = '[0]', color: list = Colors.white, mode=Colorate.Horizontal, interval: int = 0.5, hide_cursor: bool = True, enter: bool = False, center: bool = False):
        if hide_cursor:
            Cursor.HideCursor()

        if type(color) == list:
            while not length <= len(color):
                ncolor = list(color)
                for col in ncolor:
                    color.append(col)

        global passed
        passed = False

        if enter:
            th = _thread(target=Anime._input)
            th.start()

        for i in range(length + 1):
            bar = carac_1 * i + carac_0 * (length - i)
            if passed:
                break
            if type(color) == list:
                if center:
                    print(Center.XCenter(mode(color, bar)))
                else:
                    print(mode(color, bar))
            else:
                if center:
                    print(Center.XCenter(color + bar))
                else:
                    print(color + bar)
            _sleep(interval)
            System.Clear()
        if hide_cursor:
            Cursor.ShowCursor()

    def Anime() -> None: ...

    """ ! developper area ! """

    def _anime(text: str, color: list, mode, interval: int):
        _stdout.write(mode(color, text))
        _stdout.flush()
        _sleep(interval)
        System.Clear()

    def _input() -> str:
        global passed
        passed = input()
        return passed


class Write:
    """
    2 functions:
        Print()         |          print a text to the terminal while coloring it and with a fade and write effect
        Input()         |          same than Print() but adds an input to the end and returns its valor
    """

    def Print(text: str, color: list, interval=0.05, hide_cursor: bool = True, end: str = Colors.reset) -> None:
        if hide_cursor:
            Cursor.HideCursor()

        Write._write(text=text, color=color, interval=interval)

        _stdout.write(end)
        _stdout.flush()

        if hide_cursor:
            Cursor.ShowCursor()

    def Input(text: str, color: list, interval=0.05, hide_cursor: bool = True, input_color: str = Colors.reset, end: str = Colors.reset) -> str:
        if hide_cursor:
            Cursor.HideCursor()

        Write._write(text=text, color=color, interval=interval)

        valor = input(input_color)

        _stdout.write(end)
        _stdout.flush()

        if hide_cursor:
            Cursor.ShowCursor()

        return valor

    " ! developper area ! "

    def _write(text: str, color, interval: int):
        lines = list(text)
        if type(color) == list:
            while not len(lines) <= len(color):
                ncolor = list(color)
                for col in ncolor:
                    color.append(col)

        n = 0
        for line in lines:
            if type(color) == list:
                _stdout.write(_MakeColors._makeansi(color[n], line))
            else:
                _stdout.write(color + line)
            _stdout.flush()
            _sleep(interval)
            if line.strip():
                n += 1


class Center:

    """
    2 functions:
        XCenter()                  |             center the given text in X cords
        YCenter()                  |             center the given text in Y cords
        Center()                   |             center the given text in X and Y cords
        GroupAlign()               |             align the given text in a group
        TextAlign()                |             align the given text per lines

    NOTE: the functions of the class can be broken if the text argument has colors in it
    """

    center = 'CENTER'
    left = 'LEFT'
    right = 'RIGHT'

    def XCenter(text: str, spaces: int = None, icon: str = " "):
        if spaces is None:
            spaces = Center._xspaces(text=text)
        return "\n".join((icon * spaces) + text for text in text.splitlines())

    def YCenter(text: str, spaces: int = None, icon: str = "\n"):
        if spaces is None:
            spaces = Center._yspaces(text=text)

        return icon * spaces + "\n".join(text.splitlines())

    def Center(text: str, xspaces: int = None, yspaces: int = None, xicon: str = " ", yicon: str = "\n") -> str:
        if xspaces is None:
            xspaces = Center._xspaces(text=text)

        if yspaces is None:
            yspaces = Center._yspaces(text=text)

        text = yicon * yspaces + "\n".join(text.splitlines())
        return "\n".join((xicon * xspaces) + text for text in text.splitlines())

    def GroupAlign(text: str, align: str = center):
        align = align.upper()
        if align == Center.center:
            return Center.XCenter(text)
        elif align == Center.left:
            return text
        elif align == Center.right:
            length = _terminal_size().columns
            maxLineSize = max(len(line) for line in text.splitlines())
            return '\n'.join((' ' * (length - maxLineSize)) + line for line in text.splitlines())
        else:
            raise Center.BadAlignment()
    
    def TextAlign(text: str, align: str = center):
        align = align.upper()
        mlen = max(len(i) for i in text.splitlines())
        if align == Center.center:

            return "\n".join((' ' * int(mlen/2 - len(lin)/2)) + lin for lin in text.splitlines())
        elif align == Center.left:
            return text
        elif align == Center.right:
            ntext = '\n'.join(' ' * (mlen - len(lin)) + lin for lin in text.splitlines())
            return ntext
        else:
            raise Center.BadAlignment()


    """ ! developper area ! """

    def _xspaces(text: str):
        try:
            col = _terminal_size().columns
        except OSError:
            return 0
        textl = text.splitlines()
        ntextl = max((len(v) for v in textl if v.strip()), default = 0)
        return int((col - ntextl) / 2)

    def _yspaces(text: str):
        try:
            lin = _terminal_size().lines
        except OSError:
            return 0
        textl = text.splitlines()
        ntextl = len(textl)
        return int((lin - ntextl) / 2)

    class BadAlignment(Exception):
        def __init__(self):
            super().__init__("Choose a correct alignment: Center.center / Center.left / Center.right")

class Add:

    """
    1 function:
        Add()           |           allow you to add a text to another, and even center it
    """

    def Add(banner1, banner2, spaces=0, center=False):
        if center:
            split1 = len(banner1.splitlines())
            split2 = len(banner2.splitlines())
            if split1 > split2:
                spaces = (split1 - split2) // 2
            elif split2 > split1:
                spaces = (split2 - split1) // 2
            else:
                spaces = 0

        if spaces > max(len(banner1.splitlines()), len(banner2.splitlines())):
            # raise Banner.MaximumSpaces(spaces)
            spaces = max(len(banner1.splitlines()), len(banner2.splitlines()))

        ban1 = banner1.splitlines()
        ban2 = banner2.splitlines()

        ban1count = len(ban1)
        ban2count = len(ban2)

        size = Add._length(ban1)

        ban1 = Add._edit(ban1, size)

        ban1line = 0
        ban2line = 0
        text = ''

        for _ in range(spaces):

            if ban1count >= ban2count:
                ban1data = ban1[ban1line]
                ban2data = ''

                ban1line += 1

            else:
                ban1data = " " * size
                ban2data = ban2[ban2line]

                ban2line += 1

            text = text + ban1data + ban2data + '\n'
        while ban1line < ban1count or ban2line < ban2count:

            ban1data = ban1[ban1line] if ban1line < ban1count else " " * size
            ban2data = ban2[ban2line] if ban2line < ban2count else ""
            text = text + ban1data + ban2data + '\n'

            ban1line += 1
            ban2line += 1
        return text

    """ ! developper area ! """

    class MaximumSpaces(Exception):
        def __init__(self, spaces: str):
            super().__init__(f"Too much spaces [{spaces}].")

    def _length(ban1):
        bigestline = 0

        for line in ban1:
            if len(line) > bigestline:
                bigestline = len(line)
        return bigestline

    def _edit(ban1, size):
        return [line + (size - len(line)) * " " for line in ban1]


class Banner:

    """
    2 functions:
        SimpleCube()                  |             create a simple cube with the given text
        Lines()                       |             create a text framed by two lines
        Arrow()                       |             create a custom arrow
    """

    def Box(content: str, up_left: str, up_right: str, down_left: str, down_right: str, left_line: str, up_line: str, right_line: str, down_line: str) -> str:
        l = 0
        lines = content.splitlines()
        for a in lines:
            if len(a) > l:
                l = len(a)
        if l % 2 == 1:
            l += 1
        box = up_left + (up_line * l) + up_right + "\n"
        #box += "║ " + (" " * int(l / 2)) + (" " * int(l / 2)) + " ║\n"
        for line in lines:
            box += left_line + " " + line + (" " * int((l - len(line)))) + " " + right_line + "\n"
        box += down_left + (down_line * l) + down_right + "\n"
        return box


    def SimpleCube(content: str) -> str:
        l = 0
        lines = content.splitlines()
        for a in lines:
            if len(a) > l:
                l = len(a)
        if l % 2 == 1:
            l += 1
        box = "__" + ("_" * l) + "__\n"
        box += "| " + (" " * int(l / 2)) + (" " * int(l / 2)) + " |\n"
        for line in lines:
            box += "| " + line + (" " * int((l - len(line)))) + " |\n"
        box += "|_" + ("_" * l) + "_|\n"

        return box

    def DoubleCube(content: str) -> str:
        return Box.Box(content, "╔═", "═╗", "╚═", "═╝", "║", "═", "║", "═")

    def Lines(content: str, color = None, mode = Colorate.Horizontal, line = '═', pepite = 'ቐ') -> str:
        l = 1
        for c in content.splitlines():
            if len(c) > l:
                l = len(c)
        mode = Colorate.Horizontal if color is not None else (lambda **kw: kw['text'])
        box = mode(text = f"─{line*l}{pepite * 2}{line*l}─", color = color)
        assembly = box + "\n" + content + "\n" + box
        final = ''
        for lines in assembly.splitlines():
            final += Center.XCenter(lines) + "\n"
        return final
    
    def Arrow(icon: str = 'a', size: int = 2, number: int = 2, direction = 'right') -> str:
        spaces = ' ' * (size + 1)
        _arrow = ''
        structure = (size + 2, [size * 2, size * 2])
        count = 0
        if direction == 'right':
            for i in range(structure[1][0]):
                line = (structure[0] * icon)
                _arrow += (' ' * count) + spaces.join([line] * (number)) + '\n'
                count += 2

            for i in range(structure[1][0] + 1):
                line = (structure[0] * icon)
                _arrow += (' ' * count) + spaces.join([line] * (number)) + '\n'
                count -= 2
        elif direction == 'left':
            for i in range(structure[1][0]):
                count += 2

            for i in range(structure[1][0]):
                line = (structure[0] * icon)
                _arrow += (' ' * count) + spaces.join([line] * (number)) + '\n'
                count -= 2

            for i in range(structure[1][0] + 1):
                line = (structure[0] * icon)
                _arrow += (' ' * count) + spaces.join([line] * (number)) + '\n'
                count += 2
        return _arrow


Box = Banner

System.Init()