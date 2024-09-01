import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

# 读取CSV文件
df = pd.read_csv(r'E:\PycharmProjects\Legislators\result\result_433_20.csv')

# 提取真实结果和预测结果
y_true = df['Real Result']
y_pred = df['Personal Prediction']

# 计算每个类别的F1分数
f1_support = f1_score(y_true, y_pred, labels=['Yea'], average='macro')
f1_oppose = f1_score(y_true, y_pred, labels=['Nay'], average='macro')
f1_not_voting = f1_score(y_true, y_pred, labels=['Not Voting'], average='macro')

# 打印每个类别的F1分数
print(f"F1 score for Support: {f1_support}")
print(f"F1 score for Oppose: {f1_oppose}")
print(f"F1 score for Not Voting: {f1_not_voting}")

# 计算加权F1分数
f1_weighted = f1_score(y_true, y_pred, average='weighted')

# 打印microF1分数
print(f"F1 score: {f1_weighted}")

# 计算准确率
accuracy = accuracy_score(y_true, y_pred)

# 打印准确率
print(f"Accuracy: {accuracy}")


