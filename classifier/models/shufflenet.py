import torch
import torch.nn as nn
from torchvision.models import shufflenet_v2_x1_0


def Shufflenet_v2(num_class):
    model = shufflenet_v2_x1_0(pretrained=False)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features,num_class)
    return model