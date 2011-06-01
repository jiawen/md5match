#!/usr/bin/python

import argparse
import collections
import itertools
import string
import sys

def readFileIntoLines( filename ):
    f = open( filename )
    lines = f.readlines()
    f.close()
    return lines

def isMD5Hash( token ):
    token = token.lower()
    if( len( token ) != 32 ):
        return False
    for s in token:
        if( not( s.isdigit() ) ):
            if( not( s.isalpha() ) ):
                return False
            if( s.isalpha() ):
                if( not( s == 'a' or \
                             s == 'b' or \
                             s == 'c' or \
                             s == 'd' or \
                             s == 'e' or \
                             s == 'f' ) ):
                    return False
    return True

# given a list of lines
# each of the form:
# <md5hash> <filename>
# (delimited by whitespace)
# returns a dictionary mapping
# MD5 hashes to lists of filenames
def linesToDict( lines ):
    hashDict = {}

    for line in lines:
        line = line.strip()
        tokens = line.split()
        if( len( tokens ) > 1 ):
            hash = tokens[ 0 ]
            if( isMD5Hash( hash ) ):
                # get the rest of the line, starting from the second token
                filename = line[ line.find( tokens[ 1 ] ) : ]
                if( hash not in hashDict ):
                    hashDict[ hash ] = []
                hashDict[ hash ].append( filename )

    return hashDict

Entry = collections.namedtuple( 'Entry', ['hash', 'left', 'right' ] )

def entryKey( entry ):

    if( entry.left == [] ):
        return entry.right[0]
    elif( entry.right == [] ):
        return entry.left[0]
    else:
        return min( entry.left[0], entry.right[0] )

def makeMatchSets( leftDict, rightDict ):
    # create 3 lists:
    # matches, in-left-not-in-right, and in-right-not-inleft
    matches = []
    inLeftNotInRight = []
    inRightNotInLeft = []

    # walk over all hashes in the left dictionary
    # if it exists in the right dictionary, make an entry in matches
    # otherwise, add it to in-left-not-in-right
    for hash in leftDict:
        if hash in rightDict:
            matches.append( Entry( hash, leftDict[ hash ], rightDict[ hash ] ) )
        else:    
            inLeftNotInRight.append( Entry( hash, leftDict[ hash ], [] ) )

    # walk over all the hashes in the right dictionary
    # test if it's not in the left dictionary and add it to the in-right-not-in-left
    # dictionary
    for hash in rightDict:
        if not( hash in leftDict ):
            inRightNotInLeft.append( Entry( hash, [], rightDict[ hash ] ) )

    return ( matches, inLeftNotInRight, inRightNotInLeft )

def formatEntries( entries ):

    if not entries:
        return '', 0

    # find the longest left and right filenames
    
    # list of lists:
    # [ ['ab', 'cde', 'f'], ['ghij', 'kl'] ]
    leftFilenames = [ e.left for e in entries ]
    rightFilenames = [ e.right for e in entries ]
    
    # unwrap the list of lists into a single list
    leftFilenames = list( itertools.chain( *leftFilenames ) )
    rightFilenames = list( itertools.chain( *rightFilenames ) )

    longestLeft = 0
    if leftFilenames != []:
        longestLeft = max( [ len( f ) for f in leftFilenames ] )

    longestRight = 0
    if rightFilenames != []:
        longestRight = max( [ len( f ) for f in rightFilenames ] )

    formatted = ''
    lineLength = -1
    i = 0

    for e in entries:
        
        h = e.hash
        spaces = ' ' * len( h )
        leftList = e.left
        nLeft = len( leftList )
        rightList = e.right
        nRight = len( rightList )
        isFirst = True
        
        for k in range( max( nLeft, nRight ) ):
            
            leftStr = ' '
            rightStr = ' '
            if( k < nLeft ):
                leftStr = leftList[ k ]

            if( k < nRight ):
                rightStr = rightList[ k ]
            
            if( isFirst ):
                line = '%4d | %s | %s | %s\n' % ( i, h, leftStr.ljust( longestLeft ), rightStr.ljust( longestRight ) )
                isFirst = False
            else:
                line = '%4d | %s | %s | %s\n' % ( i, spaces, leftStr.ljust( longestLeft ), rightStr.ljust( longestRight ) )

            formatted += line

            if( lineLength < 0 ):
                lineLength = len( line ) - 1

        i += 1

    return( formatted, lineLength )


def main( argv = None ):

    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser( description = 'MD5 Matcher' )
    parser.add_argument( 'left' )
    parser.add_argument( 'right' )
    args = parser.parse_args()

    # read files into lines
    leftLines = readFileIntoLines( args.left )
    rightLines = readFileIntoLines( args.right )

    # parse both files into separate dictionaries
    leftDict = linesToDict( leftLines )
    rightDict = linesToDict( rightLines )

    # for each hash, sort the list of files that match the hash
    for h in leftDict:
        leftDict[ h ].sort()

    for h in rightDict:
        rightDict[ h ].sort()

    (matches, lnr, rnl) = makeMatchSets( leftDict, rightDict )
    matches.sort( key = entryKey )
    lnr.sort( key = entryKey )
    rnl.sort( key = entryKey )

    ( formattedMatches, matchesLength ) = formatEntries( matches )
    ( formattedLNR, lnrLength ) = formatEntries( lnr )
    ( formattedRNL, rnlLength ) = formatEntries( rnl )

    title = 'Matches'
    if( matchesLength < len( title ) ):
        matchesLength = len( title )

    print( '=' * matchesLength )
    print( 'Matches'.center( matchesLength ) )
    print( '=' * matchesLength )
    print( formattedMatches )

    title = 'In %s, not in %s' % ( args.left, args.right )
    if( lnrLength < len( title ) ):
        lnrLength = len( title )

    print( '=' * lnrLength )
    print( title )
    print( '=' * lnrLength )
    print( formattedLNR )

    title = 'In %s, not in %s' % ( args.right, args.left )
    if( rnlLength < len( title ) ):
        rnlLength = len( title )

    print( '=' * rnlLength )
    print( title )
    print( '=' * rnlLength )
    print( formattedRNL )

# TODO: print summary
# TODO: display duplicates
# print( '%d matches, %d only in left, %d only in right' )

if __name__ == "__main__":
    sys.exit( main() )
