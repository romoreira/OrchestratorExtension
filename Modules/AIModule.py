'''
Created on Jun 18, 2018

@author: rodrigo
'''

#Classes:
#1 - Audio
#2 - Browsing
#3 - CHAT
#4 - FILE-TRANSFER
#5 - MAIL
#6 - P2P
#7 - VIDEO
#8 - VOIP


import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.utils.validation import column_or_1d
from sklearn import metrics

from sklearn import svm, datasets
from sklearn.svm.libsvm import decision_function

def nmae(y_real, y_predict):

    #Reset Panda Data frame settings
    y_real = pd.DataFrame(y_real)
    y_predict = pd.DataFrame(y_predict)

    
    #Loop - Variables Initializing
    somatorio = 0.0
    m = 0
    media = 0
    nmae_resultado = 0
    for m in range(len(y_real)):
        somatorio += abs((y_real.iloc[m][0] - y_predict.iloc[m]))
        m += 1

    #Final adjustments
    media = y_real.iloc[:, y_real.columns == "class"].astype(float).mean()
    media = media[0]
    somatorio = somatorio[0]


    #N. M. A. E. Accuracy Measures
    nmae_resultado = (somatorio/m)/media

    return nmae_resultado


#Preparing X and Y to be trained
df = pd.read_csv('/home/rodrigo/MPLS-TE/Data-Set/cic-unb/merged_5s.csv')
x = df.iloc[:,0:28]


#Remove String format from training model
x = x.iloc[:,x.columns != "Source_IP"]
x = x.iloc[:,x.columns != "Destination_IP"]


y = df.iloc[:,29:30]

x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.30)

#y_train must be 1d column
y_train = column_or_1d(y_train, warn=False)


#Creating a Regression Object
C = LogisticRegression()

#Fit Model
C.fit(x_train,y_train)

#Perform a classification test by using Logistic Regression
y_pred = C.predict(x_test)

# y_pred_class = pd.DataFrame(y_pred_class)
print("Accuracy of the Classifier C = %.3f" % metrics.accuracy_score(y_test, y_pred))

#Print Coeficients of Regression
#print("Coeficients: " + np.array2string(C.coef_))


#Regression Method
print("The Normalized Mean Absolute Error (Regression Method): %0.4f " % nmae(y_test, y_pred))



#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#Test using IRIS data set
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#


iris = datasets.load_iris()
#print(iris)
X = iris.data[:, :2]
y = iris.target

x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
h = (x_max / x_min)/100
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
 np.arange(y_min, y_max, h))


X_plot = np.c_[xx.ravel(), yy.ravel()]

print(X.shape)
print(y.shape)

# Create the SVC model object
C = 1.0 # SVM regularization parameter
svc = svm.SVC(kernel='linear', C=C, decision_function_shape='ovr').fit(X, y)
Z = svc.predict(X_plot)
print("Z Predicted")
print(Z)


#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#

#Preparing X and Y to be trained
df = pd.read_csv('/home/rodrigo/MPLS-TE/Data-Set/cic-unb/test.csv')
x = df.iloc[:,0:28]


#Remove String format from training model
x = x.iloc[:,x.columns != "Source_IP"]
x = x.iloc[:,x.columns != "Destination_IP"]


y = df.iloc[:,29:30]

x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.30)



print(x_train.shape)
x_train = np.array(x_train)

y_train = column_or_1d(y_train, warn=False)
print(y_train.shape)

# Create the SVC model object
C = 1.0 # SVM regularization parameter
svc = svm.SVC(kernel='linear', C=C, decision_function_shape='ovr').fit(x_train, y_train)
Z = svc.predict(X_plot)


#Preparing X and Y to be trained
df = pd.read_csv('/home/rodrigo/MPLS-TE/Data-Set/cic-unb/merged_5s.csv')
x = df.iloc[:,0:28]


#Remove String format from training model
x = x.iloc[:,x.columns != "Source_IP"]
x = x.iloc[:,x.columns != "Destination_IP"]


y = df.iloc[:,29:30]

x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.30)

#y_train must be 1d column
y_train = column_or_1d(y_train, warn=False)


#Creating a Regression Object
C = LogisticRegression()

#Fit Model
C.fit(x_train,y_train)

#Perform a classification test by using Logistic Regression
y_pred = C.predict(x_test)

# y_pred_class = pd.DataFrame(y_pred_class)
print("Accuracy of the Classifier C = %.3f" % metrics.accuracy_score(y_test, y_pred))

#Print Coeficients of Regression
#print("Coeficients: " + np.array2string(C.coef_))


#Regression Method
print("The Normalized Mean Absolute Error (Regression Method): %0.4f " % nmae(y_test, y_pred))


