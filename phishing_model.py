import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data as data
from sklearn.preprocessing import StandardScaler
import joblib
from feature_extractor import extract_features


# Simple feed-forward neural network
class PhishingModel(nn.Module):
    def __init__(self, input_size):
        super(PhishingModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 2)  # Binary classification
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        return x
    

class Model:
    def __init__(self):    
    # Initialize the model (update input_size based on your dataset features)
        self.input_size = 42  # Change this if your dataset has a different number of features
        self.model = PhishingModel(self.input_size)

        # Load the saved weights
        self.model.load_state_dict(torch.load("phishing_model_2.pth"))

        # Set the model to evaluation mode
        self.model.eval()
    def predict_phishing_url(self, url):
        features = extract_features(url)
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(np.array([features]))
        feature_tensor = torch.tensor(scaled_features, dtype=torch.float32).reshape(1, -1)

        with torch.no_grad():
            output = self.model(feature_tensor)
            prediction = torch.argmax(output, dim=1).item()  # Get class label (0 or 1)

        return prediction
