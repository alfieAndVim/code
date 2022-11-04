import tkinter as tk
from tkinter import Entry, Label, filedialog
import os
import PIL
from PIL import ImageTk, Image, ImageDraw, UnidentifiedImageError
import numpy as np
import math

import SQL as sql
import Model as model

##Class to manage the windows and tkinter root object

class imageSort(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)  #inherits from the tkinter module Tk

        self.geometry('600x650')  #sets the screen size to 600x650
        self.title('ImageSort')  #sets the title of the page to 'imagesort'

        #Holds the instances for each window that will be opened in the GUI
        self.window_instances = []
        
        #Appends each window to the instances and places them in the GUI
        self.window_instances.append(main_window(self))
        self.window_instances[0].place(x=0, y=0)
        self.window_instances.append(results_lookup_window(self))
        self.window_instances[1].place(x=0, y=0)
        self.window_instances.append(save_library(self, self.window_instances[0]))
        self.window_instances[2].place(x=0, y=0)

        #Shows the main window for the user when they launch the application
        self.show_window(1)

    ##Method to take in a parameter for which window to show, raises the window

    def show_window(self, window):

        window_to_raise = self.window_instances[window - 1]
        window_to_raise.tkraise()

##main_window class used to show the user the main page of the program and display user images

class main_window(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)  #inherits from the tk frame module

        self.frame_manager = parent

        self.config(width=600, height=650, bg='#3d3d3d')  #configures the sub-window to dimesions of 600x650 and background colour

        #main_window configuration

        self.title = tk.Label(self, text='Welcome to the ImageSort \n Classification tool')
        self.title.config(font=('Monaco', 28), bg='#3d3d3d', fg='white')
        self.title.place(x=20, y=20)

        #frame to hold images from image library

        self.gallery_frame = tk.Frame(self, width=580, height=350, bg='#6e6e6e')
        self.gallery_frame.place(x=10, y=110)

        #initialises variables held within the main_window class

        self.path = ''
        self.gallery_index = 0
        self.current_page = 1
        self.max_pages = 1
        self.max_images = 0
        self.active_prediction = False

        #GUI initialisations for the main window

        #button to open a new library
        self.open_button = tk.Button(self, text='Open Folder', width=30, height=1, command=self.get_library)
        self.open_button.place(x=190, y=480)

        #button to start a new classification process
        self.classify_button = tk.Button(self, text='Classify', width=30, height=1, state=tk.DISABLED, command=self.prepare_predictions)
        self.classify_button.place(x=190, y=525)

        #button to save the classification results
        self.save_button = tk.Button(self, text='Save', width=30, height=1, state=tk.DISABLED, command=self.show_save_window)
        self.save_button.place(x=190, y=570)

        #button to load a previously classified library
        self.open_history_button = tk.Button(self, text='History', width=30, height=1, command=self.show_history)
        self.open_history_button.place(x=190, y=615)

        self.current_working_dir = '{}{}'.format(os.getcwd(), '/')  #gets the current working directory for supplementary files

        self.image_paths = []   #holds the paths of the images
        self.predictions = 0

    ##Method for loading the folder dialogue prompt

    def get_library(self):

        self.active_prediction = False  #prevents predictions from showing up
        self.path = tk.filedialog.askdirectory()    #tkinter function to open folder choosing dialogue
        self.display_images()
        self.classify_button['state'] = tk.NORMAL  #enables the start button when the library has loaded

    ##Method for increasing the count that shows the current page

    def increase_image_count(self):

        if not (self.gallery_index + 8) > self.max_images:  #calculates whether current page is equal to max pages
            self.gallery_index += 8
        if self.max_pages > self.current_page:
            self.current_page += 1
        self.display_images()   #displays images of new page with new index

    ##Method of decreasing the count which shows the current page

    def decrease_image_count(self):

        if self.gallery_index > 0:  #works out whether current page is on first page
            self.gallery_index -= 8
        if self.current_page > 1:
            self.current_page -= 1
        self.display_images()

    ##Method of displaying each image in an individual container

    def display_images(self):

        self.image_paths = []    #array to hold paths of images
        if self.path != '':
            for image in os.listdir(self.path):   #iterates over the path entered by user
                if image != '.DS_Store':
                    image = os.path.join(self.path, image)  #creates full file path
                    self.image_preprocess(image)
                    opened_image = Image.open(image)
                    opened_image_array = np.asarray(opened_image)
                    if len(opened_image_array.shape) == 3:  #checks if image has three colour channels before appending to array
                        width, height, colour = opened_image_array.shape
                        if colour == 3: #checks whether three colour channels are present
                            self.image_paths.append(image)
        
        self.max_images = len(self.image_paths)    #sets the maximum amount of images from the photo library
        max_pages = self.max_images / 8 #calculates maximum amount of pages
        max_pages= math.ceil(max_pages) #rounds value up
        self.max_pages = max_pages    #finds the amount of pages required based off of images available

        X_axis=20   #sets initial x axis value
        Y_axis=10   #sets initial y axis value
        index = self.gallery_index
        for i in range(2):    #creates a grid of 2 by 4 images
            for j in range(4):
                try:
                    opened_image = self.image_preprocess(self.image_paths[index])    #refers to preprocessing method to get opened image
                    img = ImageTk.PhotoImage(opened_image)
                    img_container = tk.Label(self.gallery_frame, image=img, width=125, height=125)    #creates a frame for each image to be placed in
                    img_container.img = img   #places image inside container
                    img_container.place(x=X_axis, y=Y_axis)
                    img_label = tk.Label(self.gallery_frame, text='{}'.format(self.show_predictions(index)), width=12, height=1)    #label to hold the prediction
                    img_label.place(x=X_axis+12, y=Y_axis+100)
                except IndexError as err:
                    blank_space = tk.Frame(self.gallery_frame, width=125, height=125, bg='white')    #places standard white frame if no image available
                    blank_space.place(x=X_axis, y=Y_axis)
                index += 1  #iterates index of array
                X_axis += 135   #increases x axis value
            X_axis=20   #increases x axis value
            Y_axis += 140   #increases y axis value

        #buttons and labels in order of how they appear on the screen

        #button to move back a page
        back_button = tk.Button(self.gallery_frame, text='Back', width=10, height=1, command=self.decrease_image_count)
        back_button.place(x=20, y=300)

        #label to show current page
        page_label = tk.Label(self.gallery_frame, text='{} / {}'.format(self.current_page, self.max_pages), width=10, height=2)
        page_label.place(x=250, y=300)

        #button to move to next page
        next_button = tk.Button(self.gallery_frame, text='Next', width=10, height=1, command=self.increase_image_count)
        next_button.place(x=490, y=300)

        if self.current_page == 1:      #enables and disables buttons where necessary
            back_button['state'] = tk.DISABLED
        else:
            back_button['state'] = tk.NORMAL

        if self.current_page == self.max_pages:
            next_button['state'] = tk.DISABLED
        else:
            next_button['state'] = tk.NORMAL

    ##opens image, detects if image is of correct file type
        
    def image_preprocess(self, image_file):

        path = image_file
        try:    #exception handling to ensure the correct image format is being inputted
            open_image = Image.open(path)
            width, height = open_image.size
            if width >= 64 and height >= 64:    #checks image dimensions are within accepted range
                if open_image.size != (64, 64):
                    open_image = open_image.resize((64, 64))    #resizes image to be compatible with model
                return open_image

            else:
                #creates GUI error message if image is too small
                error_popup('Image is too small \n {}'.format(path))    #checks whether image is large enough to be classified
                self.path = ''
                self.display_images()   #displays images

        except KeyboardInterrupt:
            pass

        except:
            error_popup('Invalid file type \n {}'.format(path))   #returns error popup message if the file type is not supported
            self.path = ''
            self.display_images()   #displays images

    ##Method for main class to show user history window

    def show_history(self):

        self.frame_manager.show_window(2)

    ##Method for main class to show user save library window

    def show_save_window(self):

        self.frame_manager.show_window(3)

    ##Method to return predictions for image labels, returns nothing if the user hasn't requested prediction

    def show_predictions(self, index):

        if self.active_prediction:

            specific_prediction = self.predictions[index]   #returns individual prediction

            return specific_prediction
        else:
            return ""

    ##Method to retrieve predicitons from model class by passing array of image paths

    def get_predictions(self, images):

        #creates an instance with the prediction class
        prediction_instance = model.prediction('model', images, self.current_working_dir)
        predictions = prediction_instance.predict_Images()  #runs method to predict images, returns array of predictions
        return predictions

    ##Converts predictions from model output text to simplified text for user

    def prepare_predictions(self):
        
        self.predictions = self.get_predictions(self.image_paths)   #gets array of predictions

        for i in range(len(self.predictions)):
            #normalises data to show within GUI
            adjusted_prediction = self.predictions[i]
            adjusted_prediction = adjusted_prediction.strip('\n')
            adjusted_prediction = adjusted_prediction.split(',')
            adjusted_prediction = adjusted_prediction[0]
            self.predictions[i] = adjusted_prediction

        self.active_prediction = True   #sets varible to True to display predictions in GUI
        self.display_images()   #reloads images with predicted labels
        self.save_button['state'] = tk.NORMAL   #allows the user to save library
    
    ##Getter method for prediction variable

    def return_predictions(self):

        return self.predictions

    ##Getter method for image paths

    def return_paths(self):

        return self.image_paths

##Class which handles user input for saving the libary

class save_library(tk.Frame):

    ##Method for initialising varibles and GUI for class

    def __init__(self, parent, prediction_instance):    #instance of main window class passed through to return prediction results
        tk.Frame.__init__(self, parent)

        self.frame_manager = parent

        #GUI initialisers

        self.config(width=600, height=650, bg='#3d3d3d')

        self.title = tk.Label(self, text='Save Library')    #title of frame
        self.title.config(font=('Monaco', 28), bg='#3d3d3d', fg='white')
        self.title.place(x=20, y=20)

        #button to go back to main window
        self.home_button = tk.Button(self, text='Home', width=30, height=1, command=self.go_home)
        self.home_button.place(x=190, y=600)

        #button to enter to save library
        self.enter_button = tk.Button(self, text='Enter', width=30, height=1, command=self.save_library)
        self.enter_button.place(x=190, y=565)

        #creates sub heading within frame
        self.sub_heading = tk.Label(self, text='Please enter the name for your library', font=('Monaco', 14), bg='#3d3d3d', fg='white')
        self.sub_heading.place(x=190, y=250)

        #text box for library name
        self.library_name_entry = tk.Entry(self)
        self.library_name_entry.place(x=220, y=300)

        #creates instance with prediciton class
        self.prediction_instance = prediction_instance

    ##Method to save library using sql class

    def save_library(self):

        library_name = self.library_name_entry.get()    #gets the text from the text box
        #using getter methods for main window frame class
        predictions = self.prediction_instance.return_predictions()
        image_paths = self.prediction_instance.return_paths()

        sql_instance = sql.database('datastore.db')   #creates instance for sql class
        sql_instance.insert_New_Library(library_name, image_paths, predictions)
        sql_instance.complete(True)

        self.go_home()    #Returns the user back to main window
        
    ##Method to show the user the main window

    def go_home(self):

        self.library_name_entry.delete(0, 'end')    #clears text box
        self.frame_manager.show_window(1)   #shows the main window


##Class to display previous results from SQLite database

class results_lookup_window(tk.Frame):

    ##Method for initialising class attributes

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.frame_manager = parent

        #initialising variables
        self.max_pages = 0
        self.current_page = 1
        self.current_index = 0
        self.current_ID = 0
        self.search_layer = 'library'

        #Gui intialisations

        self.config(width=600, height=650, bg='#3d3d3d')

        self.title = tk.Label(self, text='Past Result History') #sets title of frame
        self.title.config(font=('Monaco', 28), bg='#3d3d3d', fg='white')
        self.title.place(x=20, y=20)

        #button to refresh list of libraries
        self.refresh_button = tk.Button(self, text='Refresh', width=30, height=1, command=self.get_library_names)
        self.refresh_button.place(x=190, y=565)

        #button to go back to main window
        self.home_button = tk.Button(self, text='Home', width=30, height=1, command=self.go_home)
        self.home_button.place(x=190, y=600)

        #label to display information for end user
        self.user_entry_label = tk.Label(self, text='Please type in your choice', font=('Monaco', 14), bg='#3d3d3d', fg='white')
        self.user_entry_label.place(x=200, y=490)

        #text box to enter users choice
        self.user_entry = tk.Entry(self)
        self.user_entry.place(x=190, y=520)

        #button to enter the users choice
        self.user_entry_button = tk.Button(self, text='Enter', width=5, height=1, command=self.choose_search)
        self.user_entry_button.place(x=400, y=520)

        #button to delete users choice
        self.user_delete_button = tk.Button(self, text='Delete', width=5, height=1, command=self.delete_Library)
        self.user_delete_button.place(x=470, y=520)

        #frame to hold queries from database
        self.information_frame = tk.Frame(self, width=580, height=350, bg='#6e6e6e')
        self.information_frame.place(x=10, y=110)

        self.sql_query = sql.database('datastore.db')   #creates instance for sql class

        self.data = []  #array to hold objects of libraries, categories and images
        self.get_library_names()    #runs method to get all libraries
        self.show_menu()    #runs method to show the menu of libraries
        
    ##Method to reset widgets to prevent constant overlapping

    def refresh(self):

        self.information_frame.destroy()    #destroys all widgets within the information sub frame

        self.max_pages = len(self.data) / 5 #calculates max number of pages
        if self.max_pages % 5 == 0:
            pass
        else:
            self.max_pages = math.ceil(self.max_pages)  #rounds the number of max pages up

        self.information_frame = tk.Frame(self, width=580, heigh=350, bg='#6e6e6e') #creates new frame
        self.information_frame.place(x=10, y=110)
        self.show_menu()    #shows the menu of libraries

    ##Method to switch between retrieving categories of a library and retrieving photos of each category

    def choose_search(self):

        #if statements to select whether to show list of libraries, categories or photos
        if self.search_layer == 'library':
            self.get_Categories()

            if self.data == []:
                pass
            else:
                self.search_layer = 'category'

        elif self.search_layer == 'category':
            self.get_Photos()

            if self.data == []:
                pass
            else:
                self.search_layer = 'photo'

        else:
            pass

        self.user_entry.delete(0, 'end')    #deletes any text within text box

    ##Method to retrieve libraries from database and add to the data array

    def get_library_names(self):

        self.data = []  #reinitialises array to empty it

        for item in self.sql_query.get_All_Libraries(): #retrieves all libraries using SQL.py import
            
            self.data.append(item)  #appends each library object

        self.max_pages = len(self.data) / 5   #creates the maximum number of pages
        if self.max_pages % 5 == 0:
            pass
        else:
            self.max_pages = math.ceil(self.max_pages)  #rounds up using math library

        self.refresh()    #refreshes to update GUI

    ##Method to delete a library if the user no longer requires it to be stored in the database

    def delete_Library(self):

        libraryID = self.user_entry.get()
        self.sql_query.delete_Library(libraryID)    #uses sql.py import to delete library from database

        self.refresh()  #refreshes frame

    ##Method to retrieve all the libraries from the sql class surrounding libraryID

    def get_Categories(self):

        self.data = []  #reinitialises data array to empty it

        libraryID = self.user_entry.get()   #retrieves entry from user text box
        self.current_ID = libraryID     #saves for the libraryID
        categories = self.sql_query.get_Categories(libraryID)   #uses sql.py file to get all categories, returns array
        for item in categories:
            self.data.append(item)  #appends category objects
            
        if self.data == []:
            error_popup('No library exists with this value')
        else:

            self.refresh_button['state'] = tk.DISABLED  #disables buttons since they are no longer necessary
            self.user_delete_button['state'] = tk.DISABLED

            self.refresh()  #refreshes frame

    ##Method to retrieve all photos for specific categoryID

    def get_Photos(self):

        self.data = []  #reinitialises data array to empty it

        categoryID = self.user_entry.get()  #gets user entry from text box
        photos = self.sql_query.get_Photos(self.current_ID, categoryID) #uses sql.py file to get all photos
        
        for item in photos:
            self.data.append(item)  #appends photo object

        if self.data == []:
            error_popup('No photos exist in this category')
        else:

            self.information_frame.destroy()    #destroys all widgets within frame

            self.max_pages = len(self.data) / 8 #finds maximum amount of pages
            if self.max_pages % 8 == 0:
                pass
            else:
                self.max_pages = math.ceil(self.max_pages)  #rounds value up

            self.information_frame = tk.Frame(self, width=580, heigh=350, bg='#6e6e6e') #creates frame to hold sql queries
            self.information_frame.place(x=10, y=110)


            self.current_index = 0  #resets current index value for array
            self.current_page = 1   #resets current page value
            self.show_photos()  #shows the photos

    ##Method to show the photos for each category that the user requests

    def show_photos(self):

        X_axis=20   #sets initial x axis value
        Y_axis=10   #sets initial y axis value
        index = self.current_index

        #iterates over a range of 4 inside a range of 2
        for i in range(2):
            for j in range(4):
                try:    #exception handling to fill in blank space of array index does not exist
                    filepath = self.data[index].get_Filename()
                    opened_image = Image.open(filepath)
                    opened_image = opened_image.resize((96, 96))    #resizes image to larger size for easier viewing
                    img = ImageTk.PhotoImage(opened_image)
                    img_container = tk.Label(self.information_frame, image=img, width=125, height=125)
                    img_container.img = img
                    img_container.place(x=X_axis, y=Y_axis)   #places container in set x and y coordinates
                except IndexError as err:
                    blank_space = tk.Frame(self.information_frame, width=125, height=125, bg='white')
                    blank_space.place(x=X_axis, y=Y_axis)
                index += 1    #iterates index
                X_axis += 135   #iterates x coordinate
            X_axis += 20    #iterates x coordinate
            Y_axis += 140   #iterates y coordinate

        #creates buttons for user navigation
    
        #button used for moving back a page
        back_button = tk.Button(self.information_frame, text='Back', width=10, height=1, command=self.decrease_page_count)
        back_button.place(x=20, y=300)

        #label used for displaying current page
        page_label = tk.Label(self.information_frame, text='{} / {}'.format(self.current_page, self.max_pages), width=10, height=2)
        page_label.place(x=250, y=300)

        #button used for moving to the next page
        next_button = tk.Button(self.information_frame, text='Next', width=10, height=1, command=self.increase_page_count)
        next_button.place(x=490, y=300)

        #enables and disables buttons depending on maximum pages

        if self.current_page == 1 or self.max_pages == 0.0:
            back_button['state'] = tk.DISABLED
        else:
            back_button['state'] = tk.NORMAL

        if self.current_page == self.max_pages or self.max_pages == 0.0:
            next_button['state'] = tk.DISABLED
        else:
            next_button['state'] = tk.NORMAL

    ##Method for displaying menu items for libraries and categories

    def show_menu(self):

        y_axis=30   #sets initia; y axis value

        for i in range(self.current_index, self.current_index+5):   #iterates through range of 5

            try:
                data = self.data[i].get_Data()    #retrieves data and id from arrray of objects
                id = self.data[i].get_ID()

                text = '{}  {}'.format(id, data)    #puts id and data into string

                label = tk.Label(self.information_frame, text=text, width=50, height=2) #creates label from text data
                label.place(x=60, y=y_axis)

            except IndexError as err:   #ignores index out of range error
                pass    #displays nothing if object does not exist

            y_axis += 50    #iterates y axis

        #creates buttons for user navigation

        #button used for moving back a page
        back_button = tk.Button(self.information_frame, text='Back', width=10, height=1, command=self.decrease_page_count)
        back_button.place(x=20, y=300)

        #label used for displaying current page
        page_label = tk.Label(self.information_frame, text='{} / {}'.format(self.current_page, self.max_pages), width=10, height=2)
        page_label.place(x=250, y=300)

        #button used for moving to the next page
        next_button = tk.Button(self.information_frame, text='Next', width=10, height=1, command=self.increase_page_count)
        next_button.place(x=490, y=300)

        #enables and disables buttons where necessary
        if self.current_page == 1 or self.max_pages == 0.0:
            back_button['state'] = tk.DISABLED
        else:
            back_button['state'] = tk.NORMAL

        if self.current_page == self.max_pages or self.max_pages == 0.0:
            next_button['state'] = tk.DISABLED
        else:
            next_button['state'] = tk.NORMAL

    ##Method to increase the page count

    def increase_page_count(self):

        if self.current_page == self.max_pages: #condition if current page is last page
            pass
        else:
            self.current_page += 1

            if self.search_layer == 'photo':    #increases count by 8 if displaying photos
                self.current_index += 8
            else:
                self.current_index += 5    #increases count by 5 if displaying libraries or categories

        self.refresh()  #refreshes menu

    ##Method to decrease the page count

    def decrease_page_count(self):
        
        if self.current_page - 1 == 0:  #condition if current page is first page
            pass
        else:
            self.current_page -= 1

            if self.search_layer == 'photo':    #decreases the count by 8 if displaying photos
                self.current_index -= 8
            else:
                self.current_index -=5    #decreases the page count by 6 if displaying libraries or categories

        self.refresh()

    ##Method to take the user back to the main window, additionally refreshes the save window

    def go_home(self):

        self.data = []  #reinitialises data array to empty it
        self.refresh()  #refreshes menu frame
        self.get_library_names()    #shows names of libraries
        self.search_layer = 'library'   #goes back to library search
        self.user_entry.delete(0, 'end')    #deletes user text box entry
        self.refresh_button['state'] = tk.NORMAL    #resets buttons back to normal state
        self.user_delete_button['state'] = tk.NORMAL
        self.frame_manager.show_window(1)   #shows the main window

##popup error message

class error_popup(tk.Toplevel):

    def __init__(self, message):
        tk.Toplevel.__init__(self)  #acts as top level frame to appear over current frame

        self.geometry('500x50') #sets size of window
        self.label = tk.Label(self, text=str(message), fg='red')    #sets text colour and output
        self.label.place(x=0, y=0) 

        


app = imageSort()
app.mainloop()








































