import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
def loadgeneratedTrafficData():
    data = np.loadtxt(open('result.csv', 'rb'), delimiter=',')
    x = data[:, 0:3]
    y = data[:, 3]
    return x,y


def splitTestAndTrainData(x, y,testDataSize):
    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state = 0, test_size = testDataSize)
    return x_train,x_test,y_train,y_test

def computeAccuracyScore(y_test, classifier_predictions):
    accuracySocre = accuracy_score(y_test, classifier_predictions)*100
    print("Accuracy score is", accuracySocre)