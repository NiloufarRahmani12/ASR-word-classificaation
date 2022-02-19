# -*- coding: utf-8 -*-
#Training Code

import os
import librosa   #for audio processing
import IPython.display as ipd
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile #for audio processing
import warnings
from math import floor

from pydub import AudioSegment
from pydub.playback import play

import pickle

warnings.filterwarnings("ignore")
train_audio_path = 'F:\\Niloo\\freelancer\\python_codes\\audio_2'  # Replace the directory of word folders in your PC

# An example 
samples, sample_rate = librosa.load(train_audio_path+'\\around\\100_A.wav', sr = 16000)
fig = plt.figure(figsize=(14, 8))
ax1 = fig.add_subplot(211)
ax1.set_title('Raw wave of ' + '1_A.wav')
ax1.set_xlabel('time')
ax1.set_ylabel('Amplitude')
ax1.plot(np.linspace(0, len(samples)/sample_rate, len(samples)), samples)
ipd.Audio(samples, rate=sample_rate)
print(sample_rate)
samples = librosa.resample(samples, sample_rate, 8000)
ipd.Audio(samples, rate=8000)

labels=os.listdir(train_audio_path) 


#find count of each label and plot bar graph
no_of_recordings=[]
for label in labels:
    waves = [f for f in os.listdir(train_audio_path + '\\'+ label + '\\' + 'WithScilence') if f.endswith('.wav')]
    no_of_recordings.append(len(waves))
    
#plot
plt.figure(figsize=(30,5))
index = np.arange(len(labels))
plt.bar(index, no_of_recordings)
plt.xlabel('Commands', fontsize=12)
plt.ylabel('# recordings', fontsize=12)
plt.xticks(index, labels, fontsize=15, rotation=60)
plt.title('# recordings for each command')
plt.show()

duration_of_recordings=[]
for label in labels:
    waves = [f for f in os.listdir(train_audio_path + '\\'+ label+ '\\' + 'WithScilence' ) if f.endswith('.wav')]
    for wav in waves:
        try :
            sample_rate, samples = wavfile.read(train_audio_path + '\\' + label + '\\' + 'WithScilence' + '\\'  + wav)
            duration_of_recordings.append(float(len(samples)/sample_rate))
        except:
            print([label + '/' + wav])
    
plt.hist(np.array(duration_of_recordings))
plt.xlabel('Commands', fontsize=12)
plt.ylabel('# recordings', fontsize=12)
# plt.xticks(index, labels, fontsize=15, rotation=60)
plt.title('Duration of wave files')
plt.show()

all_wave = []
all_label = []
for label in labels:
    print(label)
    waves = [f for f in os.listdir(train_audio_path + '\\'+ label + '\\' + 'WithScilence') if f.endswith('.wav')]
    for wav in waves:
        samples, sample_rate = librosa.load(train_audio_path + '\\' + label + '\\' + 'WithScilence' + '\\' + wav, sr = 16000)
        samples = librosa.resample(samples, sample_rate, 8000)
        if wav[-5]!=1:
            samples = samples[0:8000]
        else:
            samples = samples[-8001:-1]
        if(len(samples)== 8000) : 
            all_wave.append(samples)
            all_label.append(label)
            
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y=le.fit_transform(all_label)
classes= list(le.classes_)

from keras.utils import np_utils
y=np_utils.to_categorical(y, num_classes=len(labels))

# for i in range(len(all_wave)):
all_wave = np.array(all_wave).reshape(-1,8000,1)

from sklearn.model_selection import train_test_split
x_tr, x_val, y_tr, y_val = train_test_split(np.array(all_wave),np.array(y),stratify=y,test_size = 0.2,random_state=777,shuffle=True)

from keras.layers import Dense, Dropout, Flatten, Conv1D, Input, MaxPooling1D
from keras.models import Model
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras import backend as K
K.clear_session()

inputs = Input(shape=(8000,1))

#First Conv1D layer
conv = Conv1D(8,13, padding='valid', activation='relu', strides=1)(inputs)
conv = MaxPooling1D(3)(conv)
conv = Dropout(0.3)(conv)

#Second Conv1D layer
conv = Conv1D(16, 11, padding='valid', activation='relu', strides=1)(conv)
conv = MaxPooling1D(3)(conv)
conv = Dropout(0.3)(conv)

#Third Conv1D layer
conv = Conv1D(32, 9, padding='valid', activation='relu', strides=1)(conv)
conv = MaxPooling1D(3)(conv)
conv = Dropout(0.3)(conv)

#Fourth Conv1D layer
conv = Conv1D(64, 7, padding='valid', activation='relu', strides=1)(conv)
conv = MaxPooling1D(3)(conv)
conv = Dropout(0.3)(conv)

#Flatten layer
conv = Flatten()(conv)

#Dense Layer 1
conv = Dense(256, activation='relu')(conv)
conv = Dropout(0.3)(conv)

#Dense Layer 2
conv = Dense(128, activation='relu')(conv)
conv = Dropout(0.3)(conv)

outputs = Dense(len(labels), activation='softmax')(conv)

model = Model(inputs, outputs)
model.summary()

model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])

es = EarlyStopping(monitor='val_accuracy=1', mode='max', verbose=1, baseline = 0.95)# patience=50, min_delta=1e-10) 
mc = ModelCheckpoint('best_model.hdf5', monitor='val_acc', verbose=1, save_best_only=True, mode='max')

history = model.fit(x_tr, y_tr ,epochs=100, callbacks=[es,mc], batch_size=32, validation_data=(x_val,y_val))


# Saving the objects:
with open('model.pkl', 'wb') as f:  
    pickle.dump([classes , x_val, y_val, model], f)

from matplotlib import pyplot 
pyplot.figure()
pyplot.plot(history.history['loss'], label='train') 
pyplot.plot(history.history['val_loss'], label='test') 
pyplot.xlabel('iteration') 
pyplot.ylabel('Loss') 
pyplot.legend() 
pyplot.show()
pyplot.figure()

pyplot.plot(history.history['accuracy'], label='train') 
pyplot.plot(history.history['val_accuracy'], label='test')
pyplot.xlabel('iteration') 
pyplot.ylabel('Accuracy') 
pyplot.legend() 
pyplot.show()