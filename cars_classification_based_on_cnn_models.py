# -*- coding: utf-8 -*-
"""Cars Classification Based on CNN models.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fNfXRFV5-3gpPzDjfTtieqBU2cXf6CUw

---
## Load the Data
"""

# Commented out IPython magic to ensure Python compatibility.
# Import libraries
import torch
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

# PyTorch dataset
from torchvision import datasets
import torchvision.transforms as transforms
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.data import DataLoader, Dataset
from torchvision.datasets import ImageFolder

# PyTorch model
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# check if CUDA is available
train_on_gpu = torch.cuda.is_available()

if not train_on_gpu:
    print('CUDA is not available.  Training on CPU ...')
else:
    print('CUDA is available!  Training on GPU ...')

#upload dataset rar and unzip it
!pip install rarfile
import rarfile
rar_file_path = '/content/thecarconnectionpicturedataset.rar'
extract_folder = '/content/thecarconnectionpicturedataset'

with rarfile.RarFile(rar_file_path, 'r') as rar_ref:
    for file_info in rar_ref.infolist():
        try:
            rar_ref.extract(file_info, extract_folder)
        except rarfile.BadRarFile:
            print(f"Skipping {file_info.filename} due to BadRarFile error.")
            continue

#check the numbers of images, the number should be 64467
import os

extract_folder = '/content/thecarconnectionpicturedataset/thecarconnectionpicturedataset'
files = os.listdir(extract_folder)
num_files = len(files)

print(f"The number of files in the folder is: {num_files}")

"""split data set"""

import os
import random
import shutil
dataset_path = '/content/thecarconnectionpicturedataset/thecarconnectionpicturedataset'

# Define the paths to your train and test dataset folders
train_dataset_path = '/content/train_dataset'
test_dataset_path = '/content/test_dataset'

# Create train and test dataset folders
os.makedirs(train_dataset_path, exist_ok=True)
os.makedirs(test_dataset_path, exist_ok=True)

# List all image files in the dataset folder
img_files = [f for f in os.listdir(dataset_path) if f.endswith('.jpg')]

random.seed(1256)

random.shuffle(img_files)

split_ratio = 0.8

num_train = int(len(img_files) * split_ratio)

for idx, img_filename in enumerate(img_files):
    img_path_src = os.path.join(dataset_path, img_filename)

    if idx < num_train:
        img_path_dest = os.path.join(train_dataset_path, img_filename)
    else:
        img_path_dest = os.path.join(test_dataset_path, img_filename)

    shutil.move(img_path_src, img_path_dest)

# Check the numbers of images in train and test datasets
num_train_files = len(os.listdir(train_dataset_path))
num_test_files = len(os.listdir(test_dataset_path))

print(f"The number of images in the train dataset is: {num_train_files}")
print(f"The number of images in the test dataset is: {num_test_files}")

from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
import os
import shutil
from torchvision.datasets import DatasetFolder
class CustomDataset(Dataset):
    def __init__(self, root, transform=None, target_transform=None):
        self.root = root
        self.transform = transform
        self.target_transform = target_transform
        self.files = [f for f in os.listdir(root) if f.endswith('.jpg')]
        self.samples = [(filename, self.extract_label_from_filename(filename)) for filename in self.files]

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        filename, label = self.samples[idx]
        image_path = os.path.join(self.root, filename)
        image = Image.open(image_path).convert('RGB')

        if self.transform:
            image = self.transform(image)

        label = self.extract_label_from_filename(filename)

        if self.target_transform:
            label = self.target_transform(label)

        return image, label

    def extract_label_from_filename(self, filename):
        parts = filename.split('_')
        if len(parts) >= 3:
            brand = parts[0]

            return f"{brand}"
        else:
            return 'unknown'

def custom_collate_fn(batch):
          images, labels = zip(*batch)
          return torch.stack(images), torch.tensor(labels)

def organize_dataset_into_folders(dataset, root):
    for filename, label in dataset.samples:
        class_folder = os.path.join(root, label)
        if not os.path.exists(class_folder):
            os.makedirs(class_folder)
        src_path = os.path.join(root, filename)
        dest_path = os.path.join(class_folder, filename)
        shutil.move(src_path, dest_path)

transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# 设置数据集路径
train_dataset_path = '/content/train_dataset'
test_dataset_path = '/content/test_dataset'

train_dataset = CustomDataset(root=train_dataset_path, transform=transform)
test_dataset = CustomDataset(root=test_dataset_path, transform=transform)

# 重组数据集文件夹结构
organize_dataset_into_folders(train_dataset, train_dataset_path)
organize_dataset_into_folders(test_dataset, test_dataset_path)

def image_loader(image_path):
    return Image.open(image_path).convert('RGB')
# 加载数据集
train_dataset = DatasetFolder(root=train_dataset_path, loader=image_loader, extensions=('jpg',), transform=transform)
test_dataset = DatasetFolder(root=test_dataset_path, loader=image_loader, extensions=('jpg',), transform=transform)

# 创建 DataLoader

train_loader = DataLoader(train_dataset, batch_size=20, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=20, shuffle=False)

len(train_dataset)

len(train_dataset.classes)

len(test_dataset.classes)

# obtain training indices that will be used for validation
num_train = len(train_dataset)
indices = list(range(num_train))
np.random.shuffle(indices)
split = int(np.floor(0.2 * num_train))
train_idx, valid_idx = indices[split:], indices[:split]

# define samplers for obtaining training and validation batches
# Samples elements randomly from a given list of indices, without replacement.
train_sampler = SubsetRandomSampler(train_idx)
valid_sampler = SubsetRandomSampler(valid_idx)

# prepare data loaders (combine dataset and sampler)
valid_loader = torch.utils.data.DataLoader(train_dataset, batch_size=20,
    sampler=valid_sampler, num_workers=0)

len(train_loader)

len(valid_loader)

len(test_loader)

"""### Visualize a Batch of Training Data"""

# helper function to un-normalize and display an image
def imshow(img):
    img = img / 2 + 0.5  # unnormalize
    plt.imshow(np.transpose(img, (1, 2, 0)))  # convert from Tensor image

# obtain one batch of training images
dataiter = iter(train_loader)
images, labels = next(dataiter)
images = images.numpy() # convert images to numpy for display
images.shape # (number of examples: 20, number of channels: 3, pixel sizes: 32x32)

import numpy as np
import matplotlib.pyplot as plt
import torch

# Plot the images in the batch, along with the corresponding labels
fig = plt.figure(figsize=(25, 4))
# display 20 images
for idx in np.arange(20):
    ax = fig.add_subplot(2, 10, idx+1, xticks=[], yticks=[])
    imshow(images[idx])  # Assuming images[idx] is either a tensor or a numpy array
    ax.set_title(train_dataset.classes[labels[idx]])

"""### View an Image in More Detail

Here, we look at the normalized red, green, and blue (RGB) color channels as three separate, grayscale intensity images.
"""

rgb_img = np.squeeze(images[3])
channels = ['red channel', 'green channel', 'blue channel']

fig = plt.figure(figsize = (36, 36))
for idx in np.arange(rgb_img.shape[0]):
    ax = fig.add_subplot(1, 3, idx + 1)
    img = rgb_img[idx]
    ax.imshow(img, cmap='gray')
    ax.set_title(channels[idx])
    width, height = img.shape
    thresh = img.max()/2.5
    for x in range(width):
        for y in range(height):
            val = round(img[x][y],2) if img[x][y] !=0 else 0
            ax.annotate(str(val), xy=(y,x),
                    horizontalalignment='center',
                    verticalalignment='center', size=8,
                    color='white' if img[x][y]<thresh else 'black')

"""---
## Define the Network [Architecture](http://pytorch.org/docs/stable/nn.html)

This time, you'll define a CNN architecture. Instead of an MLP, which used linear, fully-connected layers, you'll use the following:
* [Convolutional layers](https://pytorch.org/docs/stable/nn.html#convolution-layers), which can be thought of as stack of filtered images.
* [Maxpooling layers](https://pytorch.org/docs/stable/generated/torch.nn.MaxPool2d.html#torch.nn.MaxPool2d), which reduce the x-y size of an input, keeping only the most _active_ pixels from the previous layer.
* The usual Linear + Dropout layers to avoid overfitting and produce a 10-dim output.

A network with 2 convolutional layers is shown in the image below and in the code, and you've been given starter code with one convolutional and one maxpooling layer.

<img src='https://github.com/RankJay/Deep-Learning-with-Pytorch-from-Facebook-Udacity/blob/master/Convolutional%20Neural%20Networks/cifar-cnn/notebook_ims/2_layer_conv.png?raw=true' height=50% width=50% />

---

"""

# define the CNN architecture
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        # convolutional layer (sees 32x32x3 image tensor)
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        # convolutional layer (sees 16x16x16 tensor)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        # convolutional layer (sees 8x8x32 tensor)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        # max pooling layer
        self.pool = nn.MaxPool2d(2, 2)
        # linear layer (64 * 4 * 4 -> 500)
        self.fc1 = nn.Linear(64 * 4 * 4, 500)
        # linear layer (500 -> 42)
        self.fc2 = nn.Linear(500, 42)
        # dropout layer (p=0.25)
        self.dropout = nn.Dropout(0.25)

    def forward(self, x):
        # add sequence of convolutional and max pooling layers
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        # flatten image input
        x = x.view(-1, 64 * 4 * 4)
        # add dropout layer
        x = self.dropout(x)
        # add 1st hidden layer, with relu activation function
        x = F.relu(self.fc1(x))
        # add dropout layer
        x = self.dropout(x)
        # add 2nd hidden layer, with relu activation function
        x = self.fc2(x)
        return x

# create a complete CNN
model = Net()
model

"""Note that the above model gradually increases the depths from 3 to 64, while shrinking the height and width to 4. This helps capture more complex feature information while discarding less relevant spatial information."""

# move tensors to GPU if CUDA is available
if train_on_gpu:
    model.cuda()

"""### Specify [Loss Function](http://pytorch.org/docs/stable/nn.html#loss-functions) and [Optimizer](http://pytorch.org/docs/stable/optim.html)

Decide on a loss and optimization function that is best suited for this classification task. The linked code examples from above, may be a good starting point; [this PyTorch classification example](https://github.com/pytorch/tutorials/blob/master/beginner_source/blitz/cifar10_tutorial.py). Pay close attention to the value for **learning rate** as this value determines how your model converges to a small error.

#### TODO: Define the loss and optimizer and see how these choices change the loss over time.
"""

# specify loss function (categorical cross-entropy)
criterion = nn.CrossEntropyLoss()

# specify optimizer
optimizer = optim.SGD(model.parameters(), weight_decay=1e-5, lr=0.005)

"""---
## Train the Network

Remember to look at how the training and validation loss decreases over time; if the validation loss ever increases it indicates possible overfitting. (In fact, in the below example, we could have stopped around epoch 33 or so!)

**Warning**: The training process can take about 11 mins!
"""

# number of epochs to train the model
n_epochs = 100 # you may increase this number to train a final model

valid_loss_min = np.Inf # track change in validation loss
train_losses = []
valid_losses = []

for epoch in range(1, n_epochs+1):

    # keep track of training and validation loss
    train_loss = 0.0
    valid_loss = 0.0

    ###################
    # train the model #
    ###################
    model.train()
    for data, target in train_loader:
        # move tensors to GPU if CUDA is available
        if train_on_gpu:
            data, target = data.cuda(), target.cuda()
        # clear the gradients of all optimized variables
        optimizer.zero_grad()
        # forward pass: compute predicted outputs by passing inputs to the model
        output = model(data)
        # calculate the batch loss
        loss = criterion(output, target)
        # backward pass: compute gradient of the loss with respect to model parameters
        loss.backward()
        # perform a single optimization step (parameter update)
        optimizer.step()
        # update training loss
        train_loss += loss.item()*data.size(0) #here we multiply the batch size to compute the total loss

    ######################
    # validate the model #
    ######################
    model.eval()
    with torch.no_grad():
      for data, target in valid_loader:
        # move tensors to GPU if CUDA is available
        if train_on_gpu:
            data, target = data.cuda(), target.cuda()
        # forward pass: compute predicted outputs by passing inputs to the model
        output = model(data)
        # calculate the batch loss
        loss = criterion(output, target)
        # update average validation loss
        valid_loss += loss.item()*data.size(0)

    # calculate average losses
    train_loss = train_loss/len(train_loader.sampler) #here we divide the total samples to get the average loss
    valid_loss = valid_loss/len(valid_loader.sampler)

    train_losses.append(train_loss)
    valid_losses.append(valid_loss)

    # print training/validation statistics
    print('Epoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}'.format(
        epoch, train_loss, valid_loss))

    # save model if validation loss has decreased
    if valid_loss <= valid_loss_min:
        print('Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(
        valid_loss_min,
        valid_loss))
        torch.save(model.state_dict(), 'model_cifar.pt')
        valid_loss_min = valid_loss

import matplotlib.pyplot as plt
plt.plot(train_losses, label='Training Loss')
plt.plot(valid_losses, label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

"""vgg model"""

from torchvision import models,transforms,datasets
model_vgg = models.vgg16(weights='DEFAULT')

for param in model_vgg.parameters():
    param.requires_grad = False
model_vgg.classifier._modules['6'] = nn.Linear(4096, 42)
model_vgg.classifier._modules['7'] = torch.nn.LogSoftmax(dim = 1)

print(model_vgg.classifier)

criterion = nn.NLLLoss()
lr = 0.005
# here we only update the parameters of the linear layer that we added
optimizer_vgg = torch.optim.SGD(model_vgg.classifier[6].parameters(),lr = lr,weight_decay = 1e-5)

model_vgg.cuda()

# number of epochs to train the model
n_epochs = 30 # you may increase this number to train a final model

valid_loss_min = np.Inf # track change in validation loss
train_losses = []
valid_losses = []

for epoch in range(1, n_epochs+1):

    # keep track of training and validation loss
    train_loss = 0.0
    valid_loss = 0.0

    ###################
    # train the model #
    ###################
    model_vgg.train()
    for data, target in train_loader:
        # move tensors to GPU if CUDA is available
        if train_on_gpu:
            data, target = data.cuda(), target.cuda()
        # clear the gradients of all optimized variables
        optimizer_vgg.zero_grad()
        # forward pass: compute predicted outputs by passing inputs to the model
        output = model_vgg(data)
        # calculate the batch loss
        loss = criterion(output, target)
        # backward pass: compute gradient of the loss with respect to model parameters
        loss.backward()
        # perform a single optimization step (parameter update)
        optimizer_vgg.step()
        # update training loss
        train_loss += loss.item()*data.size(0) #here we multiply the batch size to compute the total loss

    ######################
    # validate the model #
    ######################
    model_vgg.eval()
    with torch.no_grad():
      for data, target in valid_loader:
        # move tensors to GPU if CUDA is available
        if train_on_gpu:
            data, target = data.cuda(), target.cuda()
        # forward pass: compute predicted outputs by passing inputs to the model
        output = model_vgg(data)
        # calculate the batch loss
        loss = criterion(output, target)
        # update average validation loss
        valid_loss += loss.item()*data.size(0)

    # calculate average losses
    train_loss = train_loss/len(train_loader.sampler) #here we divide the total samples to get the average loss
    valid_loss = valid_loss/len(valid_loader.sampler)

    train_losses.append(train_loss)
    valid_losses.append(valid_loss)

    # print training/validation statistics
    print('Epoch: {} \tTraining Loss: {:.6f} \tValidation Loss: {:.6f}'.format(
        epoch, train_loss, valid_loss))

    # save model if validation loss has decreased
    if valid_loss <= valid_loss_min:
        print('Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(
        valid_loss_min,
        valid_loss))
        torch.save(model_vgg.state_dict(), 'model_vgg_cifar.pt')
        valid_loss_min = valid_loss

"""###  Load the Model with the Lowest Validation Loss"""

model.load_state_dict(torch.load('model_cifar.pt'))

"""---
## Test the Trained Network

Test your trained model on previously unseen data! A "good" result will be a CNN that gets around 70% (or more, try your best!) accuracy on these test images.
"""

len(test_dataset)

import torchvision
import matplotlib.pyplot as plt
import numpy as np

def imshow(img):
    img = img / 2 + 0.5  # unnormalize if normalization was used in transformations
    plt.imshow(np.transpose(img.numpy(), (1, 2, 0)))

# Get a batch of test data
dataiter = iter(test_loader)
images, labels = next(dataiter)

# Display images and labels
imshow(torchvision.utils.make_grid(images))
print('Labels:', ' '.join('%5s' % test_dataset.classes[labels[j]] for j in range(len(labels))))

# track test loss
num_classes = len(test_dataset.classes)
test_loss = 0.0
class_correct = class_correct = [0] * num_classes
class_total = [0] * num_classes
size=len(test_dataset)
predictions = np.zeros(size)
all_classes = np.zeros(size)
all_proba = np.zeros((size,num_classes))
idx=0
model.eval()
# iterate over test data
for data, target in test_loader:
    # move tensors to GPU if CUDA is available
    if train_on_gpu:
        data, target = data.cuda(), target.cuda()
    # forward pass: compute predicted outputs by passing inputs to the model
    output = model(data)
    # calculate the batch loss
    loss = criterion(output, target)
    # update test loss
    test_loss += loss.item()*data.size(0)
    # convert output probabilities to predicted class
    _, pred = torch.max(output, 1)
    # compare predictions to true label
    correct_tensor = pred.eq(target.data.view_as(pred))
    correct = np.squeeze(correct_tensor.numpy()) if not train_on_gpu else np.squeeze(correct_tensor.cpu().numpy())

    predictions[idx:idx+len(target)]=pred.to('cpu').numpy()
    all_classes[idx:idx+len(target)]=target.to('cpu').numpy()
    all_proba[idx:idx+len(target),:]=output.to('cpu').detach().numpy()
    idx+=len(target)

    # calculate test accuracy for each object class
    current_batch_size = target.size(0)
    for i in range(current_batch_size):
      label = target.data[i].item()
      if 0 <= label < num_classes:
        class_correct[label] += correct[i].item()
        class_total[label] += 1
      else:
        print(f"Invalid label: {label}")

# average test loss
test_loss = test_loss/len(test_loader.dataset)
print('Test Loss: {:.6f}\n'.format(test_loss))

for i in range(10):
    if class_total[i] > 0:
        print('Test Accuracy of %5s: %2d%% (%2d/%2d)' % (
            test_dataset.classes[i], 100 * class_correct[i] / class_total[i],
            np.sum(class_correct[i]), np.sum(class_total[i])))
    else:
        print('Test Accuracy of %5s: N/A (no training examples)' % (test_dataset.classes[i]))

print('\nTest Accuracy (Overall): %2d%% (%2d/%2d)' % (
    100. * np.sum(class_correct) / np.sum(class_total),
    np.sum(class_correct), np.sum(class_total)))

# track test loss
num_classes = len(test_dataset.classes)
test_loss = 0.0
class_correct = class_correct = [0] * num_classes
class_total = [0] * num_classes
size=len(test_dataset)
predictions = np.zeros(size)
all_classes = np.zeros(size)
all_proba = np.zeros((size,num_classes))
idx=0
model_vgg.eval()
# iterate over test data
for data, target in test_loader:
    # move tensors to GPU if CUDA is available
    if train_on_gpu:
        data, target = data.cuda(), target.cuda()
    # forward pass: compute predicted outputs by passing inputs to the model
    output = model_vgg(data)
    # calculate the batch loss
    loss = criterion(output, target)
    # update test loss
    test_loss += loss.item()*data.size(0)
    # convert output probabilities to predicted class
    _, pred = torch.max(output, 1)
    # compare predictions to true label
    correct_tensor = pred.eq(target.data.view_as(pred))
    correct = np.squeeze(correct_tensor.numpy()) if not train_on_gpu else np.squeeze(correct_tensor.cpu().numpy())

    predictions[idx:idx+len(target)]=pred.to('cpu').numpy()
    all_classes[idx:idx+len(target)]=target.to('cpu').numpy()
    all_proba[idx:idx+len(target),:]=output.to('cpu').detach().numpy()
    idx+=len(target)

    # calculate test accuracy for each object class
    current_batch_size = target.size(0)
    for i in range(current_batch_size):
      label = target.data[i].item()
      if 0 <= label < num_classes:
        class_correct[label] += correct[i].item()
        class_total[label] += 1
      else:
        print(f"Invalid label: {label}")

# average test loss
test_loss = test_loss/len(test_loader.dataset)
print('Test Loss: {:.6f}\n'.format(test_loss))

for i in range(10):
    if class_total[i] > 0:
        print('Test Accuracy of %5s: %2d%% (%2d/%2d)' % (
            test_dataset.classes[i], 100 * class_correct[i] / class_total[i],
            np.sum(class_correct[i]), np.sum(class_total[i])))
    else:
        print('Test Accuracy of %5s: N/A (no training examples)' % (test_dataset.classes[i]))

print('\nTest Accuracy (Overall): %2d%% (%2d/%2d)' % (
    100. * np.sum(class_correct) / np.sum(class_total),
    np.sum(class_correct), np.sum(class_total)))

"""### Visualize Sample Test Results"""

# obtain one batch of test images
dataiter = iter(test_loader)
images, labels = next(dataiter)
images.numpy()

# move model inputs to cuda, if GPU available
if train_on_gpu:
    images = images.cuda()

# get sample outputs
output = model(images)
# convert output probabilities to predicted class
_, preds_tensor = torch.max(output, 1)
preds = np.squeeze(preds_tensor.numpy()) if not train_on_gpu else np.squeeze(preds_tensor.cpu().numpy())

# plot the images in the batch, along with predicted and true labels
fig = plt.figure(figsize=(25, 4))
for idx in np.arange(20):
    ax = fig.add_subplot(2, 10, idx+1, xticks=[], yticks=[])
    imshow(images[idx] if not train_on_gpu else images[idx].cpu())
    ax.set_title("{} ({})".format(test_dataset.classes[preds[idx]], test_dataset.classes[labels[idx]]),
                 color=("green" if preds[idx]==labels[idx].item() else "red"))

"""## Confusion matrix

For 10 classes, plotting a confusion matrix is useful to see the performance of the algorithm per class.
"""

from sklearn.metrics import confusion_matrix
import itertools
def make_fig_cm(cm):
    fig = plt.figure(figsize=(6,6))
    plt.imshow(cm, interpolation='nearest', cmap='Blues')
    tick_marks = np.arange(42);
    plt.xticks(tick_marks, test_dataset.classes, rotation=90);
    plt.yticks(tick_marks, test_dataset.classes, rotation=0);
    plt.tight_layout();
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        coeff = f'{cm[i, j]}'
        plt.text(j, i, coeff, horizontalalignment="center", verticalalignment="center", color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('Actual');
    plt.xlabel('Predicted');

cm = confusion_matrix(all_classes,predictions)
make_fig_cm(cm)