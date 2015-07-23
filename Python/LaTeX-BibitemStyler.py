###################################################################
## LaTeX-BibitemsStyler
##
## Sílvia "PchiwaN" Mur Blanch
## silvia.murblanch at gmail.com
##
## Andreea Georgescu
## andreea.i.georgescu at gmail.com
###################################################################

###################################################################
# Version 2.0 - Revised by suggestion of Olli Nummi
###################################################################
# replace '~\cite' by '\cite' in the search for cites
# use '\include' as well as '\input' to search for tex files
# search for cites in the main tex file too
# handle multiple keys inside single citation
###################################################################

###################################################################
# Version 3.0 - Python 3
###################################################################
# handles duplicate bibitems
###################################################################


from __future__ import print_function
from collections import namedtuple, OrderedDict
import os

bibstyles = namedtuple('bibstyles', ['PLAIN', 'ALPHA', 'UNSRT'])
bibstyles.__new__.__defaults__ = tuple([False] * len(bibstyles._fields))


class Styler:
    def __init__(self):
        self.filePath = ''
        self.mainTexFile = ''
        self.bibFilename = ''
        self.outputBibFile = ''
        self.preamble = '\\begin{thebibliography}{100}'
        self.postamble = '\\end{thebibliography}\n\n%%%%% CLEAR DOUBLE PAGE!\n\\newpage{\\pagestyle{empty}\\cleardoublepage}'
        self.aTexFiles = []
        self.aCites = []
        self.dBibitems = OrderedDict()

    def GetInputFiles(self):
        '''Read main tex file and get the content of all \input tags
        '''
        print('... getting input files')
        try:
            f = open(self.mainTexFile, 'r')
            s = f.read()  # read file to end
            # move parsing cursos to beginning of document
            s = s[s.find('\\begin{document}')+len('\\begin{document}'):len(s)]
            # parse the file looking for \input or \include commands
            while len(s) > 0:
                if s.find('\\input{') == -1 and s.find('\\include{') == -1:
                    break
                else:
                    if s.find('\\input{') != -1 and s.find('\\include{') != -1:  # there are both commands
                        if s.find('\\input{') < s.find('\\include{'):  # \input command comes before \include command
                            s = s[s.find('\\input{')+len('\\input{'):len(s)]
                        else:
                            s = s[s.find('\\include{')+len('\\include{'):len(s)]
                    else:
                        if s.find('\\input{') != -1:
                            s = s[s.find('\\input{')+len('\\input{'):len(s)]
                        else:
                            s = s[s.find('\\include{')+len('\\include{'):len(s)]

                    # get file name from command
                    texFile = s[0:s.find('}')]
                    print('\t\t', texFile)
                    if texFile != self.bibFilename:
                        self.aTexFiles.append(texFile)
                    # move parsing cursor past the current \input command
                    s = s[s.find('}'):len(s)]
            f.close()
        except:
            print('An error occurred while reading', self.mainTexFile)
            raise

    def GetFilePath(self):
        '''Extract main file path from main tex file
        '''
        print('... getting file path')
        self.filePath = self.mainTexFile[0:self.mainTexFile.rfind('\\') + 1]

    def GetMainTexFileCites(self):
        '''Search for cites in the project's main tex file
        '''
        print('... getting main tex file cites')
        try:
            f = open(self.filePath + self.mainTexFile, 'r')
            s = f.read()  # read file to end
            # parse current file looking for \cite commands, and store all cite keys in an array in their order of appearance
            while s.find('\\cite{') != -1:
                s = s[s.find('\\cite{')+len('\\cite{'):len(s)]
                temp = s[0:s.find('}')]
                # handle multiple keys inside single citation
                cites = temp.split(',')
                for c in cites:
                    cite = c.strip()  # clear leading and trailing whitespaces
                    try:
                        self.aCites.index(cite)  # check if the cite key is already there, to avoid duplicating keys
                    except:
                        self.aCites.append(cite)
            f.close()
        except:
            print('An error occurred while reading main .tex file')
            raise

    def GetTexFileCites(self):
        '''Read all the project's tex files and get the contents of all \cite tags,
        with no repetition
        '''
        print('... getting tex files cites')
        try:
            for texFile in self.aTexFiles:
                f = open(self.filePath + texFile, 'r')
                s = f.read()  # read file to end
                # parse current file looking for \cite commands, and store all cite keys in an array in their order of appearance
                while s.find('\\cite{') != -1:
                    s = s[s.find('\\cite{')+len('\\cite{'):len(s)]
                    temp = s[0:s.find('}')]
                    # handle multiple keys inside single citation
                    cites = temp.split(',')
                    for c in cites:
                        cite = c.strip()  # clear leading and trailing whitespaces
                        try:
                            self.aCites.index(cite)  # check if the cite key is already there, to avoid duplicating keys
                        except:
                            self.aCites.append(cite)
                f.close()
        except:
            print('An error occurred while reading input .tex file')
            raise

    def GetBibitems(self):
        '''Read bibliography files and get all \bibitems
        '''
        print('... getting \\bibitems')
        try:
            with open(self.filePath + self.bibFilename, 'br') as f:
                binary = f.read()  # read to end
                s = binary.decode('latin-1')
            # parse bibliography file and store bibitems in a dictionary
            while s.find('\\bibitem') != -1:
                s = s[s.find('\\bibitem')+len('\\bibitem'):len(s)]
                if s.find('\\bibitem') != -1:  # this is any \bibitem
                    bibitem = s[0:s.find('\\bibitem')]
                else:  # this is the last \bibitem of the bibliography file
                    bibitem = s[0:s.find('\\end{')]
                key = bibitem[1:bibitem.find('}')]  # get \bibitem key
                bibitem = bibitem.replace('{' + key + '}', '')  # remove key from the \bibitem entry
                bibitem = bibitem.strip()
                bibitem = bibitem.rstrip('\n\t')  # remove trailing characters from the \bibitem entry
                self.dBibitems[key] = bibitem  # we store the \bibitem in a dictionary; we'll access the entry by its key
            f.close()
        except:
            print('An error has ocurred while parsing the bibliography file,',
                  self.bibFilename)
            raise

    def WriteBibFile(self):
        '''Write output bibliography tex file, according to the specified sorting method
        '''
        print('... writing bibliography file')
        try:
            f = open(self.filePath + self.outputBibFile, 'w')
            # write bibliography file preamble
            print('\t\twriting preamble')
            f.write(self.preamble + '\n\n')
            # write bibliography according to the chosen style
            if self.bibStyle.PLAIN:  # same \bibitem order as the original bibliography file, but with specified preamble and postamble
                print('\t\twriting \\bibitems PLAIN style')
                for key in self.dBibitems:
                    f.write('\t\\bibitem{'+ key +'} '+ self.dBibitems[key] +'\n\n')

            elif self.bibStyle.ALPHA:  # \bibitem entry alphabetical order
                print('\t\twriting \\bibitems ALPHA style')
                for key in sorted(self.dBibitems, key=self.dBibitems.get):
                    f.write('\t\\bibitem{'+ key +'} '+ self.dBibitems[key] +'\n\n')

            elif self.bibStyle.UNSRT:  # \bibitem key order of appearance in the latex project files
                print('\t\twriting \\bibitems UNSRT style')
                for key in self.aCites:
                    f.write('\t\\bibitem{' + key + '} ' + self.dBibitems[key] + '\n\n')
                    del self.dBibitems[key]  # remove the \bibitem that we just wrote from the \bibitems array
                # at this point, the \bibitems that were cited in the latex project files have been written in the output file
                # we know proceed to write the \bibitems that were not cited in the latex project, in the same order they were read
                for key in self.dBibitems:
                    f.write('\t\\bibitem{' + key +'} '+ self.dBibitems[key] +'\n\n')
            print('\t\twriting postamble')
            f.write('\n' + self.postamble)
        except:
            print('An error has ocurred while writing the output bibliography file,',
                  self.outputBibFile)
            raise
        else:
            f.close()
            print('\nBibliography file', self.outputBibFile,
                  'has been successfully created!\n')

################### MAIN LOOP


styler = Styler()

print('\n\n')
print('########################################################')
print('######### LaTeX-BibitemsStyler by Pchiwan 2009 #########')
print('########################################################\n\n')

print('+ Enter main Tex file path (use double \'\\\')\n')
styler.mainTexFile = input()
if os.path.exists(styler.mainTexFile):

    print('\n+ Enter bibliography Tex file name\n')
    styler.bibFilename = input()

    print('\n+ Enter output bibliography Tex file name\n')
    styler.outputBibFile = input()

    print('\n+ This is the default bibliography preamble\n\n', styler.preamble)
    print('\n\n+ Do you want to change it? (y/n)')
    if input() == 'y':
        print('\n+ Enter preamble (type \'\\q\' to submit)\n')
        k = ''
        styler.preamble = ''
        while k != '\q':
            k = input()
            if k != '\q':
                styler.preamble += k

    print('\n+ This is the default bibliography postamble\n\n', styler.postamble)
    print('\n\n+ Do you want to change it? (y/n)')
    if input() == 'y':
        print('\n+ Enter postamble (type \'\\q\' to submit)\n')
        k = ''
        styler.postamble = ''
        while k != '\q':
            k = input()
            if k != '\q':
                styler.postamble += k

    print('\n+ Select a bibliography style\n')
    print('0 - PLAIN')
    print('1 - ALPHA (Alphanumerical order)')
    print('2 - UNSRT (Cite order of appearance)')
    inp = int(input())
    styler.bibStyle = bibstyles(**{bibstyles._fields[inp]: True})
    print('\n\n')

    styler.GetInputFiles()
    styler.GetFilePath()
    styler.GetMainTexFileCites()
    styler.GetTexFileCites()
    styler.GetBibitems()
    styler.WriteBibFile()
else:
    print('Please enter a valid main Tex file path')
