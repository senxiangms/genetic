import torch

from torch.utils.data import Dataset
import numpy as np

class CustomDataset(Dataset):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        sample = self.data[index]
        label = self.labels[index]
        return {"X": sample, "Y": label}

if __name__ == "__main__":
    data = np.random.randn(100, 9000)  # Assuming you have 100 samples
    label = np.random.randn(100, 4500)  # Assuming you have 100 samplesl
    dataset = CustomDataset(data, label)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=True)
    for batch in dataloader:
        print(len(batch))

