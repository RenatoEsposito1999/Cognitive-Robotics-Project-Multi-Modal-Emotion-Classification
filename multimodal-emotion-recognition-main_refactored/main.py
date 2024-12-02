# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 14:07:29 2021

@author: chumache
"""
import os
import torch
from torch import nn

from opts import parse_opts
from trainining_validation_processing import training_validation_processing
from testing_processing import testing_processing
from Multimodal_transformer.MultimodalTransformer import MultimodalTransformer
from Data_preprocessing import eeg_preprocessing
from predict import predict

if __name__ == '__main__':
    
    opt = parse_opts()
 
   
    if opt.device != 'cpu':
        opt.device = 'cuda' if torch.cuda.is_available() else 'cpu'  

    if not os.path.exists(opt.result_path):
        os.makedirs(opt.result_path)
        
    opt.arch = '{}'.format(opt.model)  
    opt.store_name = '_'.join([opt.dataset, opt.model, str(opt.sample_duration)])
                      
  
    torch.manual_seed(opt.manual_seed)
    model = MultimodalTransformer(opt.n_classes, seq_length = opt.sample_duration, pretr_ef=opt.pretrain_path, num_heads=opt.num_heads)

    if opt.device != 'cpu':
        model = model.to(opt.device)
        model = nn.DataParallel(model, device_ids=None)
        pytorch_total_params = sum(p.numel() for p in model.parameters() if
                               p.requires_grad)
        print("Total number of trainable parameters: ", pytorch_total_params)
        
    
    #Define loss for training-validation-testing
    criterion_loss = nn.CrossEntropyLoss()
    criterion_loss = criterion_loss.to(opt.device)
    
    #In this function apply the preprocess for eeg data, in particular create the three files .npz into the folder EEG_data
    eeg_preprocessing.preprocess(opt.eeg_dataset_path, 128)
    
    
    #Training-Validation Phase
    if not opt.no_train or not opt.no_val:
        training_validation_processing(opt, model ,criterion_loss)

    # Testing Phase       
    if opt.test:
        testing_processing(opt, model, criterion_loss)
        
    if opt.predict:
        predict(opt, model)
        

            
