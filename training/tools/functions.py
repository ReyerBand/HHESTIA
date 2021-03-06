#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# functions.py ////////////////////////////////////////////////////////////////////
#==================================================================================
# This module contains functions to be used with HHESTIA //////////////////////////
#==================================================================================

# modules
import ROOT as root
import numpy
import matplotlib.pyplot as plt
import copy
import random
import itertools
import types
import tempfile
import keras.models

# functions from modules
from sklearn import svm, metrics, preprocessing, datasets
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc

#==================================================================================
# Plot Confusion Matrix ///////////////////////////////////////////////////////////
#----------------------------------------------------------------------------------
# cm is the comfusion matrix //////////////////////////////////////////////////////
# classes are the names of the classes that the classifier distributes among //////
#----------------------------------------------------------------------------------

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
   """
   This function prints and plots the confusion matrix.
   Normalization can be applied by setting `normalize=True`.
   """
   if normalize:
       cm = cm.astype('float') / cm.sum(axis=1)[:, numpy.newaxis]
       print("Normalized confusion matrix")
   else:
       print('Confusion matrix, without normalization')

   print(cm)

   plt.imshow(cm, interpolation='nearest', cmap=cmap)
   plt.title(title)
   plt.colorbar()
   tick_marks = numpy.arange(len(classes))
   plt.xticks(tick_marks, classes, rotation=45)
   plt.yticks(tick_marks, classes)

   fmt = '.2f' if normalize else 'd'
   thresh = cm.max() / 2.
   for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
       plt.text(j, i, format(cm[i, j], fmt),
                horizontalalignment="center",
                color="white" if cm[i, j] > thresh else "black")

   plt.tight_layout()
   plt.ylabel('True label')
   plt.xlabel('Predicted label')

#==================================================================================
# Get Branch Names ////////////////////////////////////////////////////////////////
#----------------------------------------------------------------------------------
# tree is a TTree /////////////////////////////////////////////////////////////////
#----------------------------------------------------------------------------------

def getBranchNames(tree ):

   # empty array to store names
   treeVars = []

   # loop over branches
   for branch in tree.GetListOfBranches():
      name = branch.GetName()
      if 'nJets' in name:
         continue
      if 'SoftDropMass' in name:
         continue
      if 'mass' in name:
         continue
      if 'gen' in name:
         continue
      if 'pt' in name:
         continue
      treeVars.append(name)

   return treeVars

#==================================================================================
# Append Arrays from trees ////////////////////////////////////////////////////////
#----------------------------------------------------------------------------------
# array is a numpy array made from a TTree ////////////////////////////////////////
#----------------------------------------------------------------------------------

def appendTreeArray(array):

   tmpArray = []
   for entry in array[:] :
      a = list(entry)
      tmpArray.append(a)
   newArray = copy.copy(tmpArray)
   return newArray

#==================================================================================
# Randomize Data //////////////////////////////////////////////////////////////////
#----------------------------------------------------------------------------------
# array is an array of TTree arrays ( [ tree1array, tree2array, ...] ) ////////////
#----------------------------------------------------------------------------------

def randomizeData(array):

   trainData = []
   targetData = []
   nEvents = 0
   for iArray in range(len(array) ) :
      nEvents = nEvents + len(array[iArray])
   while nEvents > 0:
      rng = random.randint(0,len(array)-1 )
      if (len(array[rng]) > 0):
         trainData.append(array[rng].pop() )
         targetData.append(rng)
         nEvents = nEvents - 1
   return trainData, targetData

#==================================================================================
# Plot Performance ////////////////////////////////////////////////////////////////
#----------------------------------------------------------------------------------
# loss is an array of loss and loss_val from the training /////////////////////////
# acc is an array of acc and acc_val from the training ////////////////////////////
# train_test is the train data that has not been trained on ///////////////////////
# target_test is the target data that has not been trained on /////////////////////
# target_predict is the models prediction of data that has not been trained on ////
#----------------------------------------------------------------------------------

def plotPerformance(loss, acc): #, train_test, target_test, target_predict):
   
   # plot loss vs epoch
   plt.figure(figsize=(15,10))
   ax = plt.subplot(2, 2, 1)
   ax.plot(loss[0], label='loss')
   ax.plot(loss[1], label='val_loss')
   ax.legend(loc="upper right")
   ax.set_xlabel('epoch')
   ax.set_ylabel('loss')
   plt.savefig("plots/loss.pdf")
   plt.savefig("plots/loss.png")

   # plot accuracy vs epoch
   ax = plt.subplot(2, 2, 2)
   ax.plot(acc[0], label='acc')
   ax.plot(acc[0], label='val_acc')
   ax.legend(loc="upper left")
   ax.set_xlabel('epoch')
   ax.set_ylabel('acc')
   plt.savefig("plots/acc.pdf")
   plt.savefig("plots/acc.png")

   # Plot ROC
#   fpr, tpr, thresholds = roc_curve(target_test, target_predict)
#   roc_auc = auc(fpr, tpr)
#   ax = plt.subplot(2, 2, 3)
#   ax.plot(fpr, tpr, lw=2, color='cyan', label='auc = %.3f' % (roc_auc))
#   ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='k', label='random chance')
#   ax.set_xlim([0, 1.0])
#   ax.set_ylim([0, 1.0])
#   ax.set_xlabel('false positive rate')
#   ax.set_ylabel('true positive rate')
#   ax.set_title('receiver operating curve')
#   ax.legend(loc="lower right")

#==================================================================================
# Plot Probabilities //////////////////////////////////////////////////////////////
#----------------------------------------------------------------------------------
# probs is an array of probabilites, labels, and colors ///////////////////////////
#    [ [probArray, label, color], .. ] ////////////////////////////////////////////
#----------------------------------------------------------------------------------

def plotProbabilities(probs):

   for iProb in range(len(probs) ) :
      for jProb in range(len(probs) ) :
         plt.figure()
         plt.xlabel("Probability for " + probs[iProb][1] + " Classification")
         plt.hist(probs[jProb][0].T[iProb], bins=20, range=(0,1), label=probs[jProb][1], color=probs[jProb][2], histtype='step', 
                  normed=True, log = True)
         plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=6, mode="expand", borderaxespad=0.)
         plt.savefig("prob_" + probs[iProb][1] + ".pdf")
         plt.close()

#==================================================================================
# Make Keras Picklable  ///////////////////////////////////////////////////////////
#----------------------------------------------------------------------------------
# A patch to make Keras give results in pickle format /////////////////////////////
#----------------------------------------------------------------------------------

def make_keras_picklable():
    def __getstate__(self):
        model_str = ""
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=True) as fd:
            keras.models.save_model(self, fd.name, overwrite=True)
            model_str = fd.read()
        d = { 'model_str': model_str }
        return d

    def __setstate__(self, state):
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=True) as fd:
            fd.write(state['model_str'])
            fd.flush()
            model = keras.models.load_model(fd.name)
        self.__dict__ = model.__dict__


    cls = keras.models.Model
    cls.__getstate__ = __getstate__
    cls.__setstate__ = __setstate__
