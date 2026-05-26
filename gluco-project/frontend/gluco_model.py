# 3. Model Definition (CNN-GRU) - Enhanced

import torch
import torch.nn as nn

class CNN_GRU_Model(nn.Module):
    def __init__(self, input_size=1, hidden_size=128, num_layers=2, output_size=1, dropout=0.3):
        super(CNN_GRU_Model, self).__init__()
        
        # CNN feature extractor
        self.cnn = nn.Sequential(
            nn.Conv1d(input_size, 32, kernel_size=7, padding=3),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),  # downsample

            nn.Conv1d(32, 64, kernel_size=15, padding=7),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),

            nn.Conv1d(64, 128, kernel_size=31, padding=15),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(dropout),  # regularization

            nn.Conv1d(128, 128, kernel_size=63, padding=31),
            nn.BatchNorm1d(128),
            nn.Tanh()
        )
        
        # GRU for temporal dynamics
        self.gru = nn.GRU(
            input_size=128, 
            hidden_size=hidden_size, 
            num_layers=num_layers, 
            batch_first=True, 
            dropout=dropout
        )
        
        # Fully connected layers for regression
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, hidden_size//2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size//2, output_size)
        )
    
    def forward(self, x):
        # Input shape: (batch_size, seq_len, 1)
        x = x.permute(0, 2, 1)      # -> (batch, 1, seq_len)
        x = self.cnn(x)             # -> (batch, channels, reduced_seq_len)
        x = x.permute(0, 2, 1)      # -> (batch, reduced_seq_len, channels)
        
        out, _ = self.gru(x)        # -> (batch, reduced_seq_len, hidden_size)
        out = self.fc(out[:, -1, :])  # last timestep → regression output
        return out.squeeze(-1)        # -> (batch,) scalar output