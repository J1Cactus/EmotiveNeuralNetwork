import os
import csv
import shutil
import numpy as np


#BUILD A TXT FILE WITH ALL THE USEFULL DATA: <audioFileName>;<emo>;<transcriptionText>
def clusterData(Data_path, Out_file_path):
    #GET ALL THE SESSIONS DIRECTORY NAME FROM MAIN ROOT
    dirlist = [ item for item in os.listdir(Data_path) if os.path.isdir(os.path.join(Data_path, item))]
    print('All Sessions',dirlist)
    
    #CREATE OUTPUT DATA FILE: remove if it already exist and recreate it new
    try:
        os.remove(Out_file_path)
    except OSError:
        pass
    outputfile = open(Out_file_path, 'a')
    
    #The output file is placed in the root folder and the content will have the format: AudioFileName, CatOutput, ValOutput.
    for session in dirlist:
        print('Parsing: ',session)
        
        #COMPOSE DIRECTORY PATH FOR THE EMOTION RESULTS FILE FOR THE CURRENT SESSION
        directoryEmoPath = os.path.normpath(os.path.join(Data_path, session)+'\EmoEvaluation')
        emolist = [ item for item in os.listdir(directoryEmoPath) if os.path.isfile(os.path.join(directoryEmoPath, item)) ]
        print('Directory Emotion: ',directoryEmoPath)
        
        #COMPOSE DIRECTORY PATH FOR THE SENTENCE TRANSCRIPTION FILE FOR THE CURRENT SESSION
        directoryText = os.path.normpath(os.path.join(Data_path, session)+'\Transcriptions')
        translist = [ item for item in os.listdir(directoryText) if os.path.isfile(os.path.join(directoryText, item)) ]
        print('Directory Transcription: ',directoryText)
        
        #PARSE ALL THE FILES AND APPEND IN THE OUTPUT FILE
        for file in emolist:
            with open(os.path.join(directoryEmoPath, file), 'r') as inputfile:
                for lines in inputfile:
                    lines = lines.strip()
                    pos = lines.find('Ses')
                    if pos != -1:
                        #CREATE NEW LINE FOR EMOTION RESULTS
                        audioName = lines.split()[3]
                        emoLabel = lines.split()[4]
                        '''parselines = lines.split()[3]+';'+lines.split()[4]+';'+lines.split()[5]+lines.split()[6]+lines.split()[7]'''
                        #FOR EACH LINE FIND THE CORRESPONDING TRANSCRIPTION SENTENCE IN THE TRANSCRIPTION FILE
                        for file2 in translist:
                            if file2 == file:
                                with open(os.path.join(directoryText, file2), 'r') as inputfile2:
                                    for lines2 in inputfile2:
                                        if lines2.split(' ')[0] == audioName:
                                            transcription = lines2.split(':')[1]
                                            transcription = transcription.split('\n')[0]
                                            transcription = transcription.split(" ", 1)[1]
                                            break
                        
                        #APPEND IN THE OUTPUT FILE                    
                        outputfile.writelines(audioName+';'+emoLabel+';'+transcription+'\n')
            inputfile.close()
    outputfile.close()  

#MOVE ALL THE AUDIO FILES IN THE MAINROOT IN 1 DIRECTORY    
def moveCopyAudioFiles(mainRoot, destPath):
    print('****Start of method moveAudioFiles')
    
    #SET DESTINATION PATH
    print('DestPath: ',destPath)
    
    #GET ALL THE SESSIONS DIRECTORY NAME FROM MAIN ROOT
    sessDirList = [ item for item in os.listdir(mainRoot) if os.path.isdir(os.path.join(mainRoot, item)) and item[0] == 'S']
    print('All Sessions',sessDirList)
    
    for session in sessDirList:
        currentAudioDirPath = os.path.normpath(os.path.join(mainRoot, session)+'\Sentences_audio')
        audioGroupDir = [ item for item in os.listdir(currentAudioDirPath) if os.path.isdir(os.path.join(currentAudioDirPath, item)) ]

        print('Inside: ',session)
        
        for audioGroup in audioGroupDir:
            currentAudioGroupPath = os.path.normpath(os.path.join(currentAudioDirPath, audioGroup))
            audlist = [ item for item in os.listdir(currentAudioGroupPath) if os.path.isfile(os.path.join(currentAudioGroupPath, item)) ]
            print('Inside audioGroup: ',audioGroup)
               
            for Afile in audlist:
                print('Moving file: ',Afile)
                audioFilePath = os.path.join(currentAudioGroupPath, Afile)
                shutil.copy(audioFilePath, destPath)
                #shutil.move(audioFilePath, destPath)
                
    print('****End of method moveAudioFiles')   

    
if __name__ == '__main__':
    
    #SET MAIN ROOT
    #main_root = os.path.normpath(r'D:\DATA\POLIMI\----TESI-----\NewCorpus')
    #main_root = os.path.normpath(r'C:\Users\JORIGGI00\Documents\MyDOCs\Corpus_Test_Training')
    main_root = os.path.normpath(r'D:\DATA\POLIMI\----TESI-----\Corpus_Training')
    #main_root = os.path.normpath(r'C:\Users\JORIGGI00\Documents\MyDOCs\Corpus_Usefull')
    
    #SET PATH
    ZData_path = os.path.join(main_root + '\ZData')
    out_file_path =  os.path.join(main_root+'\AllData.txt') 
    audio_file_dest_path = os.path.normpath(main_root+'\AllAudioFiles')  
    
    clusterData(ZData_path, out_file_path)  
    moveCopyAudioFiles(ZData_path, audio_file_dest_path)    
        
    print('END') 
        
        
        
        
        
        