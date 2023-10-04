import csv,os
import json
def append_to_csv(text,csvfile):
    text="{"+text+"}"
    text = json.loads(text)  
    print(text)
    if not os.path.exists(csvfile):
        with open(csvfile, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=text.keys())
            writer.writeheader()
    with open(csvfile, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=text.keys())
        print(writer)
        
        # 写入新行数据
        writer.writerow(text)

    print('成功寫入 CSV 文件！')