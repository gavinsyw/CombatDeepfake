import numpy as np
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn import tree, metrics, cross_validation
import pickle
import xgboost as xgb
from xgboost.sklearn import XGBClassifier
from sklearn.grid_search import GridSearchCV
#train
pkl_file = open('train_100.pkl', 'rb')
data = pickle.load(pkl_file)
pkl_file.close()
X = data["data"]
y = data["label"]

# SVM
svclassifier_r = SVC(C=2.37, kernel='rbf', gamma=1.88)
svclassifier_r.fit(X, y)

# Logistic regression
logreg = LogisticRegression(solver='liblinear', max_iter=1000)
logreg.fit(X, y)

# Dicision Tree
DTree_classifier = tree.DecisionTreeClassifier(min_samples_split=4)
DTree_classifier.fit(X,y)

# XGBoost
"""def modelfit(alg, dtrain, predictors, useTrainCV=True, cv_folds=5, early_stopping_rounds=50):


 if useTrainCV:
  xgb_param = alg.get_xgb_params()
  xgtrain = xgb.DMatrix(dtrain[predictors].values, label=dtrain[target].values)
  cvresult = xgb.cv(xgb_param, xgtrain, num_boost_round=alg.get_params()['n_estimators'], nfold=cv_folds,
                    metrics='auc', early_stopping_rounds=early_stopping_rounds, show_progress=False)
  alg.set_params(n_estimators=cvresult.shape[0])

# Fit the algorithm on the data
alg.fit(dtrain[predictors], dtrain['Disbursed'], eval_metric='auc')

# Predict training set:
dtrain_predictions = alg.predict(dtrain[predictors])
dtrain_predprob = alg.predict_proba(dtrain[predictors])[:, 1]

# Print model report:
print
"\nModel Report"
print
"Accuracy : %.4g" % metrics.accuracy_score(dtrain['Disbursed'].values, dtrain_predictions)
print
"AUC Score (Train): %f" % metrics.roc_auc_score(dtrain['Disbursed'], dtrain_predprob)

feat_imp = pd.Series(alg.booster().get_fscore()).sort_values(ascending=False)
feat_imp.plot(kind='bar', title='Feature Importances')
plt.ylabel('Feature Importance Score')"""


xgb1 = XGBClassifier(
 learning_rate=0.03,
 n_estimators=1000,
 max_depth=5,
 min_child_weight=1,
 gamma=0,
 subsample=0.8,
 colsample_bytree=0.8,
 objective= 'binary:logistic',
 nthread=4,
 scale_pos_weight=1,
 seed=27)
xgb1.fit(X,y)

#test
pkl_file = open('test_1000.pkl', 'rb')
data = pickle.load(pkl_file)
pkl_file.close()
X_ = data["data"]
y_ = data["label"]

SVM = svclassifier_r.score(X_, y_)
LR = logreg.score(X_, y_)
DT = DTree_classifier.score(X_,y_)


print("SVM: "+str(SVM))
print("LR: "+str(LR))
print("Dicision Tree: "+str(DT))

# test for xgboost
train_predictions = xgb1.predict(X)
train_predprob = xgb1.predict_proba(X)[:, 1]
test_predictions = xgb1.predict(X_)
test_predprob = xgb1.predict_proba(X_)[:, 1]
print("\nModel Report")
print("Accuracy : %.4g" % metrics.accuracy_score(y_, test_predictions))
print("AUC Score (Train): %f" % metrics.roc_auc_score(y, train_predprob))
print("AUC Score (Test): %f" % metrics.roc_auc_score(y_, test_predprob))