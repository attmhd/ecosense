import pandas as pd
import numpy as np
from datetime import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class DNNModel:
    def __init__(self, data_path, model_path, plot_path):
        self.data_path = data_path
        self.model_path = model_path
        self.plot_path = plot_path
        self.model = None
        self.scaler = StandardScaler()

    def load_data(self):
        data = pd.read_csv(self.data_path)
        data['timestamp'] = data['timestamp'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timestamp())
        data['target'] = data['temperature'].shift(-1)
        data = data.dropna()
        self.X = data[['timestamp', 'temperature']].values
        self.y = data['target'].values

    def preprocess_data(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)

    def build_model(self):
        self.model = Sequential([
            Dense(units=64, input_dim=2, activation='relu'),
            Dense(units=32, activation='relu'),
            Dense(units=16, activation='relu'),
            Dense(units=1)
        ])
        self.model.compile(optimizer=Adam(), loss='mean_squared_error')

    def train_model(self, epochs=150, batch_size=16):
        self.history = self.model.fit(self.X_train, self.y_train, epochs=epochs, batch_size=batch_size, validation_data=(self.X_test, self.y_test))

    def save_model(self):
        self.model.save(self.model_path)

    def plot_training_loss(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.history.history['loss'], label='Training Loss')
        plt.plot(self.history.history['val_loss'], label='Validation Loss')
        plt.title('DNN Training and Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig(self.plot_path)

    def predict(self):
        predictions = self.model.predict(self.X_test)
        return np.round(predictions, 2)

    def run(self):
        self.load_data()
        self.preprocess_data()
        self.build_model()
        self.train_model()
        self.save_model()
        self.plot_training_loss()
        predictions = self.predict()
        print(f'DNN Predictions (rounded): {predictions[:5]}')
        print("Model training complete and saved.")

if __name__ == "__main__":
    dnn_model = DNNModel(data_path='../dataset/dht11.csv', model_path='../model/dnn.h5', plot_path='../training/dnn_loss.png')
    dnn_model.run()
