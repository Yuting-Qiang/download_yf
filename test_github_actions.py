import datetime
import random
import os

# 1. 生成数据
current_time = datetime.datetime.utcnow().isoformat()  # 使用UTC时间，避免时区问题
random_number = random.randint(100, 999)

# 2. 构造要写入的行
new_line = f"{current_time},{random_number}\n"

# 3. 确定数据文件路径
file_path = "scheduled_data.csv"

# 4. 写入文件
# 'a' 模式表示追加 (append)
try:
    with open(file_path, 'a') as f:
        f.write(new_line)
    print(f"Successfully appended: {new_line.strip()}")
except Exception as e:
    print(f"Error writing to file: {e}")

# 如果是第一次运行，创建文件头
if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
    with open(file_path, 'w') as f:
        f.write("Timestamp,RandomNumber\n")
