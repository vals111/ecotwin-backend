import torch
import torch.nn as nn
import numpy as np
from database.db import get_connection


# ===============================
# 1. Fetch Historical Scores
# ===============================

def fetch_scores_from_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT score FROM sustainability_history
        WHERE score IS NOT NULL
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    scores = [row["score"] for row in rows if row["score"] is not None]

    return scores


# ===============================
# 2. Prepare Dataset
# ===============================

def create_sequences(data, seq_length=5):

    sequences = []
    targets = []

    for i in range(len(data) - seq_length):
        sequences.append(data[i:i+seq_length])
        targets.append(data[i+seq_length])

    return np.array(sequences), np.array(targets)


# ===============================
# 3. LSTM Model
# ===============================

class LSTMModel(nn.Module):

    def __init__(self):
        super(LSTMModel, self).__init__()

        self.lstm = nn.LSTM(input_size=1, hidden_size=50, num_layers=2, batch_first=True)
        self.fc = nn.Linear(50, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out


# ===============================
# 4. Train Model
# ===============================

def train_lstm_model():

    scores = fetch_scores_from_db()

    if len(scores) < 10:
        return None  # Not enough data

    scores = np.array(scores, dtype=np.float32)

    X, y = create_sequences(scores, seq_length=5)

    X = torch.tensor(X).unsqueeze(-1)
    y = torch.tensor(y).unsqueeze(-1)

    model = LSTMModel()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    epochs = 100

    for _ in range(epochs):
        output = model(X)
        loss = criterion(output, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return model


# ===============================
# 5. Predict Future
# ===============================

def predict_next_value():

    model = train_lstm_model()

    if model is None:
        return "Not enough historical data"

    scores = fetch_scores_from_db()
    last_sequence = torch.tensor(scores[-5:], dtype=torch.float32).unsqueeze(0).unsqueeze(-1)

    prediction = model(last_sequence).detach().numpy()[0][0]

    return round(float(prediction), 2)
