import Pre_Processing as pp
import Model

##Main function that is run to create preprocessed data and train model
def main():

    dataset_instance = pp.dataset_process() #creates instance of dataset_process class

    create_numpy = input('Do you need to preprocess the data?, Y for yes, N for no ')   #input statement to ask whether preprocessed data needs to be created

    if create_numpy == 'Y':

        dataset_instance.save_Data()    #runs method inside dataset_process class to create preprocessed data

    data_managing_instance = pp.data_manager()  #creates instance of data_manager class
    

    model_name = input('What would you like to call the model? ')   #input to enter model name

    data_managing_instance.load_Data()  #calls method of data_manager class to load data
    (training_images, training_labels) = data_managing_instance.return_Training()   #returns training data for model training
    (validation_images, validation_labels) = data_managing_instance.return_Validation() #returns validation data for model validation

    model_instance = Model.train(training_images, training_labels, validation_images, validation_labels)    #creates instance of train class
    model_instance.start_Training(model_name)   #starts training of model, passes in chosen model name

if __name__ == '__main__':
    main()






































    