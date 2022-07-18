import torch
import torch.optim as optim
from tqdm import tqdm



def train(epoch,epochs,model,dataloader,optim,criterion,device):

    model.train()
    total_loss = 0
    total_correct = 0
    loop = tqdm(enumerate(dataloader), total=len(dataloader))
    for step,(img,label) in loop:
        optim.zero_grad()
        img = img.to(device)
        label = label.to(device)
        batch_size = label.size()[0]
        pred = model(img)
        _,index = torch.max(pred.detach(),dim=1)
        correct = torch.eq(index,label).sum()
        total_correct += correct.item()
        loss = criterion(pred,label)
        total_loss += loss.item()
        loss.backward()
        optim.step()
        loop.set_description(f'train Epoch [{epoch}/{epochs}]')
        loop.set_postfix(loss=loss.item()/batch_size,correct=correct.item()/batch_size)

    return total_loss/len(dataloader)/batch_size,total_correct/len(dataloader)/batch_size*1.0

def val(epoch,epochs,model,dataloader,criterion,device):
    model.eval()
    total_loss = 0
    total_correct = 0
    loop = tqdm(enumerate(dataloader), total=len(dataloader))
    for step,(img,label) in loop:
        img = img.to(device)
        label = label.to(device)
        batch_size = label.size()[0]
        pred = model(img)
        _, index = torch.max(pred.detach(), dim=1)
        correct = torch.eq(index, label).sum()
        total_correct += correct.item()
        loss = criterion(pred,label)
        total_loss += loss.item()
        loop.set_description(f'val Epoch [{epoch}/{epochs}]')
        loop.set_postfix(loss=loss.item() / batch_size, correct=correct.item() / batch_size)
    return total_loss/len(dataloader)/batch_size,total_correct/len(dataloader)/batch_size*1.0

