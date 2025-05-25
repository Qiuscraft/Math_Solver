import csv

# 文件路径
file_path = r'd:\2025Spring\AI\PJ\Math_Solver\data_improver\loss\Qwen_Qwen3-0.6B-data-improved-2025-5-25_13_23_23.csv'

# 初始化变量
step_interval = 100
current_sum = 0
current_count = 0
averages = []

# 读取CSV文件
with open(file_path, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # 跳过表头

    for row in reader:
        step = int(row[0])
        loss = float(row[1])

        # 累加当前区间的loss
        current_sum += loss
        current_count += 1

        # 如果达到100步，计算平均值并重置计数器
        if step % step_interval == 0:
            average_loss = current_sum / current_count
            averages.append((step, average_loss))
            current_sum = 0
            current_count = 0

# 打印结果
print("每100步的loss平均值：")
for step, avg in averages:
    print(f"Step {step}: Average Loss = {avg:.4f}")