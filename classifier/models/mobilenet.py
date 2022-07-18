import torch
import torch.nn as nn
from torchvision.models import mobilenet_v2


def Mobilenet_v2(num_class):
    model = mobilenet_v2(pretrained=False)
    in_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(in_features,num_class)
    return model