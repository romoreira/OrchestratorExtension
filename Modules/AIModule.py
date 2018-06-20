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
from sklearn.neighbors import KNeighborsClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.multiclass import OneVsOneClassifier
from sklearn.svm import LinearSVC

#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#Functions - NMAE
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
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
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#END of Functions
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#



#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#Test using Logistic Regression
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#


#Preparing X and Y to be trained
df = pd.read_csv('/home/rodrigo/MPLS-TE/Data-Set/cic-unb/merged_5s.csv')
x = df.iloc[:,0:28]


#Remove String format from training model
x = x.iloc[:,x.columns != "Source_IP"]
x = x.iloc[:,x.columns != "Destination_IP"]

#To catch target (class of network traffic)
y = df.iloc[:,29:30]

#Data-set train test split
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
print("Logistic Regression: Accuracy of the Classifier C = %.3f" % metrics.accuracy_score(y_test, y_pred))

#Regression Method
print("Logistic Regression: Normalized Mean Absolute Error (NMAE): %0.4f " % nmae(y_test, y_pred))



#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#Test using IRIS data set
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#

#Load IRIS dataset 
iris = datasets.load_iris()

#Catch only 2 parameters (there are two)
X = iris.data[:, :2]
y = iris.target

x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
h = (x_max / x_min)/100
xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
 np.arange(y_min, y_max, h))


X_plot = np.c_[xx.ravel(), yy.ravel()]

# Create the SVC model object
C = 1.0 # SVM regularization parameter
svc = svm.SVC(kernel='linear', C=C, decision_function_shape='ovr').fit(X, y)
Z = svc.predict(X_plot)

#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#End of IRIS data-set comparisson
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#




#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#IRIS Data-set versus Network Data-set (both has same features)
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#

#Reading Data to be trained
df = pd.read_csv('/home/rodrigo/MPLS-TE/Data-Set/cic-unb/test.csv')

#Cacth features from Test - In this case only two (to be compared with IRIS Data-set)
X = df.iloc[:,8:10]
y = df.iloc[:,29:30]

#Split data in Train and Test
x_train, x_test, y_train, y_test = train_test_split(X,y, test_size=0.30)

#Conversion into numpy array
x_train = np.array(x_train)
y_train = np.array(y_train)
y_train = column_or_1d(y_train, warn=False)

#Adjustments in numpy to keep big number format (without scientific notation)
np.set_printoptions(suppress=False,formatter={'float_kind':'{:16.5f}'.format},linewidth=130)

# Create the SVC model object
C = 1.0 # SVM regularization parameter
svc = svm.SVC(kernel='rbf', C=C, decision_function_shape='ovr').fit(x_train, y_train)

#Test using splitted data
Z = svc.predict(x_test)

#Print Accuracy of the Classifier (SVM)
print("SVM: Accuracy of the Classifier C = %.3f" % metrics.accuracy_score(y_test, Z))

#Print NAME Error measure (SVM)
print("SVM: Normalized Mean Absolute Error (NMAE): %0.4f " % nmae(y_test, Z))


#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#End of IRIS and Network Data-set compatissons
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#





#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#SVM - Network Data-set by considering all features
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#

#Preparing X and Y to be trained - 
df = pd.read_csv('/home/rodrigo/MPLS-TE/Data-Set/cic-unb/merged_5s.csv')
x = df.iloc[:,0:28]

#Remove String format from training model
x = x.iloc[:,x.columns != "Source_IP"]
x = x.iloc[:,x.columns != "Destination_IP"]

#To catch target (class of network traffic)
y = df.iloc[:,29:30]

#Data-set train test split
x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.30)

#Conversion into numpy array
x_train = np.array(x_train)
y_train = np.array(y_train)
x_test = np.array(x_test)
y_test = np.array(y_test)
y_train = column_or_1d(y_train, warn=False)

#Adjustments in numpy to keep big number format (without scientific notation)
np.set_printoptions(suppress=False,formatter={'float_kind':'{:16.5f}'.format},linewidth=130)

y_pred = OneVsRestClassifier(LinearSVC(C=100.)).fit(x_train, y_train).predict(x_test)
y_pred2 = OneVsOneClassifier(LinearSVC(C=100.)).fit(x_train, y_train).predict(x_test)

print("\nLarge Data:\nSVM: Accuracy of the Classifier C = %.3f " % metrics.accuracy_score(y_test, y_pred))
print("\nLarge Data:\nSVM2: Accuracy of the Classifier C = %.3f " % metrics.accuracy_score(y_test, y_pred2))


# Create the SVC model object
C = 1.0 # SVM regularization parameter
svc = svm.SVC(kernel='linear', C=C, decision_function_shape='ovr').fit(x_train, y_train)
Z = svc.predict(x_test)

print(Z)
np.savetxt('svm1.txt', y_pred, delimiter=',')
np.savetxt('svm2.txt', y_pred2, delimiter=',')


#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
#KNN
#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#

#Preparing X and Y to be trained - 
df = pd.read_csv('/home/rodrigo/MPLS-TE/Data-Set/cic-unb/merged_5s.csv')
x = df.iloc[:,0:28]

#Remove String format from training model
x = x.iloc[:,x.columns != "Source_IP"]
x = x.iloc[:,x.columns != "Destination_IP"]

#To catch target (class of network traffic)
y = df.iloc[:,29:30]

#Data-set train test split
x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.30)


#Conversion into numpy array
x_train = np.array(x_train)
y_train = np.array(y_train)
#y_test = np.array(y_test)
y_train = column_or_1d(y_train, warn=False)

#Adjustments in numpy to keep big number format (without scientific notation)
np.set_printoptions(suppress=False,formatter={'float_kind':'{:16.5f}'.format},linewidth=130)

neigh = KNeighborsClassifier(n_neighbors=3)
neigh.fit(x_train,y_train)

y_pred = neigh.predict(x_test)

np.savetxt('knn.txt', y_pred, delimiter=',')

print("\nLarge Data:\nKNN: Accuracy of the Classifier C = %.3f " % metrics.accuracy_score(y_test, y_pred))

#Print NAME Error measure (SVM)
print("KNN: Normalized Mean Absolute Error (NMAE): %0.4f " % nmae(y_test, y_pred))