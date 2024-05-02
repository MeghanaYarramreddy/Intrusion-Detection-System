from __future__ import division

import numpy
from sklearn import svm

class SVM:

     def __init__(self):
        """
        train the model from generated training data
        """
        data = numpy.loadtxt(open('result.csv', 'rb'), delimiter=',', dtype='str')
        #Support_Vector_Machine
        self.svm = svm.SVC()
        self.svm.fit(data[:, 0:3], data[:, 3])


     def classify(self, data):
            functionalParams = numpy.zeros((1,3))
            functionalParams[:,0] = data[0]
            functionalParams[:,1] = data[1]
            functionalParams[:,2] = data[2]
            prediction = self.svm.predict(functionalParams)
            print("SVM input data", data, "prediction result", prediction)
            return prediction
