from utilities import *
from sklearn import tree
args = getCommandLineArgs()
traning_data = args['traning_data']
testing_data = args['testing_data']
# Get training features and labeles
training_features, traning_labels = getDataDetails(traning_data)

#Get testing features and labeles 
testing_features, testing_labels = getDataDetails(testing_data)

#decison tree classifier
print("\n\n******************* Decision Tree Classifier ******************\n\n")
#Instanciate the classifier
attack_classifier = tree.DecisionTreeClassifier()
#Train the classifier 
attack_classifier = attack_classifier.fit(training_features, traning_labels)
#Get predection  for the testing data
predictions = attack_classifier.predict(testing_features)

print("The precision of the DECISION TREE CLASSIFIER IS: " + str(getAccuracy(testing_labels, predictions, 1)) + "%")
