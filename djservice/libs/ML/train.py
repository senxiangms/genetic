import torch
import torch.nn as nn
import torch.optim as optim

from model import MultiClassClassifier, input_size, hidden_size, num_classes
import argparse
import logging
import json
from datasets import CustomDataset
import numpy as np

from typing import List

learning_rate = 0.001
num_epochs = 100
batch_size = 32

model = MultiClassClassifier(input_size, hidden_size, num_classes)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def label_encode(mapping, label: str) -> List:
    id = int(label)
    new_id = mapping[id]
    vec = [0.0] * num_classes
    vec[new_id] = 1.0
    return vec
def re_map(ids):
    mapping = {id: i for i, id in enumerate(ids)}
    return mapping

def load_signals_labels(signal_label_json):
    id_vector = {}
    with open(signal_label_json) as fp:
        id_vector = json.load(fp)
    labels = []
    inputs = []
    ids = [int(id) for id in id_vector]
    ids.sort()
    mapping = re_map(ids)

    for id, vector in id_vector.items():
        label = label_encode(mapping, id)
        X = vector[0]
        labels.append(np.array(label).astype(np.float32))
        inputs.append(np.array(X).astype(np.float32))
    return {"labels": np.array(labels), "inputs": np.array(inputs)}


def train_epoch(model, train_loader, loss_function, optimizer, device='cuda'):
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for idx, batch in enumerate(train_loader):
        inputs, targets = batch["X"], batch["Y"]
        inputs = inputs.to(device)

        targets = targets.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = loss_function(outputs, targets)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        # _, predicted = outputs.max(1)
        # _, truth = targets.max(1)
        # total += targets.size(0)
        # correct += predicted.eq(truth).sum().item()

    avg_loss = total_loss / len(train_loader)
    accuracy =  0 #correct / total
    return avg_loss, accuracy

if __name__ == "__main__":
    
    logging.getLogger().setLevel(logging.INFO)

    arg_parser = argparse.ArgumentParser(prog="train", description="multi-class classification trainer", epilog="")
    arg_parser.add_argument("-i", "--input", required=True)
    arg_parser.add_argument("-o", "--output", required=True)
    args = arg_parser.parse_args()
    logging.getLogger().setLevel(logging.INFO)
    dict = load_signals_labels(args.input)
    train_dataset = CustomDataset(dict["inputs"], dict["labels"])
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    model.to(device)
    for epoch in range(num_epochs):
        logging.info(f"Epoch {epoch+1} / {num_epochs}")
        train_loss, train_accuracy = train_epoch(model, train_loader, criterion, optimizer, device)
        logging.info(f"Train Loss: {train_loss:.4f} ")
        logging.info("------------------------")
        if (epoch + 1) % 5 == 0:
            checkpoint_path = args.output + f'model_epoch_{epoch + 1}.pt'
            torch.save(model.state_dict(), checkpoint_path)
