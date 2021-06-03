"""
Unspecific helper classes

@author: Martin Kuemmel, Jonas Haase
@organization: Space Telescope - European Coordinating Facility (ST-ECF)
@license: Gnu Public Licence
@contact: mkuemmel@eso.org
@since: 2005/09/13

$LastChangedBy: mkuemmel $
$LastChangedDate: 2008-07-03 10:27:47 +0200 (Thu, 03 Jul 2008) $
$HeadURL: http://astropy.scipy.org/svn/astrolib/trunk/asciidata/Lib/asciiutils.py $
"""
__version__ = "Version 1.0 $LastChangedRevision: 503 $"


class Separator(object):
    """
    Class to separate an ascii line into items

    Instance of this class split an ascii line into
    the different items. The methods on how to split
    a line work with a delimiter, or according to
    whitespace or according to a fixed format given
    in a file (not yet implemented.
    """
    def __init__(self, delimiter=None, file=None):
        """
        The class constructor
        """
        self._delimiter = delimiter
        self._file      = file

    def separate(self, line):
        """
        Separates a line into its items

        @param line: the ascii line to be separated
        @type line: string

        @return: the list of items
        @rtype: [string]
        """
        # delete the trailing newline
        if line[-1] == '\n':
            line = line[:len(line)-1]

        # separate either along a delimiter
        if self._delimiter != None:
            items = self.separate_delim(line)
        # or along whitespaces
        else:
            items = self.separate_white(line)

        return items

    def separate_white(self, line):
        """
        Separates a line along the whitespace

        The method transforms a line into the list
        of its space-separated items. The first space
        is the delimiter, any further spaces are interpreted
        to belong to the item and are preserved.
        This is advantageous to keep the item length for
        string columns with leading spaces.

        @param line: the ascii line to be separated
        @type line: string

        @return: the list of items
        @rtype: [string]
        """
        # create the item list
        witems = []

        # split it conventionally
        items = line.strip().split()

        # go again over the line and identify
        # the exact starting position of each
        # item, preserving the leading spaces
        start=0
        for item in items:
            pos = line.find(item,start)
            if pos > -1:
                witems.append(line[start:pos+len(item)])
                start = pos+len(item)+1

        # return the list
        return witems

    def separate_delim(self, line):
        """
        Separates a line along a delimiter

        The method transforms a line into the list
        of its delimiter separated items.

        @param line: the ascii line to be separated
        @type line: string

        @return: the list of items
        @rtype: [string]
        """
        # split the line
        items = line.split(self._delimiter)

        # return the list
        return items


class AsciiLenGetIter(object):
    """
    A general purpose iteratorfor any class with len() and get[]
    """
    def __init__(self, len_get_object):
        """
        The class constructor
        """
        # store the associated AsciiData object
        self._len_get_object = len_get_object

        # set the index of the actual column
        self._index = -1

        # set the maximum column index
        self._max_index = len(self._len_get_object) - 1

    def __iter__(self):
        """
        Mandatory method for an iterator class
        """
        return self

    def __next__(self):
        """
        Mandatory method for an iterator class

        The method gives the next object in the iterator sequence.
        In case that a next object does no longer exist,
        a corresponding exception is thrown to indicate
        the end of the iterator sequence.
        """
        # check whether the next iteration does exist
        if self._index >= self._max_index:
            # no next iteration, raise exception
            raise StopIteration

        # enhance the actual index
        self._index += 1

        # return the next iteration
        return self._len_get_object[self._index]
