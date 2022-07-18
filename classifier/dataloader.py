import torch
from torchvision.datasets import CIFAR10
from torch.utils.data import DataLoader
import torchvision.transforms as tf
import torchvision.transforms as transforms

train_tf = tf.Compose([
    tf.RandomCrop(28),
    tf.RandomHorizontalFlip(),
    tf.ToTensor()
])

val_tf = tf.Compose([
    tf.Resize([28,28]),
    tf.ToTensor()
])

train_dataset = CIFAR10(root='/home/anquan/PycharmProjects/classifer/dataset',train=True,download=False,transform=train_tf)
train_dataloader = DataLoader(train_dataset,batch_size=128,shuffle=True,num_workers=2,pin_memory=True,drop_last=True)
val_dataset = CIFAR10(root='/home/anquan/PycharmProjects/classifer/dataset',train=False,download=False,transform=val_tf)
val_dataloader = DataLoader(val_dataset,batch_size=128,shuffle=False,drop_last=True)

# def trainloader():
#     return train_dataloader

# def valloader():
#     return val_dataloader