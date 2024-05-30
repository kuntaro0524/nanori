
list_a = [20967, 23232, 25427,27697, 29952, 32262, 34482, 36770]

# list_a 微分 して係数の平均値を取得する
def diff_list(list_a):
    diff_list = []
    for i in range(len(list_a)-1):
        diff_list.append(list_a[i+1] - list_a[i])
    return diff_list
 
diff_list = diff_list(list_a)
print(diff_list)

# 係数の平均値を取得する
def average_diff(diff_list):
    return sum(diff_list) / len(diff_list)

average_diff = average_diff(diff_list)
print(average_diff)
