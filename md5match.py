#!/usr/bin/python

import itertools
import string
import sys

if( len( sys.argv ) ) < 3:
    print( 'Usage: %s left right\nwhere left and right are md5 filenames' % sys.argv[ 0 ] )
    sys.exit( 1 )


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

def makeEntry( hash, leftFiles, rightFiles ):
    return { 'hash':hash, 'left':leftFiles, 'right':rightFiles }

leftFilename = sys.argv[ 1 ]
rightFilename = sys.argv[ 2 ]

# read files into memory
leftFile = open( leftFilename )
leftLines = leftFile.readlines()
leftFile.close()

rightFile = open( rightFilename )
rightLines = rightFile.readlines()
rightFile.close()

# parse both files into separate dictionaries
leftDict = linesToDict( leftLines )
rightDict = linesToDict( rightLines )

# for each hash, sort the list
for h in leftDict:
	leftDict[ h ].sort()

for h in rightDict:
	rightDict[ h ].sort()

# create 3 lists:
# matches, in-left-not-in-right, and in-right-not-inleft
matches = []
inLeftNotInRight = []
inRightNotInLeft = []

for hash in leftDict:
    if hash in rightDict:
        matches.append( makeEntry( hash, leftDict[ hash ], rightDict[ hash ] ) )
    else:    
        inLeftNotInRight.append( makeEntry( hash, leftDict[ hash ], [] ) )

# this operation is asymmetric since
# if it's in both, it would be picked up by the match step above
for hash in rightDict:
    if not( hash in leftDict ):
        inRightNotInLeft.append( makeEntry( hash, [], rightDict[ hash ] ) )

# compare two entries of matching hashes for sorting
def compareEntries( e0, e1 ):
    
    # if e0 has nothing on the left
    # then compare the right entries
    if( e0[ 'left' ] == [] ):
        e0RightStr = string.join( e0[ 'right' ] ).lower()
        e1RightStr = string.join( e1[ 'right' ] ).lower()
        return cmp( e0RightStr, e1RightStr )
    else:
        e0LeftStr = string.join( e0[ 'left' ] ).lower()
        e1LeftStr = string.join( e1[ 'left' ] ).lower()
        return cmp( e0LeftStr, e1LeftStr )

matches.sort( compareEntries )
inLeftNotInRight.sort( compareEntries )
inRightNotInLeft.sort( compareEntries )


def formatEntries( entries ):

    if not entries:
        return '', 0

    # find the longest left and right filenames
    
    # list of lists:
    # [ ['ab', 'cde', 'f'], ['ghij', 'kl'] ]
    leftFilenames = [ e[ 'left' ] for e in entries ]
    rightFilenames = [ e[ 'right' ] for e in entries ]
    
    # unwrap the list of lists into a single list
    leftFilenames = list( itertools.chain( *leftFilenames ) )
    rightFilenames = list( itertools.chain( *rightFilenames ) )
    
    longestLeft = max( [ len( f ) for f in leftFilenames ] )
    longestRight = max( [ len( f ) for f in rightFilenames ] )

    formatted = ''
    lineLength = -1
    i = 0
    for e in entries:
        
        h = e[ 'hash' ]
        spaces = ' ' * len( h )
        leftList = e[ 'left' ]
        nLeft = len( leftList )
        rightList = e[ 'right' ]
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
                if( k < nLeft ):
                    leftStr
                line = '%4d | %s | %s | %s\n' % ( i, h, leftStr.ljust( longestLeft ), rightStr.ljust( longestRight ) )
                isFirst = False
            else:
                line = '%4d | %s | %s | %s\n' % ( i, spaces, leftStr.ljust( longestLeft ), rightStr.ljust( longestRight ) )
        
        if( lineLength < 0 ):
            lineLength = len( line ) - 1

        formatted += line
        i += 1
    return( formatted, lineLength )

( formattedMatches, matchesLength ) = formatEntries( matches )
( formattedLNR, lnrLength ) = formatEntries( inLeftNotInRight )
( formattedRNL, rnlLength ) = formatEntries( inRightNotInLeft )

title = 'Matches'
if( matchesLength < len( title ) ):
    matchesLength = len( title )

print( '=' * matchesLength )
print( 'Matches'.center( matchesLength ) )
print( '=' * matchesLength )
print( formattedMatches )

title = 'In %s, not in %s' % ( leftFilename, rightFilename )
if( lnrLength < len( title ) ):
    lnrLength = len( title )

print( '=' * lnrLength )
print( title )
print( '=' * lnrLength )
print( formattedLNR )

title = 'In %s, not in %s' % ( rightFilename, leftFilename )
if( rnlLength < len( title ) ):
    rnlLength = len( title )

print( '=' * rnlLength )
print( title )
print( '=' * rnlLength )
print( formattedRNL )

# TODO: print summary
# TODO: display duplicates
# print( '%d matches, %d only in left, %d only in right' )