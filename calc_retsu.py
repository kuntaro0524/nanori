
list_a = [9308,11592,13800,16103,18309,20609,22838]

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
