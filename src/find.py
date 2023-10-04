import pandas as pd
import json

def sign(user_input):
  # 確定註冊代號
    df_a = pd.read_excel('txt.xlsx', sheet_name='工令')
  
    # 獲取第一行內容
    code_row = df_a.iloc[:,0].values.tolist()
    print(code_row)
    # 檢查輸入值
    
    if user_input in code_row:
        return "註冊成功"
    else:
        return "註冊失敗，請確定代號"
    
  
def test(xx, yy):
    # 讀取 A 工作表，並篩選符合條件的資料
    print(xx,yy)
    df_a = pd.read_excel('txt.xlsx', sheet_name='工令')
    df_a_filtered = df_a[df_a['代號'] == xx][df_a['工令'] == yy]
    print(df_a_filtered)
    if len(df_a_filtered) == 0:
        return None
    
    # 讀取 B 工作表，並將工令為 yy 的所有資料都取出來
    df_b = pd.read_excel('txt.xlsx', sheet_name='型號')
    df_b_filtered = df_b[df_b['工令'] == yy]
    print(df_b_filtered)
    # 將聯絡人的資訊整理成新的欄位
    df_b_filtered['區域'], df_b_filtered['案名'] = zip(*df_b_filtered['區域,案名'].str.split(','))
    
    # 只保留需要的欄位，並去除重複資料
    df_b_filtered = df_b_filtered[['工令', '地址', '區域', '案名', '聯絡人']].drop_duplicates()
    
    # 輸出結果
    print(df_b_filtered.to_dict('records'))
    return df_b_filtered.to_dict('records')
  
def test2(xx,yy,zz):
    
    # 讀取 B 工作表，並將工令為 xx 的所有資料都取出來
    df_b = pd.read_excel('txt.xlsx', sheet_name='型號')
    df_b_filtered = df_b[df_b['區域,案名'] == xx]
    print(df_b_filtered)
    
    df_b_filtered['區域'], df_b_filtered['案名'] = zip(*df_b_filtered['區域,案名'].str.split(','))
    # 只保留需要的欄位，並去除重複資料
    df_b_filtered = df_b_filtered[['工令', '區域', '案名', '聯絡人', '地址']].drop_duplicates()

  # 讀取 A 工作表，確定
    
    
    print(1)
    
    df_a = pd.read_excel('txt.xlsx', sheet_name='工令')
    df_a_filtered = df_a[df_a['代號'] == yy][df_a['工令'] == zz]
    print(df_a_filtered)
    if len(df_a_filtered) == 0:
        return "查無資料"
    # 將資料轉成字典
    dictoutput=df_b_filtered.to_dict('records')
    print(dictoutput)
    # 輸出結果
    json_data=json.dumps(dictoutput,indent=4,ensure_ascii=False).strip().lstrip()
    translation_table = str.maketrans('', '', '{}[]')
    output = json_data.translate(translation_table).strip().lstrip()
    output = output.replace(" ", "")
    print(output)
    return output