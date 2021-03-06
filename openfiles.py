import argparse
from asyncio.windows_events import NULL
from distutils.log import ERROR, error
import json
import os
import re
import subprocess

# Paradox File Comparer, doesnt compare files though
# Just finds the desired files to pull into VS Code
# Version 1: Working User Interface

userIOtxt = [ # user IO text
    'FileComparer: >>> Press CTRL + C to abort',
    'FileComparer: >>> Do you want to open your Files in your current Instance of VS Code?',
    'FileComparer: >>> Type [y/Yes] or [n/No]',
    'FileComparer: >>> Enter your desired File, please:',
    'FileComparer: >>> Please Confirm your Choices:',
    'FileComparer: >>>   selected File:   %s',
    'FileComparer: >>>    VS Code Mode:   %s',

    'FileComparer: <<< ',
    'FileComparer: >>> '
]


def homeDir():
    var1 = os.environ['HOMEDRIVE']
    temp = os.environ['HOMEPATH']
    var2 = re.sub(r'(Users\\)(\w+)', r'\1\\\2', temp)
    out = var1 + '\\' + var2
    return(out)  # returns the home directory of the current user, for example C:\\Users\\John Doe\\


# pulls a string with all files that you are searching from findvalidfiles.bat
# catches the errors it would produce when supplied with invalid input
def pullFiles(var):
    out = subprocess.check_output(
        ['findvalidfiles.bat ', var], universal_newlines=True)
    return out

# regex split a string along a specific pattern


def regexSplit(pattern, string):
    delim = '<-split->'
    out = r''
    out = re.sub(pattern, delim, string).split(delim)
    return out


def clear(): return os.system('cls')


def main():

    # declare important variables
    fileString = ''
    stringOut = r''
    userYN = r''
    lIVScode = False
    modeVSC = ''
    endIOLoop = False

    # User Interface loop
    clear()
    while not endIOLoop:
        # ask if user wants to open files in current VS Code instance or in a new one
        while 1:
            # Loop Start
            print(
                userIOtxt[0],  # [0]: Cancel Hint
                userIOtxt[1],  # [1]: VS Code Current Instance Question
                userIOtxt[2],  # [2]: Confirm Hint
                sep='\n'      # newline seperator
            )
            userYN = input(
                userIOtxt[7]  # [7]: User Input Text
            )
            if re.search(r'yes|YES|Yes|y|Y', userYN):
                lIVScode = True
                clear()
                break
            elif re.search(r'no|NO|No|n|N', userYN):
                lIVScode = False
                clear()
                break
            else:
                print('\a')
                clear()
                continue
            # Loop End

        if lIVScode:
            modeVSC = 'open new Instance'
        elif not lIVScode:
            modeVSC = 'open in current Instance'
        else:
            raise error('lIVScode has a problem!')

        # get the user file
        print(
            userIOtxt[0],  # [0]: Cancel Text
            userIOtxt[3],  # [3]: Desired File Text
            sep='\n'      # newline seperator
        )
        userInput = input(
            userIOtxt[7]  # [7]: User Input Text
        )

        clear()

        print(
            userIOtxt[0],  # [0]: Cancel Text
            userIOtxt[4],  # [4]: Confirm Choices
            userIOtxt[5] % userInput,  # [5]: display Desired File
            userIOtxt[6] % modeVSC,  # [6]: display VS Code Mode
            sep='\n'      # newline seperator
        )
        userYN = input(
            userIOtxt[7]  # [7]: User Input Text
        )
        while 1:
            if re.search(r'yes|YES|Yes|y|Y', userYN):
                endIOLoop = True
                clear()
                break

            elif re.search(r'no|NO|No|n|N', userYN):
                endIOLoop = False
                clear()
                break
            else:
                print('\a')
                clear()
                continue

    # pull neccessary data from respective sources: JSON file at local game data directory

    # pull json
    jsonTarget = homeDir()+'\Documents\\Paradox Interactive\\Crusader Kings III\\dlc_load.json'
    with open(jsonTarget) as f:
        dlc_load = json.load(f)

    # find the location of the local VS Code installation
    # for i in re.sub(r'(?<==|;)(?=[A-Z])', delim, os.environ['PATH']).split(delim):
    for i in regexSplit(r'(?<==|;)(?=[A-Z])', os.environ['PATH']):
        if re.search(r'(?:(?=[A-Z]:)(.*)(\\Microsoft VS Code\\bin))', i):
            exeLoc = i
            break
    # construct the complete path
    exeLoc = os.path.join(exeLoc, 'code.cmd')

    # pull target files string, format it correctly to process later
    findValidFilesResults = regexSplit(r'\s(?=[A-Z]:\\)', pullFiles(userInput))

    #################################################
    ####### mainpart: compare the two strings #######
    #################################################

    # iterater over the string
    for obj in findValidFilesResults:
        # find the numbers in the Directory String passed by findvalidfiles.bat
        matchString = re.search(r'(\\1158310\\)(?P<out>\d*)(\\)', obj)
        if matchString:
            # save all results here, to compare them later
            stringOut = matchString.group('out')

        # iterate through the 'dlc_load.json' file, 'enabled_mods' key, to find all active mods
        for row in dlc_load['enabled_mods']:

            # match every object belonging to the key enabled_mods in the dlc_load.json and save results in matchJson
            matchJson = re.search(r'(/ugc_)(?P<out>\w*)(\.mod)', row)
            if matchJson:

                # Combine matches into fileString
                # if the mod is in the playset, add its path to the final output file
                if stringOut == matchJson.group('out'):
                    fileString = fileString + ' ' + obj

    s = r' '

    tesSTR = regexSplit(r'\s(?=[A-Z]:\\)', fileString)

    for i in tesSTR:
        s = s + r' ' + re.sub(r'(?<=\\)', r'\\', i, re.MULTILINE)

    fileString = regexSplit(r'\s(?=[A-Z]:\\)', s)

    if lIVScode:
        del fileString[0]

    for i in fileString:
        print('Match: '+i)
        subprocess.run([exeLoc, i])

    return 0


if __name__ == '__main__':
    main()
