#!/usr/bin/python

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

def linesToDict( lines ):
    hashDict = {}

    for line in lines:
        line = line.strip()
        tokens = line.split()
        if( len( tokens ) > 1 ):
            hash = tokens[ 0 ]
            if( isMD5Hash( hash ) ):
                # get the rest of the line, starting from the second token
                value = line[ line.find( tokens[ 1 ] ) : ]
                hashDict[ hash ] = value

    return hashDict

def makeEntry( hash, leftFile, rightFile ):
    return { 'hash':hash, 'left':leftFile, 'right':rightFile }

leftFilename = sys.argv[ 1 ]
rightFilename = sys.argv[ 2 ]

# read files

leftFile = open( leftFilename )
leftLines = leftFile.readlines()
leftFile.close()

rightFile = open( rightFilename )
rightLines = rightFile.readlines()
rightFile.close()

# parse left into a dictionary
leftDict = linesToDict( leftLines )
rightDict = linesToDict( rightLines )

matches = []
inLeftNotInRight = []
inRightNotInLeft = []

for hash in leftDict:
    if hash in rightDict:
        matches.append( makeEntry( hash, leftDict[ hash ], rightDict[ hash ] ) )
    else:    
        inLeftNotInRight.append( makeEntry( hash, leftDict[ hash ], 'NOT_FOUND' ) )

for hash in rightDict:
    if not( hash in leftDict ):
        inRightNotInLeft.append( makeEntry( hash, 'NOT_FOUND', rightDict[ hash ] ) )

def compareEntries( e0, e1 ):
    if( e0[ 'left' ] == 'NOT_FOUND' ):
        return cmp( e0[ 'right' ].lower(), e1[ 'right' ].lower() )
    else:
        return cmp( e0[ 'left' ].lower(), e1[ 'left' ].lower() )

matches.sort( compareEntries )
inLeftNotInRight.sort( compareEntries )
inRightNotInLeft.sort( compareEntries )


def formatEntries( entries ):

    if not entries:
        return '', 0

    # find the longest left and right filenames
    longestLeft = max( [ len( e[ 'left' ] ) for e in entries ] )
    longestRight = max( [ len( e[ 'right' ] ) for e in entries ] )

    formatted = ''
    lineLength = -1
    i = 0
    for e in entries:
        line = '%4d | %s | %s | %s\n' % ( i, e[ 'hash' ], e[ 'left' ].ljust( longestLeft ), e[ 'right' ].ljust( longestRight ) )
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
