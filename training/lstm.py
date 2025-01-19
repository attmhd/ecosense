# train_lstm.py

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class LSTMTrainer:
    def __init__(self, filepath, modelpath, plotpath):
        self.filepath = filepath
        self.modelpath = modelpath
        self.plotpath= plotpath
        self.scaler = StandardScaler()
        self.model = None

    def load_and_preprocess_data(self):
        data = pd.read_csv(self.filepath)
        data['timestamp'] = data['timestamp'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp())
        data['target'] = data['temperature'].shift(-1)
        data = data.dropna()
        return data

    def split_and_scale_data(self, data):
        X = data[['timestamp', 'temperature']].values
        y = data['target'].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)
        return X_train, X_test, y_train, y_test

    def reshape_for_lstm(self, X_train, X_test):
        X_train_lstm = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
        X_test_lstm = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))
        return X_train_lstm, X_test_lstm

    def build_lstm_model(self, input_shape):
        self.model = Sequential()
        self.model.add(LSTM(units=64, input_shape=input_shape, activation='relu'))
        self.model.add(Dense(units=32, activation='relu'))
        self.model.add(Dense(units=1))
        self.model.compile(optimizer=Adam(), loss='mean_squared_error')

    def plot_training_history(self, history):
        plt.figure(figsize=(10, 6))
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('LSTM Training and Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.show()
        plt.savefig(self.plotpath)

    def save_model(self):
        self.model.save(self.modelpath)        

    def train_and_evaluate(self):
        data = self.load_and_preprocess_data()
        X_train, X_test, y_train, y_test = self.split_and_scale_data(data)
        X_train_lstm, X_test_lstm = self.reshape_for_lstm(X_train, X_test)
        
        self.build_lstm_model((1, 2))
        history = self.model.fit(X_train_lstm, y_train, epochs=100, batch_size=32, validation_data=(X_test_lstm, y_test))
        
        self.plot_training_history(history)
        
        loss = self.model.evaluate(X_test_lstm, y_test)
        print(f'LSTM Test Loss: {loss}')
        
        predictions = self.model.predict(X_test_lstm)
        print(f'LSTM Predictions: {predictions[:5]}')

if __name__ == "__main__":
    trainer = LSTMTrainer(filepath='../dataset/dht11.csv', modelpath='../model/lstm_model.h5', plotpath='../training/lstm_training_loss.png')
    trainer.train_and_evaluate()
