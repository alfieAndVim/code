import sqlite3 as sql
from tkinter.constants import TRUE
import os
import Pre_Processing as pp

##Class for database handling

class database:

    ##Method for initialising attributes for database class

    def __init__(self, database):
        self.database_name = database
        self.database_path = '{}{}{}'.format(os.getcwd(), '/', self.database_name)  #creates full directory for database

        self.create_Tables_condition = False    #sets condition to false to indicate that tables do not need to be created
        self.cwd = '{}{}'.format(os.getcwd(), '/')    #works out whether database already exists
        files = os.listdir(self.cwd)    #lists all files in current working directory
        if self.database_name not in files: #checks whether the database is contained within the list of files
            self.create_Tables_condition = True #sets condition to create tables

        self.conn = sql.connect(self.database_path)   #connects to database, creates database if it does not exist
        self.cursor = self.conn.cursor()    #sets cursor for database

        if self.create_Tables_condition:    #will create tables in database if it does not already exist
            self.create_Tables()    #calls method to create database tables

    ##Method for committing the cursor execution and closes connection where necessary

    def complete(self, close):
        self.conn.commit()  #commits execution

        if close:
            self.conn.close()   #closes connection to database

    ##Method for creating tables for database if it does not already exist

    def create_Tables(self):    #creates the library table to store every library the user creates
        self.conn.execute('''
            CREATE TABLE libraryTable
            (libraryID INTEGER PRIMARY KEY,
            libraryName TEXT NOT NULL,
            noOfPhotos INTEGER NOT NULL)
        ''')

        #creates the category table to store every category that can used for classification
        self.conn.execute('''
            CREATE TABLE categoryTable
            (categoryID INTEGER PRIMARY KEY,
            categoryName TEXT NOT NULL,
            noOfPhotosInCat INTEGER NOT NULL)
        ''')

        #creates the photo table to store every photo of every library
        self.conn.execute('''
            CREATE TABLE photoTable
            (photoID PRIMARY KEY,
            filename TEXT NOT NULL,
            categoryID INTEGER,
            libraryID INTEGER,
            FOREIGN KEY (categoryID) REFERENCES categoryTable (categoryID),
            FOREIGN KEY (libraryID) REFERENCES libraryTable (libraryID))
        ''')

        #creates list of categories and inserts into categoryTable

        data_instance = pp.data_manager()   #creates instance with data manager class
        categories = data_instance.return_Categories()  #calls return_Categories method in order to get list of all categories

        id = 0  #initially sets id to 0

        #iterates over categories array
        for item in categories:

            #execution to create a category entity for every item in categories array
            self.conn.execute('''
                INSERT INTO categoryTable(categoryID, categoryName, noOfPhotosInCat)
                VALUES("{}","{}","{}")
            '''.format(id, item, 0))

            self.complete(False)    #commits execution but does not close connection

            id += 1 #iterates id variable

    ##Method to insert a new library into the database

    def insert_New_Library(self, libraryName, imagePaths, Predictions):

        last_libraryID = self.get_Last_Library_ID()   #gets the most recent library and photo table id
        last_photoID = self.get_Last_Photo_ID()

        libraryID = last_libraryID + 1    #creates the next id for the table for both libraries and photos
        photoID = last_photoID + 1

        photo_number = len(imagePaths)  #calculates the amount of images in the library

        self.insert_Into_Libraries(libraryID, libraryName, photo_number)    #inserts new library

        for i in range(photo_number):
            category = Predictions[i]   #gets prediction specific to each image
            categoryID = self.get_Category_ID(category) #gets the categoryID associated with the category

            self.insert_Into_Photos(photoID, imagePaths[i], categoryID, libraryID)  #inserts new photo

            photoID += 1    #iterates photoID

        data_instance = pp.data_manager()   #creates instance of data_manager class
        categories = data_instance.return_Categories()  #gets all categories of dataset

        category_amounts = {}   #dictionary to hold the category(key) and the amount of times the category occurs in the library

        for category in categories:

            category = category.split(',')  #splits category names up by ','
            category = category[0]  #takes the first part of each category name

            occurences = Predictions.count(category)    #counts the occurences of each category in returns category array
            
            category_amounts[category] = occurences #creates new key value pair for occurences dictionary
        for category, occurence in category_amounts.items():    #iterates over dictionary
            categoryID = self.get_Category_ID(category) #gets categoryID of each category name
            self.adjust_Category_Count(categoryID, occurence)   #adjusts the number of photos in each category in database


    ##Method to insert a new photo into the photo database table

    def insert_Into_Photos(self, photoID, filename, categoryID, libraryID):

        #inserts a new photo entity into photoTable
        self.conn.execute('''
            INSERT INTO photoTable(photoID, filename, categoryID, libraryID)
            VALUES(?,?,?,?)
        ''',(int(photoID),filename,int(categoryID),int(libraryID)))

        self.complete(False)    #commits execution without closing connection
   
    ##Method to insert a new library into the library database table

    def insert_Into_Libraries(self, libraryID, libraryName, noOfPhotos):

        #inserts new library entity into libraryTable
        self.conn.execute('''
            INSERT INTO libraryTable(libraryID, libraryName, noOfPhotos)
            VALUES(?,?,?)
        ''',(int(libraryID),libraryName,int(noOfPhotos)))

        self.complete(False)    #commits execution without closing connection

    ##Method to adjust the number of photos in each category

    def adjust_Category_Count(self, categoryID, value_change):

        #fetches the number of photos for a specific category
        self.cursor.execute('''
            SELECT noOfPhotosInCat FROM categoryTable WHERE categoryID={}
        '''.format(categoryID))

        value = self.cursor.fetchall()  #gets the associated value from cursor execution

        self.complete(False)    #commits execution without closing connection

        
        value = value[0]    #normalises the data to allow for the value variable to be used as an integer
        value = str(value)  #gets string data type from integer
        value = value.replace('(','').replace(')','').replace(',','')   #removes aspects of tuple string
        value = int(value)  #gets integer value from original tuple
        value = value + value_change    #increases value by defined amount

        #updates the number of photos in specific category
        self.cursor.execute('''
            UPDATE categoryTable SET noOfPhotosInCat={} WHERE categoryID={}
        '''.format(value, categoryID))

        self.complete(False)    #commits execution without closing connection
        
    ##Method to query for all of the libraries in the database

    def get_All_Libraries(self):

        libraries = []  #empty array for libraries to be appended to

        #select every item from libraryTable
        self.cursor.execute('''
            SELECT * FROM libraryTable
        ''')

        rows = self.cursor.fetchall()   #assigns queried data to array

        #iterates over query
        for item in rows:
            libraryID, libraryName, noOfPhotos = item   #splts tuple values
            library_object = library(libraryID, libraryName, noOfPhotos)    #creates library object
            libraries.append(library_object)    #appends library object to libraries array
        return libraries    #returns array

    ##Method to delete the library from the database

    def delete_Library(self, libraryID):

        all_photos = self.get_All_Photos(libraryID)   #retrieves all images from the library
        categories = [] #empty array to store all categories

        #iterates over each photo in library
        for photo in all_photos:
            category = photo.get_Category() #gets the category from photo object
            categories.append(category) #appends each category to categories array

        category_occurences = {}    #dictionary to hold occurences of each category

        #iterates over categories array
        for category in categories:
            occurence = categories.count(category)  #counts amount of time each category occurs in categories array
            category_occurences[category] = occurence   #create new key value pair for each category and the amount of times it occurs

        #deletes library with matching libraryID
        self.cursor.execute('''
            DELETE FROM libraryTable WHERE libraryID={}
        '''.format(libraryID))

        #deletes all photos with matching libraryID
        self.cursor.execute('''
            DELETE FROM photoTable WHERE libraryID={}
        '''.format(libraryID))

        #iterates over category_occurences dictionary
        for category, occurence in category_occurences.items():

            categoryID = self.get_Category_ID(category) #gets categoryID from category name
            occurence = occurence * -1  #creates negative value to reduce number of photos in category
            self.adjust_Category_Count(categoryID, occurence)   #adjusts category count

    ##Method used to get all photos in a database with a specific libraryID

    def get_All_Photos(self, libraryID):

        photo_instances = []    #array to hold each photo object

        #gets all photos with matching libraryID
        self.cursor.execute('''
            SELECT * FROM photoTable WHERE libraryID={}
        '''.format(libraryID))

        rows = self.cursor.fetchall()   #assigns query to rows array
        
        #iterates over query array
        for photos in rows:
            photoID, filename, categoryID, libraryID = photos   #splits up tupple result
            category = self.get_Category_Name(categoryID)   #gets category name from categoryID
            photo_instance = photo(photoID, filename, category, categoryID, libraryID)    #creates an instance of the photo class

            photo_instances.append(photo_instance)    #appends the photo class instance to array

        return photo_instances  #returns array of photo objects

    ##Method used to get all photos in a database with specific libraryID and categoryID

    def get_Photos(self, libraryID, categoryID):

        photo_instances = []    #array to hold each photo object

        #query to get all photos with matching libraryID and categoryID
        self.cursor.execute('''
            SELECT * FROM photoTable WHERE libraryID={} AND categoryID={}
        '''.format(libraryID, categoryID))

        rows = self.cursor.fetchall()   #assigns query to rows array
        
        #iterates over rows array
        for photos in rows:
            photoID, filename, categoryID, libraryID = photos   #splits tupple
            category = self.get_Category_Name(categoryID)   #gets category name from categoryID
            photo_instance = photo(photoID, filename, category, categoryID, libraryID)    #creates photo class object

            photo_instances.append(photo_instance)  #appends photo class object to photo_instances array

        return photo_instances    #returns photo class objects

    ##Method used to get the categories of a specific library

    def get_Categories(self, libraryID):

        categories = [] #array to hold category objects

        add_instance = True #variable to hold condition whether to add category or not

        photos = self.get_All_Photos(libraryID) #gets all photos with speciic libraryID
        for photo in photos:
            indiv_category = photo.get_Category()   #gets each category name from photo
            category_ID = self.get_Category_ID(indiv_category)  #gets each categoryID from category name

            category_instance = category(indiv_category, category_ID)   #creates a category instance

            #iterates over categories array
            for instance in categories:
                indiv_category_id = instance.get_ID()
                if indiv_category_id == category_ID:    #only adds the category if it is not already present
                    add_instance = False
                
            if add_instance:
                categories.append(category_instance)    #appends the category instance to array
            
            add_instance = True

        return categories   #returns category objects

    ##Method to get the last libraryID

    def get_Last_Library_ID(self):

        #gets all libraryID's from libraryTable
        self.cursor.execute('''
            SELECT libraryID FROM libraryTable
        ''')

        rows = self.cursor.fetchall()   #fetches all of the id's from the libraryTable

        if rows == []:
            last_libraryID = -1 #sets last libraryID to -1 if no libraries exist
        else:
            last_libraryID = rows[-1]   #gets the last value in the list of libraryID's

        self.complete(False)    #commits execution but does not close connection

        last_libraryID = str(last_libraryID)    #normalises data to convert into int
        last_libraryID = last_libraryID.replace('(', '').replace(')', '').replace(',', '')  #removes tupple aspects of string
        last_libraryID = int(last_libraryID)    #converts to integer

        return last_libraryID   #returns the last libraryID

    ##Methods to get the last photoID

    def get_Last_Photo_ID(self):

        #queries all photoID's from photoTable
        self.cursor.execute('''
            SELECT photoID FROM photoTable
        ''')

        rows = self.cursor.fetchall()   #fetches all of the id's in th photoTable

        if rows == []:
            last_photoID = -1   #if there are no photoID's then the last photoID is set to -1
        else:
            last_photoID = rows[-1]    #fetches the last added id added to the database

        self.complete(False)    #commits execution but does not end connection

        last_photoID = str(last_photoID)    #normalises data to convert to int
        last_photoID = last_photoID.replace('(', '').replace(')', '').replace(',', '')  #removes tupple aspects of string
        last_photoID = int(last_photoID)    #converts to integer

        return last_photoID     #returns last photoID

    ##Method to get the categoryID for a category given the name of the category

    def get_Category_ID(self, categoryName):

        #queries database for categoryID and categoryName from the categoryTable
        self.cursor.execute('''
            SELECT categoryID, categoryName FROM categoryTable
        ''')

        rows = self.cursor.fetchall()   #assigns query results to rows array

        #iterates over rows array
        for category_pair in rows:
            id, name = category_pair    #splits tupple into id and name
            name = name.split(',')  #splits category name by ','
            name = name[0]  #takes first section of split
            if categoryName == name:

                return id   #returns id for matching name

    ##Method to get the category name for a category given the id of the category

    def get_Category_Name(self, categoryID):

        #queries categoryID and category name from the category table
        self.cursor.execute('''
            SELECT categoryID, categoryName FROM categoryTable
        ''')

        rows = self.cursor.fetchall()   #assigns query results to rows array

        #iterates over rows array
        for category_pair in rows:
            id, name = category_pair    #splits tupple into id and name
            name = name.split(',')  #splits category name by ','
            name = name[0]  #takes first section of split
            if categoryID == id:

                return name #returns name for matching id



##class containing single attributes specific to the library being inputted

class library:

    def __init__(self, libraryID, libraryName, NoOfPhotos):
        
        #initialisers for library class
        self.libraryID = libraryID
        self.libraryName = libraryName
        self.noOfPhotos = NoOfPhotos
        self.noOfCategories = 200

    ##Method for retrieving data about each library

    def get_Data(self):

        #creates string composed of library name and number of photos in the library
        data = '{}  -  {} photos'.format(self.libraryName, self.noOfPhotos)

        return data #returns string

    ##Method for returning the id for each library

    def get_ID(self):

        return self.libraryID   #returns the librarID

##Class containing attributes specific to each photo

class photo:

    def __init__(self, photoID, filename, category, categoryID, libraryID):

        #initialisers for photo class
        self.photoID = photoID
        self.filename = filename
        self.category = category
        self.categoryID = categoryID
        self.libraryID = libraryID

    ##Method for returning the filename and category for each photo

    def get_Data(self):

        #creates string composed of image filename and image category
        data = '{}\n{}'.format(self.filename, self.category)

        return data #returns string

    ##Method for returning the photoID for each photo object

    def get_ID(self):

        return self.photoID #returns photo id

    ##Method for returning each category name for each photo object

    def get_Category(self):

        return self.category    #returns category for photo

    ##Method for returning each filename for each photo object

    def get_Filename(self):

        return self.filename    #returns filename for photo

##Class for holding the attributes for each category

class category:

    def __init__(self, category, category_ID):

        #initialisers for category class
        self.category = category
        self.category_ID = category_ID

    ##Method for returning the category name for each category object

    def get_Data(self):

        data = self.category

        return data #returns category of category class

    ##Method for returning the categoryID for each category object

    def get_ID(self):

        return self.category_ID #returns categoryID of category class































