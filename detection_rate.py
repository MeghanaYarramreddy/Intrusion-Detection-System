import accuracy_utils
from sklearn import svm

#step1: Load the data in numpy array
x, y = accuracy_utils.loadgeneratedTrafficData()

#step2: Split the generated traffic to test  &  training data. 
testDataSize = 0.25         # Test-size is 0.25(25%) of data
x_train, x_test, y_train, y_test = accuracy_utils.splitTestAndTrainData(x, y,testDataSize)

#step3: SVM machine learning algorithm
clf = svm.SVC()

#step4: Train the SVM ML Algo with training data
clf.fit(x_train, y_train)

#step5: Pass the test data for classify or predict
classifier_predictions = clf.predict(x_test)


#step6. Calculate the Detection Ratio
print("Calculating Detection Ratio & False")
length = len(y_test)
DD = 0
DN = 0
FD = 0
TN = 0
for i in range(0,length):
    if y_test[i] == 1.0:
        if classifier_predictions[i] == 1.0:
            DD = DD + 1
        else:
            DN = DN + 1
    #calculating False alarm rate
    if y_test[i] == 0.0:
        if classifier_predictions[i] == 1.0:
            FD = FD + 1
        else:
            TN = TN + 1
DETECTION_RATE = DD / (DD + DN)
print("Detection Rate ", DETECTION_RATE) 
FALSE_ALARM_RATE = FD / (FD + TN)
print("False Alarm Rate", FALSE_ALARM_RATE)