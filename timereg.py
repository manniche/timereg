#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2009-03-07 23:00:30 stm>
# todo:
# 1: fix minutes timestamping, when minutes < 10 (the 0 gets thrown away)
# 2: last entry in the txt file has a broken timestamp = not stringified
# 3: set default task when beginning

import time, sys, os
from os import system
import datetime
from ConfigParser import ConfigParser
from calendar import monthrange

try :
    # we prefer the extended debugger
    import pydb as pdb
except ImportError:
    # but we are content with any debugger
    import pdb as pdb

class Logger(object):
    def __init__(self):
        self.logfile = 'timereg.log'

class Timereg(object):
    def __init__( self, outputtype, debug=False ):

        # debug_mode determines whether we end up in the debugger
        self.debug_mode = debug

        # intervaltime should be deleted
        self.intervaltime = None

        # activity_reg holds the current activity
        self.activity_reg = []

        # job_no holds the id for the current running job
        self.job_no = 0

        # determine whether a job is active
        self.is_job_running=False

        filestamp = time.strftime(  'y%Y-m%m-d%d-w%V', time.localtime( ) )

        self.outputtype = outputtype

        self.out_file = filestamp+'.txt'

                
    #main contains the main loop
    def main(self):
        config = ConfigParser()
        
        config.read( '.activities' )
        #config.read( os.path.expanduser( '~/.activities') )

        for section in config.sections():
            print section
            for option in config.options(section):
                print section, option, config.get( section, option )
                #print "%s: '%s:s'"%( config.get( section, option ), section, option )

        self.activities = []

        #c = timereg()
        #amount = range(len(c.activities))

        while True:
#       system('clear')
            if len(self.activity_reg) > 0:
                active =  self.activity_reg[self.job_no-1][0]
                print 'active:%s'%(active)
                for it in self.activities:
                    if it == active:
                        descr = self.activities[it]
                        print "Current activity: ",descr
                        break
            try:
                for number, activity in enumerate(self.activities):
                    print activity,' '*(3-len(str(activity))),' = '+ self.activities[activity]
                    #print 'now registering time for ',self.activities[len(self.activities)][0], '(',self.activities[len(self.activities)][1],')'
                    #print '\n'*1
                t = raw_input("Which activity?\n\tPress q to quit\n> ")

                if t == 'q':
                    print "you pressed quit\nSo be it!"
                    if self.outputtype == 'txt':
                        self.save_list()
                    elif self.outputtype == 'tid':
                        self.save_list_tidsreg()
                    print 'exiting...'
                    sys.exit(0)

                elif int(t) in range(len(self.activities)):
                    t = int(t)
                    #print "the length of list(activities) is ",len(c.activities), "you picked number ", int(t), "\n representing ", c.activities[int(t)]
                    #i=0
                    result = {t: self.set_status(t)}[t]

                else:
                    print "the number you pressed is not in your list.\nPlease review your list by pressing 'l'."
                    #c.print_list(c.activity_reg)

            except ValueError:
                t2 = raw_input( "No action is accociated with the pressed digit '%s'.\n Should I exit? (n or any other key to quit)"%( str(t) ) )

                if t2 == 'n':
                    continue
                else:
                    sys.exit(0)

    def begin(self):
        self.is_job_running=True
        return time.time()

    def end(self):
        if self.is_job_running != True:
            sys.exit("there are no jobs running. I error. And end. Bye.")
        else:
            return time.time()

    def end_job(self):
        if not self.is_job_running:
            return
        end = self.end()
        end_time = time.strftime( '%d/%m-%Y %H:%M:%S', time.localtime( end ) )
        self.activity_reg[ self.job_no-1 ].insert( 2, end_time ) #human-readable time
        self.activity_reg[ self.job_no-1 ].insert( 4, end )  #epoch time stamp
        self.is_job_running = False

    def set_status(self,list_number):
        if self.is_job_running:
            self.end_job()

        self.activity_reg.insert( self.job_no, [] )
        self.activity_reg[self.job_no].insert( 0, list_number )
        begin = self.begin()
        begin_time = time.strftime( '%d/%m-%Y %H:%M:%S', time.localtime( begin ) )
        self.activity_reg[ self.job_no ].insert( 1, begin_time )  # human-readable time
        self.activity_reg[ self.job_no ].insert( 3, begin ) # epoch time stamp
        self.is_job_running = True
        self.job_no+=1

    def interval( self, epoch_list ):
        """
        computes the interval between two epoch timestamps and returns the difference expressed in base 10 hours. Eg. 2 hours 30 minutes == 2.50
        interval expects two epoch timestamps, but in this doctest, we're faking it in order to be able to actually understand the values
        >>> c = timereg( 'txt' )
        >>> c.interval( [ time.mktime((2008, 2, 4, 20, 14, 25, 0, 35, 0)), time.mktime((2008, 2, 4, 22, 44, 25, 0, 35, 0)) ] )
        '2.50'
        >>> c.interval( [ time.mktime((2008, 2, 4, 20, 14, 25, 0, 35, 0)), time.mktime((2008, 2, 4, 20, 35, 25, 0, 35, 0)) ] )
        '0.35'
        >>> c.interval( [ time.mktime((2008, 2, 4, 20, 14, 25, 0, 35, 0)), time.mktime((2008, 2, 4, 20, 44, 25, 0, 35, 0)) ] )
        '0.50'
        >>> c.interval( [ time.mktime((2008, 2, 4, 20, 14, 25, 0, 35, 0)), time.mktime((2008, 2, 5, 22, 14, 25, 0, 36, 0)) ] )
        '26.00'
        >>> c.interval( [ time.mktime((2008, 2, 4, 20, 14, 25, 0, 35, 0)), time.mktime((2008, 2, 4, 20, 17, 25, 0, 35, 0)) ] )
        '0.05'
        """

        if self.debug_mode:
            pdb.set_trace()

        secs = float( time.mktime( time.localtime( epoch_list[1] - epoch_list[0] ) ) )

        #return float hours in base 10
        return '%.2f'%( float( secs / 60 / 60 ) )

    def save_list( self ):

        if not ( self.is_job_running and len(self.activity_reg) > 0 ):
            sys.exit( "no jobs registered, exiting." )

        job_list = ''
        print    'finish the last job'
        if self.is_job_running:
            self.end_job()
        print "activity %s ended at %s"% (str(self.activity_reg[self.job_no-1][0]),str (self.activity_reg[self.job_no-1][2]))
        if not os.path.exists( self.out_file ):
            job_list='# activity code | start time | end time | {duration hours}.{duration minutes} (in base 10)\n'
        total_hours =0
        total_minutes=0
        for job_item in self.activity_reg:
            if self.debug_mode:
                pdb.set_trace()

            try:
                job_list += str(job_item[0])+'|'+str(job_item[1])+'|'+str(job_item[2])+'|'+'%s%s'%( str( self.interval ( [job_item[3], job_item[4] ]) ), os.linesep )
            except IndexError:
                sys.exit( "no activities were registered, exiting." )

        if os.path.exists( self.out_file ):
            print "file %s exists, appending to it" %( self.out_file )
            sfh = open(self.out_file, 'a')
        else:
            sfh = open(self.out_file, 'w')
        sfh.write(job_list)

        print 'saved activities into file', self.out_file
        sfh.close()

    def save_list_tidsreg( self ):
        """saves a list of activities, tidsreg style
        dodging baseball bats
        """
        if self.is_job_running:
            self.end_job()
        job_list = ''
        for job_item in self.activity_reg:
            try:
                job_list += '"%s"  %s # %s-%s%s'%( str( job_item[ 0 ] ), str( self.interval ( [ job_item[ 3 ], job_item[ 4 ] ] ).replace( '.', ':' ) ), job_item[ 1 ].split()[ 1 ], job_item[ 2 ].split()[ 1 ],  os.linesep )
            except IndexError:
                sys.exit( "no activities were registered, exiting." )
        if os.path.exists( self.out_file ):
            sfh = open(self.out_file, 'a')
        else:
            sfh = open(self.out_file, 'w')
        sfh.write(job_list)
        sfh.close()

    def save_list_xml(self):
        print "log: finish the last job"
        if self.is_job_running:
            self.end_job()
        #print "log: activity %s ended at %s"% (str(self.activity_reg[self.job_no-1][0]),str (self.activity_reg[self.job_no-1][2]))
        xml_list = '<?xml version=\'1.0\' encoding=\'utf-8\'?>'
        xml_list += '<job_list items=\'%d\'>'%(len(self.activity_reg))
        total_hours =0
        total_minutes=0
        iterator = 1
        for job_item in self.activity_reg:
            xml_list += '<job number=\'%d\'>'%(iterator)
            xml_list += '<activity_code>%s</activity_code>'%(str(job_item[0]))
            xml_list += '<start_time>%s</start_time>'%(str(job_item[1]))
            xml_list += '<end_time>%s</end_time>'%(str(job_item[2]))
            xml_list += '<duration value=\'hours\'>%s</duration>'%(str(self.interval ( [job_item[3], job_item[4] ]) ) )
            xml_list += '</job>'
            iterator +=1
            #total_hours+=int(self.interval(job_item)[0])
            #total_minutes+=int(self.interval(job_item)[1])

        #xml_list += '<registered_total value=\'hours\'>%s</registered_total>'%(str(total_hours))
        #xml_list += '<registered_total value=\'minutes\'>%s</registered_total>'%(str(total_minutes))
        xml_list += '</job_list>'

        if os.path.exists( self.out_file ):
            print "output file already exists, lazyboy have not yet implemented append, so I make new file for you, cheap."
            xfh = open(self.out_file+str(time.time()), 'w')
        else:
            xfh = open(self.out_file,'w')
        xfh.write(xml_list)
        xfh.close()

        '''
        Saves the list tidsreg-style, for dbc-compatibility ;)
        '''
        #    def save_list_tidsreg(self):

    @staticmethod
    def print_help():
        help_string='''
        Time reg.
        A tool for registering your time.
        Steen Manniche, steen@manniche.net

        usage:

        python timereg.py [-h] [-v] [-o outputformat]

        -h displays this text

        -v run doctests for timereg

        -o specify the outputformat for timereg. avaliable options are:
            txt: pipe separated output format (default)
            tid: tidsreg-compatible output format

        Write your activities and codes for them in activity_list.py or
        get an autogenerated activity_list.py from get_jobs.py
        Press q when finished and your activites with time durations
        are saved to file identified by a timestamp for the current day.
        '''
        print help_string

#the following performs a doctest, if the -v flag is given to the interpreter
def _test():
    import doctest
    doctest.testmod()


if __name__=='__main__':

    from optparse import OptionParser

    if len(sys.argv) == 2 and sys.argv[1] == '-v':
        print "running tests"
        _test()
        sys.exit(0)

    elif len(sys.argv) == 3 and sys.argv[1] == '-o':
        if sys.argv[2] == 'txt' or sys.argv[2] == 'tid':
            output = sys.argv[2]
        else:
            Timereg.print_help()
            sys.exit("outputformat %s not supported"%( sys.argv[2] ) )

        c = Timereg( output )

    elif len(sys.argv) > 1:
        Timereg.print_help()
        sys.exit( "%s : no such argument, try doctest suite with -v. timereg is run without arguments."%(sys.argv[1:]) )

    else:
        # no arguments passed, assuming default
        c = Timereg( 'txt' )

    c.main()
