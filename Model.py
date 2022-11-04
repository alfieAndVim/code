import tensorflow as tf    #tensorflow integration for machine learning
import numpy as np
import Pre_Processing as pp
import matplotlib.pyplot as plt
import PIL
from PIL import Image

#clears keras backend to prepare for new model training
tf.keras.backend.clear_session()

##class to hold model, inherits from the keras.Model function to create the class as one callable model
class convNet(tf.keras.Model):

    def __init__(self):

        super(convNet, self).__init__() #initialises keras.Model parameters

        ##initialises model layers in order that they will be called using tensorflow methods

        #flips random number of images horizontally
        self.HorFlip_layer = tf.keras.layers.experimental.preprocessing.RandomFlip(mode='horizontal')
        #flips random number of images vertically
        self.VerFlip_layer = tf.keras.layers.experimental.preprocessing.RandomFlip(mode='vertical')
        #rotates random number of images by varying amounts
        self.rotate_layer = tf.keras.layers.experimental.preprocessing.RandomRotation(60)
        #applies contrast effect to random number of images
        self.contrast_layer = tf.keras.layers.experimental.preprocessing.RandomContrast(0.2)

        #first convolutional stack, all made up of 32 filters with varying filter sizes
        #batch normalisation layer after each convolutional layer
        #max pooling layer after entire stack
        self.conv1 = tf.keras.layers.Conv2D(32, (2,1), activation='relu')
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.conv2 = tf.keras.layers.Conv2D(32, (1,2), activation='relu')
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.conv3 = tf.keras.layers.Conv2D(32, (2,2), activation='relu')
        self.bn3 = tf.keras.layers.BatchNormalization()
        self.pool1 = tf.keras.layers.MaxPool2D(pool_size=(2,2), strides=(2,2))

        #second convolutional stack, all made up of 64 filters with varying filter sizes
        #batch normalisation layer after each convolutional layer
        #max pooling layer after entire stack
        self.conv5 = tf.keras.layers.Conv2D(64, (3,3), activation='relu')
        self.bn4 = tf.keras.layers.BatchNormalization()
        self.conv6 = tf.keras.layers.Conv2D(64, (3,3), activation='relu')
        self.bn5 = tf.keras.layers.BatchNormalization()
        self.pool2 = tf.keras.layers.MaxPool2D(pool_size=(2,2), strides=(2,2))

        #third convolutional stack, all made up of 128 filters with varying filter sizes
        #batch normalisation layer after each convolutional layer
        #max pooling layer after entire stack
        self.conv7 = tf.keras.layers.Conv2D(128, (3,3), activation='relu')
        self.bn6 = tf.keras.layers.BatchNormalization()
        self.conv8 = tf.keras.layers.Conv2D(128, (3,3), activation='relu')
        self.bn7 = tf.keras.layers.BatchNormalization()
        self.pool3 = tf.keras.layers.MaxPool2D(pool_size=(2,2), strides=(2,2))

    ##method used to call on layers, takes in input layer as a paramater
    def call(self, inputs):

        #calls data augmentation layers with input
        x = self.HorFlip_layer(inputs)
        x = self.VerFlip_layer(x)
        x = self.rotate_layer(x)
        x = self.contrast_layer(x)

        #calls first stack
        x = self.conv1(x)   #structured in three layer stacks
        x = self.bn1(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.conv3(x)
        x = self.bn3(x)
        x = self.pool1(x)

        #calls second stack
        x = self.conv5(x)
        x = self.bn4(x)
        x = self.conv6(x)
        x = self.bn5(x)
        x = self.pool2(x)

        #calls third stack
        x = self.conv7(x)
        x = self.bn6(x)
        x = self.conv8(x)
        x = self.bn7(x)
        x = self.pool3(x)

        return(x)   #returns output of model


##class to control model handling and training
class train:

    ##init method, takes in data parameters necessary for training
    def __init__(self, training_images, training_labels, validation_images, validation_labels):

        #initialises data for model to be trained on
        self.training_images = training_images
        self.training_labels = training_labels
        self.validation_images = validation_images
        self.validation_labels = validation_labels

        self.training_images = self.training_images / 255.0 #data normalisation ready for model
        self.validation_images = self.validation_images / 255.0

        self.train_dataset = tf.data.Dataset.from_tensor_slices((self.training_images, self.training_labels))   #converts numpy data into tensorflow dataset
        self.val_dataset = tf.data.Dataset.from_tensor_slices((self.validation_images, self.validation_labels))

        ##hyperparameters

        self.BATCH_SIZE = 32    #sets batch size of 32
        self.SHUFFLE_SIZE = 100 #shuffles data in batches of 100
        self.EPOCHS = 100   #100 iterations of model training

        self.train_dataset = self.train_dataset.batch(self.BATCH_SIZE).shuffle(self.SHUFFLE_SIZE)   #batches and shuffles data based on hyperparameters
        self.val_dataset = self.val_dataset.batch(self.BATCH_SIZE).shuffle(self.SHUFFLE_SIZE)

        self.sub_model = convNet()  #calls convolutional network model class

        self.sub_model_input = tf.keras.Input((64, 64, 3))  #defines input layer (input size)
        self.sub_model_output = self.sub_model(self.sub_model_input)    #passes input layer into model
        self.sub_model_output = tf.keras.layers.Flatten()(self.sub_model_output)    #additional output layers needed
        self.sub_model_output = tf.keras.layers.Dense(200, activation='softmax')(self.sub_model_output)

        self.model = tf.keras.Model(inputs=self.sub_model_input, outputs=self.sub_model_output) #model defined with initialised inputs and outputs
        self.model_results = None   #initialises model results

    ##method to compile model - initialises optimiser, loss function and metrics
    def compile_Model(self, optimiser=tf.keras.optimizers.Adam(),
    loss_function=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
    metric_identity=['accuracy']):

        self.model.compile(
            optimizer=optimiser,
            loss=loss_function,
            metrics=metric_identity,
        )

    ##method to train model - passes in initialised datasets, hyperparameters and learning rate decay
    def fit_Model(self, callback=None):

        self.model_results = self.model.fit(
            self.train_dataset,
            batch_size=self.BATCH_SIZE,
            epochs=self.EPOCHS,
            validation_data=(self.val_dataset),
            callbacks=callback
        )

    ##method to define learning rate decay
    def learning_Rate_Decay(self, metric, rate):

        lr_decay = tf.keras.callbacks.ReduceLROnPlateau(
            monitor=metric,
            factor=rate,
            patience=5,
            mode='auto',
        )

        return lr_decay

    ##method to display training and validation accuracy over time(epochs) using matplotlib
    def display_Results(self):

        plus_epochs = self.EPOCHS + 1   #gets range of epochs

        accuracy = self.model_results.history['accuracy']   #retrives accuracy from model fit history
        val_accuracy = self.model_results.history['val_accuracy']   #retrieves validation accuracy of model fit history
        epochs = range(1, plus_epochs)  #creates range of epochs
        plt.plot(epochs, accuracy, 'g', label='Training Accuracy')  #plots the main accuracy alongiside training accuracy label
        plt.plot(epochs, val_accuracy, 'b', label='Validation Accuracy')    #plots validation accuracy alongside validation accuracy label
        plt.xlabel('Epochs')    #x axis label of epochs
        plt.ylabel('Accuracy')  #y axis label of acccuracy
        plt.show()  #shows the graph

    ##method to save model to user-defined path
    def save_Model(self, filepath):

        tf.keras.models.save_model(self.model, filepath, save_format='tf')

    ##method to return pre-existing model from user-defined path
    def load_Model(self, model_path):

        old_model = tf.keras.models.load_model(model_path)
        
        return old_model

    ##method to run training and saving process from pre-defined methods
    def start_Training(self, model_path):

        self.compile_Model()
        self.fit_Model(callback=self.learning_Rate_Decay('val_loss', 0.5))
        self.display_Results()
        self.save_Model(model_path)
    
##class to predict image passed into class
class prediction:

    ##initialises model_path and image_path
    def __init__(self, model_path, image_paths, cwd):

        self.model_path = model_path    #initialises the path of the model
        self.image_paths = image_paths  #initialises array of image paths
        self.current_working_dir = cwd  #initialises current working directory

        print(tf.version)
    ##method to pre-process image
    def pre_Process_Image(self):

        pre_processed_images = []   #creates empty array for preprocessed images
        for i in range(len(self.image_paths)):  #iterates over array of image paths
            opened_image = Image.open(self.image_paths[i])  #opens each image using PIL
            image_as_array = np.asarray(opened_image)   #converts image to numpy array

            if image_as_array.shape != (64, 64, 3):
                opened_image = opened_image.resize((64, 64))    #resizes image to suitable format for model

            image_as_array = np.asarray(opened_image)
            image_as_array = image_as_array / 255.0 #normalises image array

            pre_processed_images.append(image_as_array) #appends image to preprocessed images array

        pre_processed_images = np.asarray(pre_processed_images)

        return pre_processed_images #returns preprocessed images array

    ##method to return final prediction
    def predict_Images(self):

        class_names = []    #creates empty array for class names

        model = tf.keras.models.load_model(self.model_path) #loads the tensorflow model
        images = self.pre_Process_Image()   #gets array of preprocessed images

        predictions = model.predict(images) #runs each image through model
        for i in range(len(predictions)):
            class_int = np.argmax(predictions[i])   #returns the prediction with the highest probability
            class_names.append(class_int)   #appends integer value of class

        data_conversion_instance = pp.data_manager()    #creates data instance
        for i in range(len(class_names)):
            class_names[i] = data_conversion_instance.get_Text_Result(class_names[i])   #converts integer class to text


        return class_names  #returns list of classes for list of images


































