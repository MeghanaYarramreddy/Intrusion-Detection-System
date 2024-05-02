import argparse
import numpy as np

def getCommandLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--traning_data', help = 'Training data', required = True)
    parser.add_argument('-v' , '--testing_data', help = 'Testing data', required = True)
    return vars(parser.parse_args())
def getDataDetails(csv_data):
    data = np.genfromtxt(csv_data, delimiter = ",")
    features = data[:, [0,1,2]]
    labels = data[:, 3]
    return features, labels

def getAccuracy(real_labels, predicted_labels, fltr):
    realAttackCount = 0.0
    PredictedAttackCount = 0.0

    for real_label in real_labels:
            if real_label == fltr:
                realAttackCount += 1
    for predicted_label in predicted_labels:
            if predicted_label == fltr:
                    PredictedAttackCount +=1
    print("Real number of attacks: " + str(realAttackCount))
    print("Predicted number of attacks: " + str(PredictedAttackCount))
    precision = PredictedAttackCount * 100 / realAttackCount
    return precision 