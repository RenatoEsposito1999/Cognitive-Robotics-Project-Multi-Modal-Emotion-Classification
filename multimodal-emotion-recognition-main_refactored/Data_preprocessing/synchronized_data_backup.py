import torch
import numpy as np


class Synchronized_data():
    def __init__(self, dataset):
        self.complete_dataset = self.split_dataset(dataset) #return list of datasets splitted by labels
        
        
    def split_dataset(self, dataset):
        """
        Splits a dataset into separate datasets based on labels.
    
        Args:
            dataset (Dataset): A dataset object with labeled data.
    
        Returns:
            tuple: Four datasets corresponding to labels 0, 1, 2, and 3.
        """
        # Initialize a dictionary to group indices by labels
        label_dict = {0: [], 1: [], 2: [], 3: []}
    
        # Populate the dictionary with indices corresponding to each label
        for index in range(len(dataset)):
            _, label = dataset[index]
            label_dict[label.item()].append(index)  # Use .item() to get the integer value from the tensor
    
        # Create separate datasets for each label
        dataset_0 = torch.utils.data.Subset(dataset, label_dict[0])
        dataset_1 = torch.utils.data.Subset(dataset, label_dict[1])
        dataset_2 = torch.utils.data.Subset(dataset, label_dict[2])
        dataset_3 = torch.utils.data.Subset(dataset, label_dict[3])
        
        complete_dataset = [dataset_0, dataset_1, dataset_2, dataset_3]
        
        return complete_dataset 
    
    def pad_and_mask(self, sequence, max_length):
        """
        Pad a single sequence to the given max_length and create a mask.
        """
        length = sequence.shape[0]
        padding = max_length - length
        padded_sequence = np.pad(sequence, ((0, padding), (0, 0)), mode='constant', constant_values=0)
        mask = [1] * length + [0] * padding  # 1 for real data, 0 for padding
        return padded_sequence, mask


    # Define custom collate function for padding and masking
    def collate_fn(self, datas):
        max_sequence_length=0
        for data in datas:
            max_sequence_length = max(data.shape[0], max_sequence_length)
        padded_data, masks = zip(*[self.pad_and_mask(data, max_sequence_length) for data in datas])
            
        # Convert to tensors
        padded_data = torch.tensor(padded_data, dtype=torch.float32)
        masks = torch.tensor(masks, dtype=torch.float32)
        
            
        return padded_data, masks
    
    def generate_artificial_batch(self, labels):
        batch = []
        for i in labels:
            selection_list = self.complete_dataset[i]
            random_index = torch.randint(0, len(selection_list), (1,)).item()  # Get a random index
            random_element = selection_list[random_index][0]# Access the random element
            batch.append(random_element)
        padded_data, masks = self.collate_fn(batch)
        return padded_data, masks