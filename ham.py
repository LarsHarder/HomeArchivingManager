#!/bin/python

# ham.py
#
# HomeArchivingManager
#
# Move files to an archiving-location and create symlinks from original location.
# Allows to archive Files to CD/DVD/BluRay, keep the files available from
# original location, while reducing the size for a backup of the files
# at the original location. (Think of a differential Backup...)
#
# Lars Harder
# started:      20160710
# last edited:  20160711


import os
import sys
import shutil

SECTORSIZE = 2048           # size of a sector on a CD/DVD/BluRay for
                            # calculating used filesize
CDSIZE = 700000000          # size of a CD in bytes
DVDSIZE = 4700000000        # size of a DVD in bytes
BLUERAYSIZE = 25000000000   # size of a BluRay in bytes

CONFIGFILE = '.ham'         # Name of config-file for ham in $home
LISTFILE = '.hamlist'       # Name of list-file for ham in $home


pathToArchive = ''          # Where to store the archived files
                            # (read from CONFIGFILE)
home = ''                   # $home directory

def testForPosix():
    if os.name != 'posix':
        print "ham only works with a posix-compatible operating system"
        sys.exit(2)
    else:
        return

def printHelp():
    print 'Help Message for ham.py'
    print ' prepare <cd / dvd / bd>      create new archiveset'
    print ' add <files>                  add files to archiveset'
    print ' adddir <directories>         add files from directory and subdirectories to archiveset'
    print ' create                       move files and set symlinks'
    print ' discard                      delete new archiveset without changing any files'
    print ' --help                       this message'

def readConfigFile():
    home =  os.environ.get('HOME')
    if home == None:
        print 'Environment Variable "HOME" not set'
        sys.exit(3)
    try:
        configFile = open(home + '/' + CONFIGFILE,'r')
    except IOError:
        print 'No config-file found in $home'
        sys.exit(4)
    try:
        config = configFile.read()
    except IOError:
        print 'config-file empty'
        sys.exit(5)
    parameters = config.split()
    if parameters.__len__() == 3:
        if (parameters[0].lower() != 'archive') or (parameters[1] != '='):
            print 'error in config-file'
            sys.exit(6)
        pathToArchive = parameters[2]
    else:
        print 'error in config-file'
        sys.exit(7)
    if not os.path.isdir(pathToArchive):
        print 'directory for Archive does not exist: ' + pathToArchive
        sys.exit(8)
    return home, pathToArchive

def sizeOfFiles():
    try:
        listFile = open(home + '/' + LISTFILE, 'r')
    except IOError:
        print 'error opening listfile for creating'
        sys.exit(16)
    try:
        maxSizeOfArchive = int(listFile.readline())
    except:
        print 'error reading listfile 1'
        sys.exit(17)
    listOfFilesToArchive = []
    for fileToArchive in listFile:
        listOfFilesToArchive.append(fileToArchive[:-1]) # read and remove newline
    setOfFilesToArchive = set(listOfFilesToArchive)

    # check for duplicates
    if len(setOfFilesToArchive) < len(listOfFilesToArchive):
        print 'Discarding ' + str(len(listOfFilesToArchive)-len(setOfFilesToArchive)) + ' duplicate entries'
        listOfFilesToArchive = list(setOfFilesToArchive)

    # calculate size of files
    size = 0
    for fileToArchive in listOfFilesToArchive:
        fileSize = os.path.getsize(fileToArchive)
        fileSizeOnDisk = round((fileSize / SECTORSIZE) + 0.5) * SECTORSIZE
        size = size + fileSizeOnDisk
    return size, listOfFilesToArchive, maxSizeOfArchive

def prepare(sizeOfArchive):
    if os.path.isfile (home + '/' + LISTFILE):
        print 'listfile present - DISCARD, ADD or CREATE'
        sys.exit(9)
    try:
        listFile = open(home + '/' + LISTFILE, 'w')
    except IOError:
        print 'could not create List File'
        sys.exit(10)
    print 'Create new Archive for size of ' + sizeOfArchive.__str__()
    listFile.write(sizeOfArchive.__str__() + '\n')
    listFile.close()
    sys.exit(0)


def add(filesToAdd):
    if not os.path.isfile (home + '/' + LISTFILE):
        print 'listfile not present - PREPARE'
        sys.exit(11)
    filesWithFullPath = []
    for newFile in filesToAdd:
        if os.path.isfile(os.getcwd() + '/' + newFile):
            filesWithFullPath.append(os.getcwd() + '/' + newFile)
        else:
            print newFile + ' is not a file'
            sys.exit(12)
    try:
        listFile = open(home + '/' + LISTFILE, 'a')
    except IOError:
        print 'could not open listfile for appending'
        sys.exit(13)
    for newFile in filesWithFullPath:
        listFile.write(newFile + '\n')
    listFile.close()
    print 'added ' + str(filesToAdd.__len__()) + ' files'
    size, listOfFiles, maxSizeOfArchive = sizeOfFiles()
    print 'archive uses ' + str(size) + ' of ' + str(maxSizeOfArchive)
    sys.exit(0)
    return

def addDirectory(paths):
    if not os.path.isfile (home + '/' + LISTFILE):
        print 'listfile not present - PREPARE'
        sys.exit(23)
    filesWithFullPath = []
    for newPath in paths:
        print "newPath: " + os.getcwd() + '/' + newPath
        if not os.path.isdir(os.getcwd() + '/' + newPath):
            print newPath + ' is not a directory'
            sys.exit(25)
    try:
        listFile = open(home + '/' + LISTFILE, 'a')
    except IOError:
        print 'could not open listfile for appending'
        sys.exit(24)

    for path in paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for aFile in filenames:
                    #print 'adding      : cwd:' + os.getcwd() + ' dirpath:' + dirpath + ' file: ' + aFile
                    if dirpath [-1:] == '/':
                        filesWithFullPath.append(os.getcwd() + '/' + dirpath +  aFile)
                    else:
                        filesWithFullPath.append(os.getcwd() + '/' + dirpath + '/' + aFile)

    for newFile in filesWithFullPath:
        print 'add file ' + newFile
        listFile.write(newFile + '\n')
    listFile.close()
    print 'added files'
    size, listOfFiles, maxSizeOfArchive = sizeOfFiles()
    print 'archive uses ' + str(size) + ' of ' + str(maxSizeOfArchive)
    sys.exit(0)
    return

def getLatestArchive():
    directories = []
    for (dirpath, dirnames, filenames) in os.walk(pathToArchive):
        directories.extend(dirnames)
        break
    directoryNumbers = []

    # if Archive empty return 0 archives
    if len(dirnames) == 0:
        return 0
    try:
        for directoryName in directories:
            nr = int(directoryName)
            directoryNumbers.append(nr)
    except ValueError:
        print 'Archive contains directories that are not numerical'
        sys.exit()
    directoryNumbers.sort()
    return int(directoryNumbers[-1])

def deleteListfile():
    try:
        os.remove (home + '/' + LISTFILE)
    except IOError:
        print 'Error deleting listfile'
        sys.exit(15)

def moveListfileToArchive(archiveNumber):
    try:
        shutil.move(home + '/' + LISTFILE, pathToArchive  + str(archiveNumber) + '/' + LISTFILE)
    except IOError:
        print 'listfile could not be moved to archive'
        sys.exit(22)

def createFolder(targetPath):
    # if path exists, return
    if os.path.isdir(targetPath):
        return

    # find parent directory
    indexOfLastSlash = targetPath.rfind('/')
    leftPath = targetPath[0:indexOfLastSlash]
    rightPath = targetPath[indexOfLastSlash + 1:]

    # create it
    createFolder(leftPath)

    # finally create last directory in targetPath
    try:
        os.mkdir(targetPath + '/')
    except OSError:
        print 'could not create new directory: ' + targetPath
        sys.exit(21)

def moveFile(source, targetDirectory):
    # find path of source
    indexOfLastSlash = source.rfind('/')
    sourcePath = source[0:indexOfLastSlash]

    createFolder(targetDirectory + sourcePath)
    os.rename(source, targetDirectory +  source)
    return

def symlinkFile(source, targetDirectory):
    os.symlink(targetDirectory + source, source)
    return

def create():
    size, listOfFilesToArchive, maxSizeOfArchive = sizeOfFiles()

    if size > maxSizeOfArchive:
        print 'size of files is larger than size of Archive - delete manually or DISCARD'
        sys.exit(18)

    latestArchive = getLatestArchive()
    currentArchive = latestArchive + 1

    # create new Archive-Directory
    try:
        os.mkdir(pathToArchive + str(currentArchive) + '/')
    except OSError:
        print 'could not create new directory for archive'
        sys.exit(20)

    # move files and set symlinks
    # move first, bacause moving a file then symlinking leads to
    # OSError: [Errno 16] Device or resource busy
    for fileToArchive in listOfFilesToArchive:
        moveFile(fileToArchive, pathToArchive + str(currentArchive))

    for fileToArchive in listOfFilesToArchive:
        symlinkFile(fileToArchive, pathToArchive + str(currentArchive))

    moveListfileToArchive(currentArchive)
    return

def discard():
    if not os.path.isfile (home + '/' + LISTFILE):
        print 'listfile not present - nothing to discard'
        sys.exit(14)
    deleteListfile()
    print 'listfile deleted'
    sys.exit(0)

def parseCommandline():
    commandline = sys.argv
    if 'ham.py' in commandline[0]:
        commandline = commandline[1:]
    if commandline.__len__() == 0:
        printHelp()
        sys.exit(1)
    if commandline[0].lower()=='--help':
        printHelp()
        sys.exit(0)
    if commandline[0].lower()=='prepare':
        if commandline.__len__() == 2 and commandline[1].lower()=='cd':
            prepare(CDSIZE)
            return
        if commandline.__len__() == 2 and commandline[1].lower()=='dvd':
            prepare(DVDSIZE)
            return
        if commandline.__len__() == 2 and commandline[1].lower()=='bd':
            prepare(BLUERAYSIZE)
            return
        printHelp()
        sys.exit(1)
    if commandline[0].lower()=='add':
        if commandline.__len__() == 1:
            printHelp()
            sys.exit(1)
        filesToAdd = commandline[1:]
        add(filesToAdd)
        return
    if commandline[0].lower()=='adddir':
        if commandline.__len__() == 1:
            printHelp()
            sys.exit(1)
        pathsToAdd = commandline[1:]
        addDirectory(pathsToAdd)
    if commandline[0].lower()=='create':
        if commandline.__len__() > 1:
            printHelp()
            sys.exit(1)
        create()
        return
    if commandline[0].lower()=='discard':
        if commandline.__len__() > 1:
            printHelp()
            sys.exit(1)
        discard()
        return
    printHelp()
    sys.exit(1)

testForPosix()
home, pathToArchive = readConfigFile()
parseCommandline()
