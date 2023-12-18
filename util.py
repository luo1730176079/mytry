import pandas as pd
import re
import numpy as np
import sys
import os
def regular_matching(xlsx_path):
    df_new = pd.DataFrame(columns=["名称","型号","公称通径(DN)","公称压力(PN)","材质","数量","单价(元)","合计(元)"])                          #表三对应目标列

    #可能开头几行不是标题，要判断，根据没有列名的列的数量来判断
    for i in range(10):
        df = pd.read_excel(xlsx_path,sheet_name=0,skiprows=i)
        temp_empty = 0
        for j in df.columns:
            if j[:7] == 'Unnamed':
                temp_empty = temp_empty + 1
        if temp_empty / len(df.columns) <= 0.5:     #当没有列名的列的数量大于50%，取下一列做列名
            break

    if df.columns[1] == "设备名称" and df.columns[2] == "规格型号/技术参数" and df.columns[7] == "备注":
        df = df.dropna(subset=['备注'])
    df.columns = [re.sub(r'[^\u4e00-\u9fa5\d]+', '',i) for i in df.columns]     #删除列名中的空格和英文字母    
    #df = df.iloc[:39,:]        #表一手动清洗数据，即只看前39行
    df = df.dropna(axis=1, how='all')

    #判断是否需要进行划分，0表示不需要进行划分，1表示需要进划分，这里暂时先根据'，'来划分，然后将每一列的所有数据放到“数据”列
    colmns_if_cut = pd.DataFrame(columns=["列名","是否需要划分","数据","是否使用"])
    colmns_if_cut["列名"] = df.columns
    colmns_if_cut["是否需要划分"] = 0
    colmns_if_cut["是否使用"] = 0
    for i in range(len(colmns_if_cut)):
        colmns_if_cut.at[i,"数据"] = df[colmns_if_cut.iloc[i,0]].tolist()
        for j in range(2):
            if ' ' in str(df[colmns_if_cut.iloc[i,0]][0]) or ',' in str(df[colmns_if_cut.iloc[i,0]][0]) or '，' in str(df[colmns_if_cut.iloc[i,0]][0]):
                colmns_if_cut.iloc[i,1] = 1
                break
    colmns_if_cut.iloc[0,3] = 1

    for i in df_new.columns:
        #如果输出表的某列名和输入表的列名相同，且不需要进行划分，则直接复制过去
        if any( columns_name == i for columns_name in df.columns):
        #if any( i in str(columns_name) for columns_name in df.columns):
            df_new[i] = df[i]
            colmns_if_cut.loc[colmns_if_cut["列名"] == i,"是否使用"] = 1
            continue

        if "名称" in i:
            for j in range(len(colmns_if_cut)):
                if any("阀" in str(word) for word in colmns_if_cut.iloc[j,2]) or any("弯头" in str(word) for word in colmns_if_cut.iloc[j,2]):    #是否存在关键词
                    if colmns_if_cut.iloc[j,1] == 0:           #判断是否是需要划分的列
                        df_new[i] = df[colmns_if_cut.iloc[j,0]]    
                        colmns_if_cut.iloc[j,3] = 1
                        break 
                    else:   #是需要划分的列
                        pattern = re.compile(r'[\u4e00-\u9fa5]+(?:阀|法兰|排水器)')
                        df_new[i] = df[colmns_if_cut.iloc[j,0]].apply(lambda x: re.search(pattern,str(x)))
                        df_new[i] = df_new[i].apply(lambda x:x.group() if x is not None else x)
            continue

        if "型号" in i:
            pattern = re.compile(r'(?!DN|PN)[a-zA-Z0-9]+-[a-zA-Z0-9.]+(?!Mpa)|CL\d+')
            for j in range(len(colmns_if_cut)):
                if any(re.search(pattern,str(word)) is not None for word in colmns_if_cut.iloc[j,2]):    #是否存在关键词
                    if colmns_if_cut.iloc[j,1] == 0:           #判断是否是需要划分的列
                        if any(re.search("DN\d+|PN\d+",str(word)) is not None for word in colmns_if_cut.iloc[j,2]):    #是否存在DN或PN
                            continue
                        df_new[i] = df[colmns_if_cut.iloc[j,0]]
                        colmns_if_cut.iloc[j,3] = 1
                        break 
                    else:   #是需要划分的列
                        df_new[i] = df[colmns_if_cut.iloc[j,0]].apply(lambda x: re.search(pattern,str(x)))
                        df_new[i] = df_new[i].apply(lambda x:x.group() if x is not None else x)
                    
            continue

        if "通径" in i:
            for j in range(len(colmns_if_cut)):
                if any("DN" in str(word) for word in colmns_if_cut.iloc[j,2]):    #是否存在关键词
                    if colmns_if_cut.iloc[j,1] == 0:           #判断是否是需要划分的列
                        if any(re.search("[\u4e00-\u9fa5]+",str(word)) is not None for word in colmns_if_cut.iloc[j,2]):    #是否存在关键词
                            continue
                        df_new[i] = df[colmns_if_cut.iloc[j,0]]
                        colmns_if_cut.iloc[j,3] = 1
                        break 
                    else:   #是需要划分的列
                        df_new[i] = df[colmns_if_cut.iloc[j,0]].apply(lambda x: re.search("DN\d+\.?\d+",str(x)))
                        df_new[i] = df_new[i].apply(lambda x:x.group() if x is not None else x)

            continue

        if "压力" in i:
            stress = ["PN","MPa","CL"]
            pattern = re.compile('|'.join(re.escape(word) for word in stress))
            for j in range(len(colmns_if_cut)):
                if any(str(material) in str(word) for word in colmns_if_cut.iloc[j,2] for material in stress):    #是否存在关键词
                    if colmns_if_cut.iloc[j,1] == 0:           #判断是否是需要划分的列
                        df_new[i] = df[colmns_if_cut.iloc[j,0]]
                        colmns_if_cut.iloc[j,3] = 1
                        break 
                    else:   #是需要划分的列
                        df_new[i] = df[colmns_if_cut.iloc[j,0]].apply(lambda x: re.search("PN\d+\.?\d+",str(x)))
                        df_new[i] = df_new[i].apply(lambda x:x.group() if x is not None else x)
            continue
        
        if "材质" in i or "材料" in i:
            materials = ["304","碳钢","不锈钢"]
            pattern = re.compile('|'.join(re.escape(word) for word in materials))
            for j in range(len(colmns_if_cut)):
                #if any("304" in str(word) for word in colmns_if_cut.iloc[j,2]) or any("碳钢" in str(word) for word in colmns_if_cut.iloc[j,2]):    #是否存在关键词
                if any(str(material) in str(word) for word in colmns_if_cut.iloc[j,2] for material in materials):    #是否存在关键词
                    if colmns_if_cut.iloc[j,1] == 0:           #判断是否是需要划分的列
                        df_new[i] = df[colmns_if_cut.iloc[j,0]]
                        colmns_if_cut.iloc[j,3] = 1
                        break 
                    else:   #是需要划分的列
                        df_new[i] = df[colmns_if_cut.iloc[j,0]].apply(lambda x: re.search(pattern,str(x)))
                        df_new[i] = df_new[i].apply(lambda x:x.group() if x is not None else x)
            continue

        if "连接形式" in i :
            materials = ["内螺纹","RF法兰"]
            pattern = re.compile('|'.join(re.escape(word) for word in materials))
            for j in range(len(colmns_if_cut)):
                if any(str(material) in str(word) for word in colmns_if_cut.iloc[j,2] for material in materials):    #是否存在关键词
                    if colmns_if_cut.iloc[j,1] == 0:           #判断是否是需要划分的列
                        df_new[i] = df[colmns_if_cut.iloc[j,0]]
                        colmns_if_cut.iloc[j,3] = 1
                        break 
                    else:   #是需要划分的列
                        df_new[i] = df[colmns_if_cut.iloc[j,0]].apply(lambda x: re.search(pattern,str(x)))
                        df_new[i] = df_new[i].apply(lambda x:x.group() if x is not None else x)
            continue

        #一般数量列都不需要进行划分
        if "数量" in i:
            for j in range(len(colmns_if_cut)):
                if all(isinstance(item, (int, float)) for item in colmns_if_cut.iloc[j,2]) and (colmns_if_cut.iloc[j,2][1] != 2 or colmns_if_cut.iloc[j,2][2] != 3 or colmns_if_cut.iloc[j,2][3] != 4) and all(item<10000 for item in colmns_if_cut.iloc[j,2]):    #如果某一列都是数字，那这一列是数量列
                    if colmns_if_cut.iloc[j,1] == 0:           
                        df_new[i] = df[colmns_if_cut.iloc[j,0]]
                        colmns_if_cut.iloc[j,3] = 1
                        break 

            continue

    for i in range(len(colmns_if_cut)):
        if colmns_if_cut.iloc[i,3] == 0:
            df_new[colmns_if_cut.iloc[i,0]] = df[colmns_if_cut.iloc[i,0]]

    df_new = df_new.reset_index()
    df_new = df_new[['index'] + [col for col in df_new.columns if col != 'index']]
    df_new['index'] = df_new['index'].apply(lambda x:x+1)
    df_new = df_new.rename(columns={'index': '序号'})

    #xlsx_name = os.path.basename(xlsx_path)
    xlsx_name = xlsx_path.split('.xlsx')[0]
    new_xlsx = xlsx_name + "_output.xlsx"
    df_new.to_excel(f'{xlsx_name}_output.xlsx', index=False)

    print(f"please check  output filepath: {xlsx_name}_output.xlsx")
    print("finish work ..") 
    #sys.exit()
    return new_xlsx

    