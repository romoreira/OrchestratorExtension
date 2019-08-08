'''
Created on Jun 18, 2018

@author: Rodrigo Moreira
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

from sklearn.metrics import classification_report
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.utils.validation import column_or_1d
from sklearn import metrics
from sklearn import svm, datasets
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.cross_validation import KFold
from sklearn.feature_selection import SelectKBest
from sklearn.ensemble import ExtraTreesClassifier


#Class imports - QoS Enforcement Rest API
import threading
import json
import requests
import re
import paramiko
from flask import Flask, request, abort
from zmq.tests import test_includes

class AiCore():
    
    
    TREINED = False
 
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    #Functions - NMAE
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    def nmae(self,y_real, y_predict):
    
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
        media = y_real.iloc[:, y_real.columns == "Label"].astype(float).mean()
        media = media[0]
        somatorio = somatorio[0]
    
    
        #N. M. A. E. Accuracy Measures
        nmae_resultado = (somatorio/m)/media
    
        return nmae_resultado
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    #END of Function NMAE
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    
    
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    #LOGISTIC REGRESSION
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    
    def logistic_regression():
    
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
    #SVM - Network Data-set by considering all features
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    
    def svm_classifier(self):
    
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
        
        #TO-DO
    
    
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    #KNN
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    
    def knn_fit(self, x_train, y_train, x_test, y_test):
        neigh = KNeighborsClassifier(n_neighbors=5)
        neigh.fit(x_train,y_train)
        
        y_pred = neigh.predict(x_test)
        
       
        #np.savetxt('knn.txt', y_pred, delimiter=',')
        
        print("KNN: Accuracy of the Classifier C = %.3f " % metrics.accuracy_score(y_test, y_pred))
        print(classification_report(y_test, y_pred))
        
        self.confusion_matrix(y_test, y_pred)
        
        
        
        #Print NAME Error measure (KNN)
        #print("KNN: Normalized Mean Absolute Error (NMAE): %0.4f " % self.nmae(y_test, y_pred))
        return neigh
    
    def confusion_matrix(self, y_test,y_pred):
        print(metrics.confusion_matrix(y_test, y_pred))
        TN_VOIP, FP_VOIP, FN_VOIP, TP_VOIP, TN_NETFLIX, FP_NETFLIX, FN_NETFLIX, TP_NETFLIX, TN_CS, FP_CS, FN_CS, TP_CS, TN_TELNET, FP_TELNET, FN_TELNET, TP_TELNET = metrics.confusion_matrix(y_test, y_pred).ravel()
        
        print("TN: %d" % TN_VOIP)
        print("FP: %d" % FP_VOIP)
        print("FN: %d" % FN_VOIP)
        print("TP: %d" % TP_VOIP)
        
    
    def tree_fit(self,x_train, y_train, x_test, y_test):
        clf_gini = DecisionTreeClassifier(criterion = "gini", random_state = 100, max_depth=3, min_samples_leaf=5)
        clf_gini.fit(x_train, y_train)
        y_pred = clf_gini.predict(x_test)
        print("\nDecision Tree: Accuracy of the Classifier C is: %.3f " % metrics.accuracy_score(y_test,y_pred))
        print(classification_report(y_test, y_pred))

    def svm_fit(self,x_train, y_train, x_test, y_test):
        clf = svm.SVC(kernel='rbf')
        clf.fit(x_train, y_train)
        y_pred = clf.predict(x_test)
        print("\nSVM: Accuracy of the Classifier C is: %.3f " % metrics.accuracy_score(y_test,y_pred))
        print(classification_report(y_test, y_pred))
        
    def k_fold(self, X, y):
        X = np.array(X)
        y = np.array(y)
        kf = KFold(3, True, 1)
        
        data = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        
        for train_indices, test_indices in kf.split(data):
            print('Train: %s | test: %s' % (train_indices, test_indices))
        
        #for iteration, data in enumerate(kf, start=1):
        #    print('{!s:^9} {}'.format(iteration, data[0], data[1]))
        
        
    def classifiers(self):
        
    
        #Preparing X and Y to be trained - 
        #df = pd.read_csv('/home/rodrigo/MPLS-TE/Data-Set/cic-unb/ds_80_features.csv')
        df = pd.read_csv('/home/rodrigo/MPLS-TE/Data-Set/IJUGC/Traffic_Merge.csv', sep=';')
        x = df.iloc[:,0:84]

        #Remove String format from training model
        x = x.iloc[:,x.columns != "Src IP"]
        x = x.iloc[:,x.columns != "Dst IP"]
        x = x.iloc[:,x.columns != "Timestamp"]
        x = x.iloc[:,x.columns != "Flow ID"]
        x = x.iloc[:,x.columns != "Label"]#Remove the target columns
        
        #To catch target (class of network traffic)
        y = df.iloc[:,83:84]
        
        #Data-set train test split
        x_train, x_test, y_train, y_test = train_test_split(x,y, test_size=0.30)
  
        #Conversion into numpy array
        x_train = np.array(x_train)
        y_train = np.array(y_train)
        #y_test = np.array(y_test)
        y_train = column_or_1d(y_train, warn=False)
        
        
        
        #Adjustments in numpy to keep big number format (without scientific notation)
        np.set_printoptions(suppress=False,formatter={'float_kind':'{:16.5f}'.format},linewidth=130)
        
        self.knn_fit(x_train, y_train, x_test, y_test)
        self.tree_fit(x_train, y_train, x_test, y_test)
        
        #---KNN---#
        x = np.array(x)
        y = np.array(y)
        print(x.shape)
        neigh = KNeighborsClassifier(n_neighbors=5)
        kf = KFold(len(y), n_folds=10)
        scores = []
        for train_index, test_index in kf:
            #print("Train: ",train_index, " Test: ", test_index)
            x_train, x_test = x[train_index], x[test_index]
            y_train, y_test = y[train_index], y[test_index]
            neigh.fit(x_train, y_train)
            y_pred = neigh.predict(x_test)
            score = accuracy_score(y_test, y_pred)
            print("Score: ",score)
            scores.append(score)
        
        
        print("Media: ",sum(scores)/len(scores)*100)
        
        
        #---DecisionTree---#
        score = 0
        clf_gini = DecisionTreeClassifier(criterion = "gini", random_state = 100, max_depth=3, min_samples_leaf=5)
        kf = KFold(len(y), n_folds=10)
        scores = []
        for train_index, test_index in kf:
            #print("Train: ",train_index, " Test: ", test_index)
            x_train, x_test = x[train_index], x[test_index]
            y_train, y_test = y[train_index], y[test_index]
            clf_gini.fit(x_train, y_train)

            y_pred = clf_gini.predict(x_test)
            score = accuracy_score(y_test, y_pred)
            print("Decision Tree-Score: ",score)
            scores.append(score)
        
        
        
        print("DecisionTree Media: ",sum(scores)/len(scores)*100)
        
        
        #self.k_fold(x,y)
        #self.svm_fit(x_train, y_train, x_test, y_test)
        
        
        #neigh = KNeighborsClassifier(n_neighbors=5) - experiment
        #neigh.fit(x_train,y_train - Experiment
        
        #y_pred = neigh.predict(x_test) - Experiment
        
       
        #np.savetxt('knn.txt', y_pred, delimiter=',')
        
        #print("KNN: Accuracy of the Classifier C = %.3f " % metrics.accuracy_score(y_test, y_pred)) - Experimet
        #print(classification_report(y_test, y_pred)) - Experiment
        
        #Print NAME Error measure (KNN)
        #print("KNN: Normalized Mean Absolute Error (NMAE): %0.4f " % self.nmae(y_test, y_pred))
        #return neigh - Experiment
    
    
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    #Decision Tree
    #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
    
    def decision_tree_classifier(self):
    
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
            
        clf_gini = DecisionTreeClassifier(criterion = "gini", random_state = 100, max_depth=3, min_samples_leaf=5)
        clf_gini.fit(x_train, y_train)
        
        y_pred = clf_gini.predict(x_test)
        print("Decision Tree: Accuracy is: ", accuracy_score(y_test,y_pred)*100)
        print("Decision Tree: Normalized Mean Absolute Error (NMAE): %0.4f " % nmae(y_test, y_pred))
    


class AiWebService(threading.Thread):

    app = Flask(__name__)
    app.config["DEBUG"] = True
  
    KNN = None
  
    def __init__(self,thread_numbering,AiRuntime):
        ai_core = AiCore()
        AiWebService.KNN = ai_core.knn_classifier()
        self.thread_numbering = thread_numbering
        threading.Thread.__init__(self)
   
    def run(self):
        print("AI Listener is Running!")
        self.app.run(host='0.0.0.0', port=8083,debug=False)

    @app.route("/ml",methods=['POST'])
    def classifier_querry_api():
        '''
        Querry Classifier about current traffic
        '''
        
        #Raise an error if URL parameter is null
        if request.json is None:
            return json.dumps({"":""},sort_keys=True, indent=4)

        #Convert comma separetad atributes in list       
        mylist = [request.json['network_snapshot']]
        
        #Crate Pandas DataFrame with these columns
        df = pd.DataFrame([sub.split(",") for sub in mylist],columns=['Flow ID', 'Src IP', 'Src Port', 'Dst IP', 'Dst Port', 'Protocol',
           'Timestamp', 'Flow Duration', 'Tot Fwd Pkts', 'Tot Bwd Pkts',
           'TotLen Fwd Pkts', 'TotLen Bwd Pkts', 'Fwd Pkt Len Max',
           'Fwd Pkt Len Min', 'Fwd Pkt Len Mean', 'Fwd Pkt Len Std',
           'Bwd Pkt Len Max', 'Bwd Pkt Len Min', 'Bwd Pkt Len Mean',
           'Bwd Pkt Len Std', 'Flow Byts/s', 'Flow Pkts/s', 'Flow IAT Mean',
           'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min', 'Fwd IAT Tot',
           'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
           'Bwd IAT Tot', 'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max',
           'Bwd IAT Min', 'Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags',
           'Bwd URG Flags', 'Fwd Header Len', 'Bwd Header Len', 'Fwd Pkts/s',
           'Bwd Pkts/s', 'Pkt Len Min', 'Pkt Len Max', 'Pkt Len Mean',
           'Pkt Len Std', 'Pkt Len Var', 'FIN Flag Cnt', 'SYN Flag Cnt',
           'RST Flag Cnt', 'PSH Flag Cnt', 'ACK Flag Cnt', 'URG Flag Cnt',
           'CWE Flag Count', 'ECE Flag Cnt', 'Down/Up Ratio', 'Pkt Size Avg',
           'Fwd Seg Size Avg', 'Bwd Seg Size Avg', 'Fwd Byts/b Avg',
           'Fwd Pkts/b Avg', 'Fwd Blk Rate Avg', 'Bwd Byts/b Avg',
           'Bwd Pkts/b Avg', 'Bwd Blk Rate Avg', 'Subflow Fwd Pkts',
           'Subflow Fwd Byts', 'Subflow Bwd Pkts', 'Subflow Bwd Byts',
           'Init Fwd Win Byts', 'Init Bwd Win Byts', 'Fwd Act Data Pkts',
           'Fwd Seg Size Min', 'Active Mean', 'Active Std', 'Active Max',
           'Active Min', 'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min', 'Label'])
        
        #Create x variable
        x = df.iloc[:,0:84]
      
        #Remove String format from training model
        x = x.iloc[:,x.columns != "Src IP"]
        x = x.iloc[:,x.columns != "Dst IP"]
        x = x.iloc[:,x.columns != "Timestamp"]
        x = x.iloc[:,x.columns != "Flow ID"]
        #Remove the target columns
        x = x.iloc[:,x.columns != "Label"]
    
        #By using previous trained model makes a predictions using current Snap Shot of network
        y_predict = AiWebService.KNN.predict(x)
        
        return json.dumps({"traffic_catogory":y_predict[0]})
        #return json.dumps(request.json['message'])
        
class AiRuntime():
    
    def __init__(self, *args, **kwargs):
        super(AiRuntime, self).__init__(*args, **kwargs)
        web_service = AiWebService(1,self)
        web_service.setName("Thread2")
        web_service.start()

   
if __name__ == "__main__":
#    web_service = AiRuntime()
     ai_core = AiCore()
     KNN = ai_core.classifiers()


















































































































# #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
# #Test using IRIS data set
# #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
# 
# #Load IRIS dataset 
# iris = datasets.load_iris()
# 
# #Catch only 2 parameters (there are two)
# X = iris.data[:, :2]
# y = iris.target
# 
# x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
# y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
# h = (x_max / x_min)/100
# xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
#  np.arange(y_min, y_max, h))
# 
# 
# X_plot = np.c_[xx.ravel(), yy.ravel()]
# 
# # Create the SVC model object
# C = 1.0 # SVM regularization parameter
# svc = svm.SVC(kernel='linear', C=C, decision_function_shape='ovr').fit(X, y)
# Z = svc.predict(X_plot)
# 
# #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
# #End of IRIS data-set comparisson
# #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
# 
# 
# 
# 
# #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
# #IRIS Data-set versus Network Data-set (both has same features)
# #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
# 
# #Reading Data to be trained
# df = pd.read_csv('/home/rodrigo/MPLS-TE/Data-Set/cic-unb/test.csv')
# 
# #Cacth features from Test - In this case only two (to be compared with IRIS Data-set)
# X = df.iloc[:,8:10]
# y = df.iloc[:,29:30]
# 
# #Split data in Train and Test
# x_train, x_test, y_train, y_test = train_test_split(X,y, test_size=0.30)
# 
# #Conversion into numpy array
# x_train = np.array(x_train)
# y_train = np.array(y_train)
# y_train = column_or_1d(y_train, warn=False)
# 
# #Adjustments in numpy to keep big number format (without scientific notation)
# np.set_printoptions(suppress=False,formatter={'float_kind':'{:16.5f}'.format},linewidth=130)
# 
# # Create the SVC model object
# C = 1.0 # SVM regularization parameter
# svc = svm.SVC(kernel='rbf', C=C, decision_function_shape='ovr').fit(x_train, y_train)
# 
# #Test using splitted data
# Z = svc.predict(x_test)
# 
# #Print Accuracy of the Classifier (SVM)
# #print("SVM: Accuracy of the Classifier C = %.3f" % metrics.accuracy_score(y_test, Z))
# 
# #Print NAME Error measure (SVM)
# #print("SVM: Normalized Mean Absolute Error (NMAE): %0.4f " % nmae(y_test, Z))
# 
# 
# #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#
# #End of IRIS and Network Data-set comparissons
# #-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#-------------#

