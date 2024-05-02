
from __future__ import division


import matplotlib.pyplot as plt
import numpy as np
from mlxtend.plotting import plot_decision_regions
from sklearn import svm

data = np.loadtxt(open('result.csv', 'rb'), delimiter= ',')

#sfe,ssip,rfip
sfe = 0
ssip = 1
rfip = 2
sfe_ssip_pair = [sfe,ssip]
sfe_rfip_pair = [sfe,rfip]

#Graph1 sfe & ssip
def generateGraphs(data,graph_pair,graphTitle,xAxisLabel,yAxisLabel,fileName):
   
    X = data[:, graph_pair]
    y = data[:, 3]
    clf = svm.SVC()
    clf.fit(X, y)
    # Plot Decision Region using mlxtend's awesome plottiog function 
    fig = plt.figure(figsize=(10,8))
    fig = plot_decision_regions(X=X,
                      y=y.astype(int),
                      clf=clf,
                      legend=2)
    plt.title(graphTitle, size=16)
   
    plt.xlabel(xAxisLabel)
 
    plt.ylabel(yAxisLabel)
    plt.savefig(fileName)

graphTitle = 'SVM DDOS  - Decision Region Boundary'
xAxisLabel = 'Speed of Flow Entry'
yAxisLabel = 'Speed of Source IP'
fileName = "svm_graph1.png"
generateGraphs(data,sfe_ssip_pair,graphTitle,xAxisLabel,yAxisLabel,fileName)


graphTitle = 'SVM DDOS  -  Decision Region Boundary'
xAxisLabel = 'sfe'
yAxisLabel = 'rfip'
fileName = "svm_graph2.png"
generateGraphs(data,sfe_rfip_pair,graphTitle,xAxisLabel,yAxisLabel,fileName)
