import numpy as np
import os
import csv
import operator
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Bidirectional
from keras.layers import TimeDistributed
from keras.layers import AveragePooling1D
from keras.layers import Flatten
from keras.layers import Masking
from keras.models import load_model
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD, Adam, RMSprop
import matplotlib.pyplot as plt
from sklearn import svm, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
import itertools
from keras.utils import np_utils
np.seterr(divide='ignore', invalid='ignore')



def plot_confusion_matrix(cm, classes, normalize=False, title='Confusion matrix', cmap=plt.cm):
    
    plt.figure(figsize=(4,7))
    
    #NOT NORMALIZED
    print('Confusion matrix, without normalization')
    print(cm)
    plt.subplot(2, 1, 1)
    plt.imshow(cm, interpolation='nearest', cmap=cmap.Blues)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    
    #NORMALIZED
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    print("Normalized confusion matrix")
    print(cm)
    plt.subplot(2, 1, 2)
    plt.imshow(cm, interpolation='nearest', cmap=cmap.Blues)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    
    return plt


def computeConfMatrix(allPredictionClasses, expected, dirRes, nameFileResult, flagPlotGraph):
    expected = np.argmax(expected, axis=1)
    cm = confusion_matrix(expected, allPredictionClasses)
    plt = plot_confusion_matrix(cm, ['joy','ang','sad','neu'], title=nameFileResult+'-CM')
    
    OutputImgPath = os.path.join(dirRes, nameFileResult+'_CM.png')
    plt.savefig(OutputImgPath)
    if flagPlotGraph:
        plt.show()
    
    
def statistics(Y, yhat, correctCounter, predEmoCounter):
    index, value = max(enumerate(Y[0]), key=operator.itemgetter(1))
    Pindex, Pvalue = max(enumerate(yhat[0]), key=operator.itemgetter(1))
    '''print('index: ', index, 'value: ', value)
    print('index: ', Pindex, 'value: ', Pvalue)'''
    
    #UPDATE CORRECT COUNTER
    if index == Pindex:
        correctCounter[index] += 1
    
    #UPDATE PREDICTED EMO COUNTER
    predEmoCounter[Pindex] += 1
    
    return correctCounter, predEmoCounter


def addEmoCountV2(emoLabel, counter):
    if  emoLabel[0][0] == 1: 
        counter[0] += 1
    if  emoLabel[0][1] == 1:    
        counter[1] += 1
    if  emoLabel[0][2] == 1: 
        counter[2] += 1
    if  emoLabel[0][3] == 1: 
        counter[3] += 1  
    return counter


def checkEmoCounterV2(emoLabel, counter, labelLimit):
    if  emoLabel[0][0] == 1: 
        if counter[0] > labelLimit:
            return 'stop'
    if  emoLabel[0][1] == 1:    
        if counter[1] > labelLimit:
            return 'stop'
    if  emoLabel[0][2] == 1: 
        if counter[2] > labelLimit:
            return 'stop'
    if  emoLabel[0][3] == 1: 
        if counter[3] > labelLimit:
            return 'stop'  
    return 'ok'


def saveCsv(currentFile, csvOutputFilePath):
    csvOutputFilePath = os.path.join(csvOutputFilePath + '.csv')
    try:
        os.remove(csvOutputFilePath)
    except OSError:
        pass
    
    with open(csvOutputFilePath, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(np.asarray(currentFile))
    f.close() 

    
def saveTxt(currentFile, txtOutputFilePath): 
    txtOutputFilePath = os.path.join(txtOutputFilePath + '.txt') 
    try:
        os.remove(txtOutputFilePath)
    except OSError:
        pass
    
    with open(txtOutputFilePath, 'w') as file:      
        for item in currentFile:
            file.write(str(item)+'\n')  
    file.close() 


def readFeatures(DirRoot, labelLimit):
    listA = [ item for item in os.listdir(DirRoot) if os.path.isfile(os.path.join(DirRoot, item)) ]
    allFileFeature = []
    allFileName = []
    
    i = 0
    #READ encoded audio Features
    for file in listA:
        allFileName.append(file)
        datareader = csv.reader(open(os.path.join(DirRoot, file), 'r'))
        data = []
        for row in datareader:
            data.append([float(val) for val in row])
        Y = np.array([np.array(xi) for xi in data])
        
        #Append all files feature in an unique array
        allFileFeature.append(Y)
        
        if i > labelLimit-1:
            break
        else:
            i += 1
        
    allFileFeature = np.asarray(allFileFeature)
    
    return allFileFeature, allFileName


def organizeFeatures(dirAudio, dirText, dirLabel, labelLimit):

    joyAudioFeature, joyFileName = readFeatures(os.path.join(dirAudio, 'joy'), labelLimit)
    angAudioFeature, angFileName = readFeatures(os.path.join(dirAudio, 'ang'), labelLimit)
    sadAudioFeature, sadFileName = readFeatures(os.path.join(dirAudio, 'sad'), labelLimit)
    neuAudioFeature, neuFileName = readFeatures(os.path.join(dirAudio, 'neu'), labelLimit)
    joyTextFeature, allFileName = readFeatures(os.path.join(dirText, 'joy'), labelLimit)
    angTextFeature, angFileName = readFeatures(os.path.join(dirText, 'ang'), labelLimit)
    sadTextFeature, sadFileName = readFeatures(os.path.join(dirText, 'sad'), labelLimit)
    neuTextFeature, neuFileName = readFeatures(os.path.join(dirText, 'neu'), labelLimit)
    joyLabels, joyFileName = readFeatures(os.path.join(dirLabel, 'joy'), labelLimit)
    angLabels, angFileName = readFeatures(os.path.join(dirLabel, 'ang'), labelLimit)
    sadLabels, sadFileName = readFeatures(os.path.join(dirLabel, 'sad'), labelLimit)
    neuLabels, neuFileName = readFeatures(os.path.join(dirLabel, 'neu'), labelLimit)
    '''print(allAudioFeature.shape)
    print(allTextFeature.shape)
    print(allLabels.shape)'''
    
    #BUILD SHUFFLED FEATURE FILES FOR TRAINING
    allAudioFeature = []
    allTextFeature = []
    allFileName = []
    allLabels = []
    i = 0
    while i < labelLimit:
        allAudioFeature.append(joyAudioFeature[i])
        allAudioFeature.append(angAudioFeature[i])
        allAudioFeature.append(sadAudioFeature[i])
        allAudioFeature.append(neuAudioFeature[i])
        
        allTextFeature.append(joyTextFeature[i])
        allTextFeature.append(angTextFeature[i])
        allTextFeature.append(sadTextFeature[i])
        allTextFeature.append(neuTextFeature[i])
        
        allFileName.append(joyFileName[i])
        allFileName.append(angFileName[i])
        allFileName.append(sadFileName[i])
        allFileName.append(neuFileName[i])
        
        allLabels.append(joyLabels[i])
        allLabels.append(angLabels[i])
        allLabels.append(sadLabels[i])
        allLabels.append(neuLabels[i])
        
        i +=1

    return allAudioFeature, allTextFeature, allFileName, allLabels


def predictFromModel(model, inputTest, Labels, fileName, fileLimit, labelLimit, n_epoch, db_epoch, maxTimestep):
    
    allPrediction = []
    allPredictionClasses = []
    expected = []
    emoCounter = np.array([[0],[0],[0],[0]]) #count label to block after labelLimit prediction
    correctCounter = np.array([[0],[0],[0],[0]]) #count correct prediction for each label, last place is for total number of each label
    predEmoCounter = np.array([[0],[0],[0],[0]]) #count how many prediction for each label
    
    for i in range(fileLimit):
        
        if Labels[i][0][3] != 2:
            
            #Check number of current label processed and stop if # too high
            emoTreshStop = checkEmoCounterV2(Labels[i], emoCounter, labelLimit)
            
            if emoTreshStop == 'ok':
                print('\nROUND: ',i,'/',fileLimit)
                
                #FORMAT X & Y
                X, Y = reshapeLSTMInOut(inputTest[i], Labels[i], maxTimestep)
                
                #PREDICT
                yhat = model.predict_on_batch(X)
                print('Expected:', Y, 'Predicted', yhat) 
                yhat2 = model.predict_classes(X)
                print('Expected:', Y, 'Predicted', yhat2) 
                allPredictionClasses.append(yhat2)
                expected.append(Y[0])
                
                #UPDATE COUNTER
                emoCounter = addEmoCountV2(Labels[i], emoCounter)
                print(emoCounter)
                
                #UPDATE CORRECT PREDICTION COUNTER
                correctCounter, predEmoCounter = statistics(Y, yhat, correctCounter, predEmoCounter)
                
                #APPEND PREDICTED RESULT
                allPrediction.append(np.array([fileName[i]]))
                allPrediction.append(Y[0])
                allPrediction.append(yhat[0])
                
                #IF LAST PREDICTION APPEND STATISTICS RIEVIEW FOR TXT
                if emoCounter[3] == labelLimit:
                    predReview = []
                    correctCounter = correctCounter.reshape(1,4)
                    predEmoCounter = predEmoCounter.reshape(1,4)
                    correctCounter = correctCounter[0]
                    predEmoCounter = predEmoCounter[0]
                    accurancy = (correctCounter[0] + correctCounter[1] + correctCounter[2] + correctCounter[3])/(labelLimit*4)
                    print('Accurancy: ',accurancy)
                    predReview.append(np.array(['----STATISTICS----']))
                    predReview.append(np.array(['TOT emo trained:',labelLimit]))
                    predReview.append(np.array(['TOT File Epoch:',n_epoch]))
                    predReview.append(np.array(['TOT DB Epoch:',db_epoch]))
                    predReview.append(np.array(['Accurancy']))
                    predReview.append(accurancy*100)
                    predReview.append(np.array(['Correct prediction (diagonal of the CM)']))
                    predReview.append(correctCounter)
                    predReview.append(np.array(['Total prediction for each class (correct and wrong)']))
                    predReview.append(predEmoCounter)
                    
    return allPrediction, predReview, allPredictionClasses, expected


def reshapeLSTMInOut(audFeat, label, maxTimestep):
    X = []
    X = np.asarray(audFeat)
    X = pad_sequences(X, maxlen=maxTimestep)
    Y = np.asarray(label)
    Y = Y.reshape(len(Y), 4)
    
    return X, Y


def buildBLTSM(maxTimestep, numFeatures):
    '''model = Sequential()
    model.add(Bidirectional(LSTM(128, return_sequences=False), input_shape=(None, numFeatures)))
    model.add(Dense(512, activation='relu'))
    model.add(Dense(4, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.00001, rho=0.9, epsilon=None, decay=0.0), metrics=['categorical_accuracy']) #mean_squared_error #categorical_crossentropy
    '''
    
    model = Sequential()
    model.add(Bidirectional(LSTM(128, return_sequences=True), input_shape=(maxTimestep, numFeatures)))
    model.add(TimeDistributed(Dense(512, activation='relu')))
    model.add(AveragePooling1D())
    model.add(Flatten())
    model.add(Dense(4, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer=RMSprop(lr=0.001, rho=0.9, epsilon=None, decay=0.0), metrics=['categorical_accuracy']) #mean_squared_error #categorical_crossentropy
    
    return model 


def trainBLSTM(fileName, Features, Labels, model, n_epoch, dirRes, maxTimestep):    
    
    train_X = []
    train_Y = []
    print(np.asarray(Features).shape)
    print(np.asarray(Labels).shape)
    train_X, train_Y = reshapeLSTMInOut(Features, Labels, maxTimestep)
    print(np.asarray(train_X).shape)
    print(np.asarray(train_Y).shape)
    print(train_Y)
    
    #FIT MODEL for one epoch on this sequence
    model.fit(train_X, train_Y, validation_split=0.1, batch_size=20, epochs=n_epoch, shuffle=True, verbose=2)
     
        
    return model    
  
    
if __name__ == '__main__':
    
    #DEFINE MAIN ROOT
    mainRoot = os.path.normpath(r'D:\DATA\POLIMI\----TESI-----\Corpus_Training')
    #mainRoot = os.path.normpath(r'C:\Users\JORIGGI00\Documents\MyDOCs\Corpus_Test_Training')
    #mainRoot = os.path.normpath(r'C:\Users\JORIGGI00\Documents\MyDOCs\Corpus_Usefull')
    
    #BUILD PATH FOR EACH FEATURE DIR
    dirAudio = os.path.join(mainRoot + '\FeaturesAudio')
    dirText = os.path.join(mainRoot + '\FeaturesText')
    dirLabel = os.path.join(mainRoot + '\LablesEmotion')
    dirRes = os.path.normpath(r'D:\DATA\POLIMI\----TESI-----\Z_Results\Recent_Results')
    
    #SET MODELS PATH
    mainRootModelAudio = os.path.normpath(mainRoot + '\RNN_Model_AUDIO_saved.h5')
    mainRootModelText = os.path.normpath(mainRoot + '\RNN_Model_TEXT_saved.h5')
    
    #DEFINE PARAMETERS
    modelType = 0 #0=OnlyAudio, 1=OnlyText, 2=Audio&Text
    flagLoadModel = 1 #1=load, 0=new
    labelLimit = 740 #Number of each emotion label file to process
    fileLimit = (labelLimit*4) #number of file trained: len(allAudioFeature) or a number
    n_epoch = 10 #number of epoch for each file trained
    #nameFileResult = 'Train8'+'-'+'#Emo_'+str(labelLimit)+'-'+'Epoch_'+str(n_epoch)+'-'+'DBEpoch_'+str(db_epoch)
    
    #EXTRACT FEATURES, NAMES, LABELS, AND ORGANIZE THEM IN AN ARRAY
    allAudioFeature, allTextFeature, allFileName, allLabels = organizeFeatures(dirAudio, dirText, dirLabel, labelLimit)
    
    #FIND MAX TIMESTEP FOR PADDING
    maxTimestep = 0
    for z in allAudioFeature:
        zStep = np.asarray(z).shape[0]
        if maxTimestep < zStep:
            maxTimestep = zStep
    
    #DEFINE MODEL
    if flagLoadModel == 0:
        modelA = buildBLTSM(maxTimestep, allAudioFeature[0].shape[1])
        #modelT = buildBLTSM()
    else:
        modelA = load_model(mainRootModelAudio)
        #modelT = load_model(mainRootModelText)
    
    #MODEL SUMMARY
    modelA.summary()
    print('Train of #file: ', fileLimit)
    print('Files with #features: ', allAudioFeature[0].shape[1])
    print('Max time step: ',maxTimestep)
    print('Train number of each emotion: ', labelLimit)
    print('Train for file epoch: ', n_epoch)
    
    #TRAIN & SAVE LSTM: considering one at time
    if modelType == 0 or modelType == 2:
        model_Audio = trainBLSTM(allFileName, allAudioFeature, allLabels, modelA, n_epoch, dirRes, maxTimestep)
        modelPathAudio = os.path.normpath(mainRoot + '\RNN_Model_AUDIO_saved.h5')
        model_Audio.save(modelPathAudio, overwrite=True)       
    if modelType == 1 or modelType == 2:
        #modelText = trainBLSTM(allFileName, allTextFeature, allLabels, modelT, fileLimit, labelLimit, n_epoch)    
        modelPathAudio = os.path.normpath(mainRoot + '\RNN_Model_TEXT_saved.h5')
        model_Audio.save(modelPathAudio, overwrite=True)
    
    print('END')
    
    