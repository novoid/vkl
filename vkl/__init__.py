#!/usr/bin/env python3
# -*- coding: utf-8 -*-
PROG_VERSION = u"Time-stamp: <2018-02-03 20:47:04 vk>"

"""
vkpyls
~~~~~~

This tool provides various alternative visualizations of
directory contents.

:copyright: (c) 2010 by Karl Voit <tools@Karl-Voit.at>
:license: GPL v3 or any later version
:bugreports: <tools@Karl-Voit.at>

See USAGE below for details!

FIXXME:
    * BUG: broken links are missing in output!
    * add possibility to specify directory (other than current directory)
    * find additional metrics
    * additional parameter: print out groups of items sorted by alphabet
    * move from optparse to argparse

"""
import logging, os, sys, time, datetime
from optparse import OptionParser


## "True": use "ls" to print out verbose list of items
## "False": use python simple printout
CONFIG_USE_GNU_LS=True

PROG_VERSION_DATE = PROG_VERSION[13:23]

## modify this to your taste although the default setting is quite cool already :-)
if sys.platform=="darwin":
    GNU_LS_OPTIONS='-lt -a -r -d -G'
else: ## hope, that GNU ls is installed ;-)
    GNU_LS_OPTIONS='-lt --all --reverse --directory --classify --color=auto'


## NOTE: find out about colors with:
## for i in range(1,100):
##         print str(i) + '\033['+str(i)+'m' + "Test" + '\033[0m'
## COLOUR_CODE='\033[43m' ## yellowish, suitable for white background
## COLOUR_CODE='\033[43m' ## yellow
COLOUR_CODE='\033[7m' ## invert


## ======================================================================= ##
##                                                                         ##
##         You should NOT need to modify anything below this line!         ##
##                                                                         ##
## ======================================================================= ##


## initialize config setting as global variable
USE_GNU_LS=""

USAGE = "\n\
         %prog <options>\n\
\n\
This tool lists the current directory content in various metric\n\
GNU ls does not provide.\n\n\
:copyright: (c) 2010-now by Karl Voit <tools@Karl-Voit.at>\n\
:version: " + PROG_VERSION_DATE + "\n\
:license: GPL v3 or any later version\n\
:bugreports: <tools@Karl-Voit.at>"


parser = OptionParser(usage=USAGE)

parser.add_option("-l", "--log", dest="pseudologtime", action="store_true", default=True,
                  help="displays directory content by a pseudo logarithmic time (default option)")

parser.add_option("-m", "--mtime", dest="mtime", action="store_true",
                  help="sort items using modification time (default option)")

parser.add_option("-c", "--ctime", dest="ctime", action="store_true",
                  help="sort items using change time")

parser.add_option("-a", "--atime", dest="atime", action="store_true",
                  help="sort items using access time")

parser.add_option("-p", "--primitivels", dest="primitivels", action="store_true",
                  help="use primitive output of directory rather than using GNU ls")

parser.add_option("-d", "--delegate", dest="delegate", action="store", default='',
                  help="delegate additional arguments to ls command")

parser.add_option("--debug", dest="debug", action="store_true",
                  help="enable (senseless) debug output")

## parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
##                   help="do not output anything but just errors on console")

(options, args) = parser.parse_args()



def handle_logging():
    """Log handling and configuration"""

    if options.debug:
        FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
##     elif options.quiet:
##         FORMAT = "%(levelname)-8s %(message)s"
##         logging.basicConfig(level=logging.CRITICAL, format=FORMAT)
    else:
        FORMAT = "%(message)s"
        logging.basicConfig(level=logging.INFO, format=FORMAT)


def get_directory_items_with_times():
    """returns a list containing all directory items as dictionaries with their a/c/mtimes"""

    items = []
    for item in os.listdir("."):
        if not os.path.exists(item):
            logging.warn("WARNING: \"" + item + "\" seems to be a broken link")
        else:
            items.append( {"name":item, "mtime":os.path.getmtime(item), "ctime":os.path.getctime(item),
                "atime":os.path.getatime(item) } )

    logging.debug("found "+str( len(items) )+" items")

    return items



def debug_output_of_items(items, timemetrics):
    """prints debug output of items"""

    logging.debug(" " + timemetrics + "         " + str( len(items) )+" items")
    for item in items:
        logging.debug(" " + str(item[timemetrics]) + "  of item " + str(item['name']) )


def sort_items_by_time(items, mcatime):
    """sorts list of item-dictionaries by m- c- or atime"""

    logging.debug("sort_items_by_time got    "+str( len(items) )+" items")
    newlist = items.sort(key=lambda x: x['mtime'])
    logging.debug("sort_items_by_time sorted "+str( len(newlist) )+" items")

    return newlist


def print_out_items(items, mcatime, use_gnu_ls):
    """print out items in given list"""

    justificationlength = 2

    if use_gnu_ls:

        ## make a string with all item names to give it to 'ls' as a package (for nice formatting):
        unfolded_itemstring = ""
        for item in items:
            unfolded_itemstring += " \"" + item['name'] + "\""

        ## ls accepts --time=(atime|ctime) with mtime as default if no option is given
        timeoption=""
        if not mcatime=="mtime":
            timeoption="--time=" + mcatime

        ## on OS X, SysV ls uses other options for amc-time:
        if sys.platform=="darwin":
                if mcatime=="mtime":
                        timeoption="" ## mtime is default
                elif mcatime=='ctime':
                        timeoption="-c"
                elif mcatime=='atime':
                        timeoption="-u"

        os.system('ls %s %s %s %s' % (options.delegate, timeoption, GNU_LS_OPTIONS, unfolded_itemstring))   ## ... using system function

    else:

        for item in items:
            # logging.info(" ".ljust(justificationlength) + str(item['name']) )   ## ... using python output
            print((str( item['name'] )))   ## ... using simple python output


def print_colored_string(string):
    """prints out a coloured string"""

    ## NOTE: find out about colors with:
    ## for i in range(1,100):
    ##         print str(i) + '\033['+str(i)+'m' + "Test" + '\033[0m'

    if sys.platform == 'win32':
        print('—' * 20 + '→' + string)  # no colors for Windows, so sad. :-(
    else:
        print(COLOUR_CODE + string + '\033[0m')


def list_dir_pseudologtime(items, timemetrics, use_gnu_ls):
    """lists directory content in a pseudo logarithmic time format"""

    now=time.time()
    logging.debug("current time: " + str(now) )

    logtable = [ \
    { 'seconds':60*30 , 'shortname':"30 min ", 'longname':"half an hour" , 'visual':" "} , \
    { 'seconds':60*30 , 'shortname':"30 min ", 'longname':"recently" , 'visual':" "} , \
    { 'seconds':60*60              , 'shortname':"1 h ", 'longname':"1 hour  "          , 'visual':".. h                                    "} , \
    { 'seconds':60*60*3            , 'shortname':"3 h ", 'longname':"3 hours  "         , 'visual':".. hhh                                  "} , \
    { 'seconds':60*60*24           , 'shortname':"1 d ", 'longname':"1 day  "           , 'visual':"........ d                             "} , \
    { 'seconds':60*60*24*7         , 'shortname':"1 w ", 'longname':"1 week  "          , 'visual':"........ ddddddd                       "} , \
    { 'seconds':60*60*24*30        , 'shortname':"1 m ", 'longname':"1 month "          , 'visual':"........ ddddddd ddddddd ddddddd ddddddd"} , \
    { 'seconds':60*60*24*30*3      , 'shortname':"3 m ", 'longname':"3 months  "        , 'visual':"............ mmm                       "} , \
    { 'seconds':60*60*24*30*6      , 'shortname':"6 m ", 'longname':"6 months  "        , 'visual':"............ mmm mmm                   "} , \
    { 'seconds':60*60*24*30*12     , 'shortname':"1 y ", 'longname':"a year  "          , 'visual':"............ mmm mmm mmm mmm           "} ]

    current_time_to_compare = logtable.pop()

    logging.debug(" " + timemetrics + "   " + str( len(items) )+" items")
    infostring = ""
    items_to_print = []
    for item in items:

        logging.debug("comparing item (" + str(item['name']) + ") and " + current_time_to_compare['longname'] + " (" +
                str(str(current_time_to_compare['seconds']))  + "): now-itemtime (" \
                + str(now - item[timemetrics]) + ") < " + str(current_time_to_compare['seconds']) + \
                " = " + str( now - item[timemetrics] < current_time_to_compare['seconds'] ) )

        ## as long as current item < next-loglevel: pop:
        while logtable and (now - item[timemetrics] < current_time_to_compare['seconds'] ):

            indentlength = 2

            if use_gnu_ls:
                indentlength = 25

            infostring = " ".ljust(indentlength, ' ') + "< " + current_time_to_compare['longname'].ljust(10, ' ')

            current_time_to_compare = logtable.pop()

        # logging.debug(" " + str(item[timemetrics]) + "  of item " + str(item['longname']) )

        ## print out infostring and clear it (if given):
        if infostring:

            ## before corresponding next infostring, print previous items as a bunch:
            print_out_items( items_to_print, timemetrics, use_gnu_ls )
            items_to_print = []

            print_colored_string(infostring)
            infostring = ""

        items_to_print.append(item)

    ## if no infostring is left, print out rest of items:
    if items_to_print:
        print_out_items( items_to_print, timemetrics, use_gnu_ls )

def main():
    """Main function [make pylint happy :)]"""

    handle_logging()

    ## error handling:

    if (options.mtime and options.ctime) or \
       (options.ctime and options.atime) or \
       (options.atime and options.mtime):
        logging.error("please choose only one of mtime, ctime, or atime!")
        os.sys.exit(2)

    if not (options.pseudologtime):
        logging.error("please choose one option of log!")
        os.sys.exit(1)

    ## do things:

    ## handle "use GNU ls" according to default setting or override via command line:
    if options.primitivels:
        USE_GNU_LS=False   ## override via command line switch
    elif sys.platform == 'win32':
        USE_GNU_LS=False   ## override for primitive Windows shell
    else:
        USE_GNU_LS=CONFIG_USE_GNU_LS  ## use default setting from very above
    logging.debug( "USE_GNU_LS=" + str(USE_GNU_LS) )

    items = get_directory_items_with_times()

    ## sort items according to time:
    if options.mtime:
        logging.debug("sorting by mtime")
        items.sort(key=lambda x: x['mtime'])
        TIMEMETRICS='mtime'
    elif options.ctime:
        logging.debug("sorting by ctime")
        items.sort(key=lambda x: x['ctime'])
        TIMEMETRICS='ctime'
    elif options.atime:
        logging.debug("sorting by atime")
        items.sort(key=lambda x: x['atime'])
        TIMEMETRICS='atime'
    else:
        logging.debug("no option for atime, ctime, or mtime was found. using default: mtime")
        items.sort(key=lambda x: x['mtime'])
        TIMEMETRICS='mtime'

    debug_output_of_items(items, TIMEMETRICS)

    if options.pseudologtime:
        logging.debug("pseudo log time parameter recognised")
        list_dir_pseudologtime(items, TIMEMETRICS, USE_GNU_LS)
        os.sys.exit(0)



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################
# vim:foldmethod=indent expandtab ai ft=python tw=120 fileencoding=utf-8 shiftwidth=4
