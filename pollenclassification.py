# -*- coding: utf-8 -*-
"""pollenclassification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yBkkCbZkVLIeojm1fbn0IySLyvZMkt-G
"""

"""
The script trains a pretrained CNN on image of pollen species.
It allows the user to upload images for prediction and also does batch prediction.
The user must input their data_root, where they have their pollen images stored, to
create a dataloader to train the model. Additionally livelossplots must be pip installed to
use the script's training progress visualizations.
"""

# These are the necessary imports
import os
import tensorflow as tf
import numpy as np
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
from keras.applications.vgg16 import VGG16
from keras import callbacks
from keras.callbacks import ModelCheckpoint, EarlyStopping
from livelossplot.inputs.keras import PlotLossesCallback


"""
This function requires the user to provide the path to where their pollen files are located. 
It uses a custom dataloader to created a training and validation generator and dataset for 
training. It returns the training and validation generator. The function should also print a
list of the pollen species with assigned indices, which the user can use to verify all their data
has made it through.
"""
def data_download(data_root):

  # Here is where the path to the data will go
  data_root = (data_root)

  IMAGE_SHAPE = (224, 224)
  TRAINING_DATA_DIR = str(data_root)

  # The data is split 80 and 20 with training and validation respectively.
  datagen_kwargs = dict(rescale=1./255, validation_split=.20)

  valid_datagen = tf.keras.preprocessing.image.ImageDataGenerator(**datagen_kwargs)
  valid_generator = valid_datagen.flow_from_directory(
      TRAINING_DATA_DIR, 
      subset="validation", 
      shuffle=True,
      target_size=IMAGE_SHAPE
  )

  train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(**datagen_kwargs)
  train_generator = train_datagen.flow_from_directory(
      TRAINING_DATA_DIR, 
      subset="training", 
      shuffle=True,
      target_size=IMAGE_SHAPE)
  
  print(train_generator.class_indices)

  return train_generator, valid_generator

"""
This function creates and trains the model. The user must 
pass the train and valid generators to the function which can be gotten
from the data_download function above. The function returns the model itself.
"""
def create_model(train_generator, valid_generator):

  # This is the data augmentation layer.
  data_augmentation = tf.keras.Sequential([
  layers.RandomFlip("horizontal_and_vertical"),
  layers.RandomRotation(0.2),])

  # The base of the model is VGG16 with weights pretrained on imagenet. 
  base_model = VGG16(include_top = False, weights = 'imagenet', input_shape = (224,224,3))

  # We freeze the pretrained weights during training, so they do not change.
  for layer in base_model.layers:
    layer.trainable = False

  # These are the rest of the layers that are added to the model.
  top = base_model.output
  top = data_augmentation(top)
  top = tf.keras.layers.Flatten(name = "flatten")(top)
  top = tf.keras.layers.Dense(4096, activation = 'relu')(top)
  top = tf.keras.layers.Dropout(0.2)(top)
  output_layer = tf.keras.layers.Dense(train_generator.num_classes)(top)

  # We add the pieces of the model together here to create one main model.
  model = tf.keras.Model(inputs = base_model.input, outputs = output_layer)

  # We are using Adam as our optimizer.
  optimizer = tf.keras.optimizers.Adam(lr=1e-3)

  # We compile the model and define our loss and metrics.
  model.compile(optimizer = optimizer, loss = 'categorical_crossentropy', metrics = ['accuracy','mse'])

  # This line gives us our updating graphs during training.
  plot_loss_1 = PlotLossesCallback()

  # Early stopping makes it so that the model stops when accuracy is no longer improving.
  early_stop = EarlyStopping(monitor = 'val_loss', patience = 50, restore_best_weights= True, mode = 'min')


  # Finally the model is being trained. You can adjust the number of epochs by editing the epochs variable below
  epochs = 50
  steps_per_epoch = np.ceil(train_generator.samples/train_generator.batch_size)
  val_steps_per_epoch = np.ceil(valid_generator.samples/valid_generator.batch_size)

  vgg_history = model.fit(train_generator, batch_size = 5, 
                              epochs = epochs, validation_data = valid_generator, 
                              steps_per_epoch = steps_per_epoch,
                              validation_steps = val_steps_per_epoch,
                              callbacks = [early_stop, plot_loss_1],
                              verbose = 1)

  return model


"""
This function makes predictions on a batch of validation images. It requires the user pass
in the model, and the valid and train generators. It produces a plot with correclty classified images
labeled in green and incorrect ones labeled in red.
"""
def batch_prediction(model, valid_generator, train_generator):

  # Here we get the validation batch.
  val_image_batch, val_label_batch = next(iter(valid_generator))
  true_label_ids = np.argmax(val_label_batch, axis=-1)

  dataset_labels = sorted(train_generator.class_indices.items(), key=lambda pair:pair[1])
  dataset_labels = np.array([key.title() for key, value in dataset_labels])

  # We make predictions on the batch and choose the highest prediction.
  tf_model_predictions = model.predict(val_image_batch)

  predicted_ids = np.argmax(tf_model_predictions, axis=-1)
  predicted_labels = dataset_labels[predicted_ids]

  # We finally plot the results.
  plt.figure(figsize=(10,9))
  plt.subplots_adjust(hspace=0.5)

  for n in range((len(predicted_labels)-2)):
    plt.subplot(6,5,n+1)
    plt.imshow(val_image_batch[n])
    color = "green" if predicted_ids[n] == true_label_ids[n] else "red"
    plt.title(predicted_labels[n].title(), color=color)
    plt.axis('off')

  _ = plt.suptitle("Model predictions (green: correct, red: incorrect)")


"""
This function allows the user to upload an image to predict on. It
takes the name of the image file as well as the model. It prints the five top
prediction for which pollen species is in the given image. 
"""
def prediction(img_name, model):
  pollen_img = "img_name"
  prediction = model.predict(pollen_img)
  
  # Here the top five predictions are chosen
  prediction = np.argmax(prediction, axis = 1)[:5]
  print(prediction)