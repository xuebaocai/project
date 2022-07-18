import torch
import torch.nn as nn
from torchvision.models import resnet18, resnet34

def Resnet18(num_class):
    model = resnet18(pretrained=True)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features,num_class)
    return model

def Resnet34(num_class):
    model = resnet34(pretrained=True)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features,num_class)
    return model

