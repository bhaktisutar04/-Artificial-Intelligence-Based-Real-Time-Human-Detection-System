from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import roc_auc_score
from sklearn.metrics import log_loss
from sklearn.metrics import roc_curve
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

X_actual = [0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1]
Y_predic = [0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1]

results = confusion_matrix(X_actual, Y_predic)
print('Confusion Matrix :')
print(results)

sns.heatmap(results,annot=True,fmt='g',xticklabels=['Person','Not Person'],yticklabels=['Person','Not Person'])
plt.ylabel('Prediction',fontsize=13)
plt.xlabel('Actual',fontsize=13)
plt.title('Confusion Matrix',fontsize=17)
plt.show()

print('Accuracy Score is',accuracy_score(X_actual, Y_predic))
print('Classification Report : ')
print(classification_report(X_actual, Y_predic))
print('AUC-ROC:',roc_auc_score(X_actual, Y_predic))
print('LOGLOSS Value is',log_loss(X_actual, Y_predic))

fpr, tpr, thresholds = roc_curve(X_actual, Y_predic)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label='ROC curve')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend(loc='lower right')
plt.show()
