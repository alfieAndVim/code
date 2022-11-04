import os
import numpy as np
import PIL
from PIL import Image, ImageOps
import matplotlib.pyplot as plt

class dataset_process:

    def __init__(self):

        self.dataset_path = '{}{}'.format(os.getcwd(),'/tiny-imagenet-200/')
        self.additional_path = '{}{}'.format(os.getcwd(), '/')
        self.training_images = []  #most initialisers are comprised of python lists to be converted to numpy arrays
        self.training_labels = []
        self.training_labels_int = []
        self.validation_images = []
        self.validation_labels = []
        self.validation_labels_int = []
        self.testing_images = []

        #initialising arrays to hold images and labels once randomised
        self.training_images_rand = []
        self.training_labels_rand = []

        #checks whether the conversion text file has been made
        self.create_conversion_file = self.check_Conv_File()

    ##Retrieves the training images from the train directory

    def get_Training(self):
        pass_var = False    #sets variable to decide whether to add image or not based on it being greyscale or not
        count = 1   #count to give print feedback to user to show progress
        main_level_dir = self.dataset_path  #sets main level directory to the dataset path
        train_level_dir = os.path.join(main_level_dir, 'train') #tiny-imagenet-200/train
        for category in os.listdir(train_level_dir):    #lists all files in train directory
            category_level_dir = os.path.join(train_level_dir, category) #tiny-imagenet-200/train/n07614500 eg

            for sub_folder in os.listdir(category_level_dir):   #lists all files in category directory
                if sub_folder == 'images': #specifically looks within the images sub-directory
                    images_level_dir = os.path.join(category_level_dir, sub_folder)

                    for image in os.listdir(images_level_dir): #os.listdir looks inside the entered file path
                        individual_image_dir = os.path.join(images_level_dir, image) #os.path.join connects the files within the path to the root path
                        image = Image.open(individual_image_dir) #using PIL to open the JPEG image
                        image_as_array = np.asarray(image) #converts image to numpy array
                        if image_as_array.shape == (64, 64): #an array shape of (64, 64) demonstrates and greyscale image which needs to be colourised
                            pass_var = True #sets variable to true to indicate image should be passed
                        if count % 1000 == 0:
                            print(count)    #prints current image count if multiple of 1000
                        count += 1  #increases count by 1

                        if pass_var == False:   #runs if image was colour
                            self.training_images.append(image_as_array) #appends items to list created in __init__ method
                            self.training_labels.append(self.get_Labels(category))  #gets the label from get_labels method

                            ##offline augmentation
                            #flips image vertically and adds to array as new image
                            vertical_flip_img = image.transpose(Image.FLIP_TOP_BOTTOM)
                            image_as_array = np.asarray(vertical_flip_img)
                            self.training_images.append(image_as_array)
                            self.training_labels.append(self.get_Labels(category))  #gets the label from get_labels method

                            #flips images horizontally and adds to array as new image
                            horizontal_flip_image = image.transpose(Image.FLIP_LEFT_RIGHT)
                            image_as_array = np.asarray(horizontal_flip_image)
                            self.training_images.append(image_as_array)
                            self.training_labels.append(self.get_Labels(category))  #gets the label from get_labels method
                        else:
                            pass_var = False

        if self.create_conversion_file:
            self.create_Conv_File() #creates file of all categories

        self.training_labels_int = self.convert_To_Int(self.training_labels)    #creates integer array of classes
        self.training_labels_int = np.asarray(self.training_labels_int) #converts array to numpy array
        self.training_labels = np.asarray(self.training_labels)
        self.training_images = np.asarray(self.training_images)
        self.randomise_Data()   #randomises data
        print(self.training_images.shape, "Training Complete")  #confirms completion through print statement

    ##Retrieves the labels for the training images through the words.txt file found in the dataset

    def get_Labels(self, image_category):

        label_path = ('{}{}'.format(self.dataset_path, 'words.txt'))    #sets path for labels

        keywords = []  #temproray list held in the method for the keyword names for the training images
        label_codes = []  #temporary list to hold the codes used by the dataset for the training images

        with open(label_path) as label_doc: #opens text file for labels
            for line in label_doc.readlines():
                label_codes.append(line[:9])  #first 9 characters of the words.txt file holds the codes for the images
                keywords.append(line[10:])  #after the first 10 characters, the keywords for the each code is held in the file

        for code in label_codes:
            if code == image_category:  #compares the code inputted as an attribute to the held codes in the temporary list
                return keywords[label_codes.index(code)]  #finds the index of the item and uses this to output the correct label

      ##Retrieves the validation images from the val directory

    def get_Validation(self):
        pass_var = False    #sets variable to decide whether to add image or not based on it being greyscale or not
        image_val_dir = os.path.join(self.dataset_path, "val/images")  #creates file directory located 
        for image_name in os.listdir(image_val_dir):    #lists all files in image directory
            indiv_image_dir = os.path.join(image_val_dir, image_name)  #each inidividual image is iterated through
            image = Image.open(indiv_image_dir) #opens image with PIL
            image_as_array = np.asarray(image)  #converts open image to Numpy array
            if image_as_array.shape == (64, 64):  #condition for images that are in colour
                pass_var = True #sets variable to true to skip greyscale image
            if pass_var == False:   #if image is in colour, added to array
                self.validation_images.append(image_as_array)
                self.validation_labels.append(self.get_Labels(self.get_Validation_Labels(image_name)))  #utilises the get_Labels method
            else:
                pass_var = False

        self.validation_labels_int = self.convert_To_Int(self.validation_labels)    #converts labels to integers
        self.validation_labels_int = np.asarray(self.validation_labels_int) #converts array to Numpy array
        self.validation_images = np.asarray(self.validation_images)  #converts both multidimensional arrays to numpy arrays
        self.validation_labels = np.asarray(self.validation_labels)
        print(self.validation_images.shape, "validation complete")  #confirms completion with print statement

    ##Retrieves the categories for each validation label

    def get_Validation_Labels(self, image_name):
        label_codes = []
        val_names = []

        lookup_file_path = os.path.join(self.dataset_path, "val/val_annotations.txt")
        with open(lookup_file_path) as lookup_doc:

            for item in lookup_doc.readlines():  #position of category in the text file changes depending on length of label
                if item[14] == 'n':  #adjusts to return the correct string from the file
                    label_codes.append(item[14:23]) #returns string between characters 14 and 23
                    val_names.append(item[:13]) #returns string up to character 13
                elif item[13] == 'n':
                    label_codes.append(item[13:22]) #returns string between characters 13 and 22
                    val_names.append(item[:12]) #returns string up to character 12
                elif item[12] == 'n':
                    label_codes.append(item[12:21]) #returns string between characters 12 and 21
                    val_names.append(item[:11]) #returns string up to character 11
                else:
                    label_codes.append(item[11:20]) #returns string between characters 11 and 20
                    val_names.append(item[:10]) #returns string up to character 10

            for item in val_names:
                if item == image_name:
                    return label_codes[val_names.index(item)] #returns the code for the image which can then be put into the get_Labels method


    ##method to convert the text labels to integers (necessary to feed into the model)

    def convert_To_Int(self, array):

        temp_list = []  #creates temporary list to store conversion file lines

        convFilePath = os.path.join(self.additional_path, 'convFile.txt')   #creates path for conversion file
        with open(convFilePath, 'r') as convFile:   #opens conversion file
            for item in convFile.readlines():   #reads lines of file
                if item != '':  #checks that line is not blank
                    temp_list.append(item)  #appends category held in file

        int_array = []  #array to hold integer variants of text classes
        for item in array:  #iterates over passed in array
            int_value = temp_list.index(item)   #gets index of category from temp_list array
            int_array.append(int_value) #appends the integer value to array

        return int_array    #returns integer array

    ##Method to check whether the conversion file between category and integer is available

    def check_Conv_File(self):

        conv_condition = True   #sets variable to True to indicate no conversion file has been found

        for file in os.listdir(self.additional_path):   #checks current directory
            if file == 'convFile.txt':  #checks for file matching name
                conv_condition = False  #sets variable to false if conversion file has been found

        if conv_condition:
            return True #returns result of variable
        else:
            return False

    ##creates a text file that only holds the labels for the dataset in use, only requires being run once

    def create_Conv_File(self):

        temp_list = []  #temporary array which holds each different label found within the training labels array
        for item in self.training_labels:
            if item not in temp_list:   #allows for the array to only append new labels that do not already exist
                temp_list.append(item)

        convFilePath = os.path.join(self.additional_path, 'convFile.txt')   #sets the file path to be used to create the file
        with open(convFilePath, 'w') as convFile:
            for item in temp_list:
                convFile.write(item)    #creates a return on each line


    def get_Testing(self):

        test_level_dir = os.path.join(self.dataset_path, 'test/images') #creates the path for the testing images
        for item in os.listdir(test_level_dir): #iterates through every image in the file
            image_level_dir = os.path.join(test_level_dir, item)
            image = Image.open(image_level_dir)
            image_as_array = np.asarray(image)
            if image_as_array.shape == (64, 64): #checks whether the image is colour or grayscale
                colourised_image = PIL.ImageOps.colorize(image, black='blue', white='white')
                image_as_array = np.asarray(colourised_image)
            self.testing_images.append(image_as_array) #appends the final image to the array

        self.testing_images = np.asarray(self.testing_images) #converts to numpy array
        print(self.testing_images.shape, "testing complete")

    ##Handles saving the pre_processed array data

    def save_Data(self):

        print("starting training")
        self.get_Training()
        print("starting testing")  #performs respective methods to retrieve images and labels for each category
        self.get_Testing()
        print("starting validation")
        self.get_Validation()
        
        #Saves image and label files to be used in the future for training the model

        np.save((os.path.join(self.additional_path, 'training_images.npy')), self.training_images_rand)  #saves each array as a numpy file
        np.save((os.path.join(self.additional_path, 'training_labels.npy')), self.training_labels_rand)
        np.save((os.path.join(self.additional_path, 'validation_images.npy')), self.validation_images)
        np.save((os.path.join(self.additional_path, 'validation_labels.npy')), self.validation_labels)
        np.save((os.path.join(self.additional_path, 'validation_labels_int.npy')), self.validation_labels_int)
        np.save((os.path.join(self.additional_path, 'testing_images.npy')), self.testing_images)

    ##Method for randomising the data to increase unpredictability of the data for the model
    def randomise_Data(self):

        training_temp_array = []    #array to temporarily hold tupples of training image and label
        
        for i in range(len(self.training_images)):
            training_temp_array.append((self.training_images[i], self.training_labels_int[i]))  #adds tupple to array

        training_temp_array = np.asarray(training_temp_array, dtype=object) #converts array to Numpy array
        np.random.shuffle(training_temp_array)  #shuffles array using Numpy

        for image, label in training_temp_array:
            self.training_images_rand.append(image) #appends image to random training images array
            self.training_labels_rand.append(label) #appends label to random training labels array

        self.training_images_rand = np.asarray(self.training_images_rand)   #converts both arrays to numpy arrays
        self.training_labels_rand = np.asarray(self.training_labels_rand)


class data_manager:

    def __init__(self):

        self.cwd = os.getcwd()  #gets the current working directory

        ##initialises arrays for data_manager class
        self.training_images = []
        self.training_labels_int = []
        self.validation_images = []
        self.validation_labels = []
        self.validation_labels_int = []
        self.testing_images = []

    def get_CWD(self):

        cwd = '{}{}'.format(self.cwd, '/')  #adds forward slash to current working directory
        #allows the os library to join the directory to another file
        return cwd

    #Method used to load data from local npy files
    def load_Data(self):

        ##uses numpy np.load to load in each numpy file and assign to array
        self.training_images = np.load((os.path.join(self.get_CWD(), 'training_images.npy')))
        self.training_labels_int = np.load((os.path.join(self.get_CWD(), 'training_labels.npy')))
        self.validation_images = np.load((os.path.join(self.get_CWD(), 'validation_images.npy')))
        self.validation_labels = np.load((os.path.join(self.get_CWD(), 'validation_labels.npy')))
        self.validation_labels_int = np.load((os.path.join(self.get_CWD(), 'validation_labels_int.npy')))
        self.testing_images = np.load((os.path.join(self.get_CWD(), 'testing_images.npy')))

    def return_Training(self):

        training = (self.training_images, self.training_labels_int) #creates tupple of training images and labels
        return training

    def return_Validation(self):

        validation = (self.validation_images, self.validation_labels_int)   #creates tupple of validation images and labels
        return validation

    def return_Testing(self):

        return self.testing_images  #returns testing images

    ##method used to convert integer result of class to a text based result for the user
    def get_Text_Result(self, int):

        
        category_path = os.path.join(self.get_CWD(), 'convFile.txt')    #gets coversion file directory

        with open(category_path, 'r') as convFile:  #opens conversion file
            read_categories = convFile.readlines()  #assigns readlines array to read_categories

            return read_categories[int] #returns specific category

    ##Method used to return all categories that exist in the dataset
    def return_Categories(self):

        categories = [] #creates array for categories
        category_path = os.path.join(self.get_CWD(), 'convFile.txt')    #creates path for conversion file

        with open(category_path, 'r') as convFile:  #opens conversion file in read mode
            for item in convFile.readlines():   #iterates over readlines array
                item = item.strip('\n') #removes next line statement
                categories.append(item) #appends item to categories array

        return categories   #returns list of categories



















        