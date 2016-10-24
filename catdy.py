#!/usr/bin/python2

# Author: Joseph Wiseman <joswiseman@cock.li>
# URL: https://github.com/dryes/catdy/

import argparse
import os
import re
import sys


def init_argparse():
    parser = argparse.ArgumentParser(description='scene category determiner, yes.',
                                     usage=os.path.basename(sys.argv[0]) + ' [--opts] input1 [input2] ...')

    parser.add_argument('input', nargs='*',
                        help='dirname/directory', default='')

    parser.add_argument('--catonly', '-c', action='store_true',
                        help='only print category - no dirname', default=False)
    parser.add_argument('--lower', '-l', action='store_true',
                        help='print category in lowercase', default=False)

    args = parser.parse_args()
    return vars(args)


def match(tag, dirname):
    return True if re.search(r'[._-]%s[._-]' % tag, dirname) is not None else False


def filecount(input, fileext):
    if not os.path.isdir(input):
        return False

    count = 0
    for f in os.listdir(input):
        if re.search(r'\.%s$' % fileext, f, re.IGNORECASE) is not None:
            count = (count + 1)

    return count


def _isvideo(dirname):
    return match(r'(B[DR]RIP|BLURAY|(DV)?DIVX|DVDRIP|M?DVD[59R]|[HX][._-]?26[45]|HDDVD|SUB(TITLE)?S?[._-]?(FIX|PACK)|S?VCD|WMV(\-?HD)?|XVID(VD)?)', dirname)


def _isretail(dirname):
    return match('(B[DR]RIP|BLURAY|(XVI)?DVD(RIP|IVX)|HDDVD|LASERDISC|VHS(RIP)?)', dirname)


def _istv(dirname):
    return match('(A?DSR(RIP)?|A?[HPS]DTV(RIP)?|TVRIP|WEB(\-?DL|HD(RIP)?|RIP)?)', dirname)


def _ishd(dirname):
    return match('(720P|1080P|2160P)', dirname)


def _isseries(dirname):
    return match('((?<!^)(\d{4}\.\d{2}\.\d{2}|\d{1,3}X\d{1,4}|S\d{1,3}([DE]\d{1,3}[A-Z]?)+?|[ES](eason|eries|pisode)?\d{1,3}[A-Z]?))', dirname)


def _isaudio(dirname, input):
    if match(r'A(UDIO)?BOOK', dirname):
        return 'ABOOK'

    if match(r'FLAC', dirname):
        return 'FLAC'

    if filecount(input, 'mp3'):
        return 'MP3'

    return False


def _is0day(input, dirname):
    if not filecount(input, 'zip'):
        return False

    if match(r'EBOOK', dirname):
        return 'EBOOK'

    if match(r'LINUX', dirname):
        return '0DAY-LINUX'

    if match(r'MAC(OSX)?', dirname):
        return '0DAY-MAC'

    return '0DAY'


def _isconsole(dirname):
    return match(r'(DC|GB[AC]|[3N]DS|N?GC|PS[1234PVX](CD|DVD([59]|RIP)?|ITA)?|WIIU?|XBOX|X(BOX)?360|XBOXONE)', dirname)


def _isiso(input, dirname):
    if not filecount(input, '(rar|001|iso|bin)'):
        return False

    if match(r'LINUX', dirname):
        return 'ISO-LINUX'

    if match(r'MAC(OSX)?', dirname):
        return 'ISO-MAC'

    return 'ISO'


def video(dirname):
    # work right > left for tags.
    # eg. 720p.HDTV.x264-GRP
    # codec > source > resolution

    isretail = _isretail(dirname)
    istv = _istv(dirname)
    ishd = _ishd(dirname)
    isseries = _isseries(dirname)

    if match('COMPLETE[._-]BLURAY', dirname):
        if isseries:
            return 'BLURAY-SERIES'
        else:
            return 'BLURAY'

    if match('DDC', dirname):
        return 'MVID'

    if match('DIVX|XVID', dirname):
        if isretail and isseries:
            return 'XVID-SERIES'
        elif istv and not isretail:
            return 'TV-XVID'
        else:
            return 'XVID'

    if match('M?DVD[59R](?![._-]RIP)', dirname):
        if match('MDVD[59R]?', dirname):
            return 'MDVDR'
        elif isseries:
            return 'DVDR-SERIES'
        else:
            return 'DVDR'

    if match('[HX][._-]?264', dirname):
        if isretail and ishd and isseries:
            return 'X264-SERIES-HD'
        elif isretail and isseries:
            return 'X264-SERIES'
        elif istv and not isretail and ishd:
            return 'TV-HD-X264'
        elif istv and not isretail:
            return 'TV-X264'
        elif ishd:
            return 'X264-HD'
        else:
            return 'X264'

    if match('[HX][._-]?265', dirname):
        if isretail and ishd and isseries:
            return 'X265-SERIES-HD'
        elif isretail and isseries:
            return 'X265-SERIES'
        elif istv and not isretail and ishd:
            return 'TV-HD-X265'
        elif istv and not isretail:
            return 'TV-X265'
        elif ishd:
            return 'X265-HD'
        else:
            return 'X265'

    if match('S?VCD', dirname):
        if isseries:
            return 'VCD-SERIES'
        else:
            return 'VCD'

    if match('WMV(\-?HD)?', dirname):
        if isretail and ishd and isseries:
            return 'WMV-SERIES-HD'
        elif isretail and isseries:
            return 'WMV-SERIES'
        elif istv and not isretail and ishd:
            return 'TV-HD-WMV'
        elif istv and not isretail:
            return 'TV-WMV'
        elif ishd:
            return 'WMV-HD'
        else:
            return 'WMV'

    return None


def console(dirname):
    if match('3DS', dirname):
        return 'CONSOLE-3DS'

    if match('DC(?![._-]COMICS)', dirname):
        return 'CONSOLE-DC'

    if match('GBA(?![._-]INJECT)', dirname):
        return 'CONSOLE-GBA'

    if match('GBC(?![._-]INJECT)', dirname):
        return 'CONSOLE-GBC'

    if match('N?GC', dirname):
        return 'CONSOLE-NGC'

    if match('PS[1X]', dirname):
        return 'CONSOLE-PSX'

    if match('PS2(CD|DVD([59]|RIP)?)?', dirname):
        return 'CONSOLE-PS2'

    if match('PS3', dirname):
        return 'CONSOLE-PS3'

    if match('PS4', dirname):
        return 'CONSOLE-PS4'

    if match('PSP', dirname):
        return 'CONSOLE-PSP'

    if match('PSV(ITA)?', dirname):
        return 'CONSOLE-PSVITA'

    if match('WII(?![._-]U)', dirname):
        return 'CONSOLE-WII'

    if match('WII[._-]?U', dirname):
        return 'CONSOLE-WIIU'

    if match('XBOX1?(?![._-](360|ONE))', dirname):
        return 'CONSOLE-XBOX'

    if match('X(BOX)?[._-]?360', dirname):
        return 'CONSOLE-XBOX360'

    if match('XBOXONE', dirname):
        return 'CONSOLE-XBOXONE'

    return None


def main(input):
    dirname = input.split(os.sep)[-1].upper()

    if _isvideo(dirname):
        return video(dirname)

    isaudio = _isaudio(dirname, input)
    if isaudio:
        return isaudio

    is0day = _is0day(input, dirname)
    if is0day:
        return is0day

    if _isconsole(dirname):
        return console(dirname)

    isiso = _isiso(input, dirname)
    if isiso:
        return isiso

    return None


if __name__ == '__main__':
    args = init_argparse()
    inputlen = len(args['input'])

    for d in args['input']:
        cat = main(d)

        if not cat:
            cat = 'None'

        if args['lower']:
            cat = cat.lower()

        if args['catonly']:
            print('%s' % cat)
            if inputlen == 1:
                sys.exit(1)
            continue

        print('%s > %s' % (d, cat))
