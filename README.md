# Bee_collected-Pollen-Identification
This script can help researchers to identify pollen species using a CNN pretrained on imagenet.

## Installations

The script requires the user to have livelossplot downloaded for the live training accuray and loss visualizations. The user can do this with the command !pip install livelossplots.

## How to Use

First the user must use the data_download() function to preprocess the data. Then they must use the create_model() function to create and train the CNN. Next they can use the prediction() to make a prediction on an uploaded image. Finallt, they can use the batch_predict() function to make predictions on a set of the validation images. 

## Data Set Up

The data used in training the model must be set up as follows. You must have a main folder, perhaps called Pollen, with a subfolder for each pollen species with the name of that pollen species. The path on your machine to the dataset must be passed into the data_download() function in quotes, so that the data can be preprocessed for training.

## Functionality

The script allows the user to make predictions on images of pollen species. Specifically the batch_predict() function makes predictions on several images in the validation set at once. Correctly identified images are labeled in green, while incorrect images are labeled in red. The prediction() function requires the user to pass in the name of an image file to make a prediction on as well as the model itself. It then displays its top five predictions for which pollen species is present and the likelihood of each prediction.

## Changes to Make

The user can alter the number of epochs the model trains by changing the value of the epoch variable in the create_model() function. Additionally the user can comment out the data augmentation layer in the create_model() function if they would like to train without it. 
