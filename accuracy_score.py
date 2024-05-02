import accuracy_utils
from sklearn import svm
from sklearn.model_selection import cross_val_score

#step1: Load the data in numpy array
x, y = accuracy_utils.loadgeneratedTrafficData()

#step2: Split the generated traffic to test  &  training data. 
testDataSize = 0.25         # Test-size is 0.25(25%) of data
x_train, x_test, y_train, y_test = accuracy_utils.splitTestAndTrainData(x, y,testDataSize)

#step3: SVM machine learning algorithm

linearKernal = "linear"
svmClassification = svm.SVC(kernel=linearKernal,C=0.025)

#step4: train the SVM ML Algo with training data
svmClassification.fit(x_train, y_train)

#step5: pass the test data for classify or predict
classifier_predictions = svmClassification.predict(x_test)

#step6: compute the accuracy from the prediction result.
accuracy_utils.computeAccuracyScore(y_test, classifier_predictions)

#step7. compute cross validation score
cross_validation_score = cross_val_score(svmClassification, x_train, y_train, cv=5)
print("cross-validation score is",cross_validation_score.mean())
