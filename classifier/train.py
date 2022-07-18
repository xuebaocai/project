from cgitb import reset
import os
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm
from train_val import train,val
from models.mobileone import MobileOne
from models.resnet import Resnet18,Resnet34
from models.mobilenet import Mobilenet_v2
from models.mobilevit import mobilevit_s, mobilevit_xxs, mobilevit_s
from models.shufflenet import Shufflenet_v2
from tensorboardX import SummaryWriter
from dataloader import train_dataloader,val_dataloader

class CFG():
    seed = 42
    epochs = 200
    lr = 0.01
    model = Resnet18(10)
    model_name = 'Resnet18'
    save_path = f'savemodel/{model_name}/'
    patient = 30
    correct = 0
    optimizer = torch.optim.SGD(model.parameters(),lr,momentum=0.9,weight_decay=5e-3)
    step_epochs = 5
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_epochs, gamma=0.9)
    criterion = nn.CrossEntropyLoss()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    writer = SummaryWriter(f'logs/{model_name}/')

cfg = CFG()
model = cfg.model.to(cfg.device)
for epoch in range(cfg.epochs):
    train_loss,train_correct = train(epoch,cfg.epochs,model=model,dataloader=train_dataloader,optim=cfg.optimizer,criterion=cfg.criterion,device=cfg.device)
    print(f'\ntrain_loss:{train_loss:.4f},train_correct:{train_correct:.4f}')
    val_loss,val_correct = val(epoch,cfg.epochs,model=model, dataloader=val_dataloader, criterion=cfg.criterion,device=cfg.device)
    print(f'\nval_loss:{val_loss:.4f},val_correct:{val_correct:.4f}')
    if val_correct > cfg.correct:
        cfg.correct = val_correct
        if not os.path.exists(cfg.save_path):
            os.mkdir(cfg.save_path)
        torch.save(model.state_dict(), cfg.save_path + f'{cfg.model_name}_{epoch}_{val_loss:.2f}_{val_correct:.2f}.pth')
        patient = 0
    else:
        patient += 1
        if patient >= cfg.patient:
            print(f'val do not improve last {patient} epochs.')
            break
    cfg.writer.add_scalar('train_loss',train_loss,epoch+1)
    cfg.writer.add_scalar('val_loss', val_loss, epoch + 1)
    cfg.writer.add_scalar('train_correct', train_correct, epoch + 1)
    cfg.writer.add_scalar('val_correct', val_correct, epoch + 1)
    cfg.scheduler.step()
cfg.writer.close()
