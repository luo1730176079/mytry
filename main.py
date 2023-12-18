import pandas as pd
import re
import spacy
import os
nlp = spacy.load("zh_core_web_lg")
import hanlp
HanLP = hanlp.load("close_tok_pos_ner_srl_dep_sdp_con_electra_small_20210304_135840") 
from util import regular_matching

def dea_with_dn(column_names):
    name_list = ["公称通径","尺寸"]
    res_list = []
    for name in name_list:
        device_name_doc = nlp(name)
        similarities = [(column_name, device_name_doc.similarity(
            nlp(column_name))) for column_name in column_names]
        similarities.sort(key=lambda x: x[1], reverse=True)
        tmp_column_name = similarities[0][0]
        res_list.append((tmp_column_name,similarities[0][1]))

    res_list.sort(key=lambda x: x[1], reverse=True)
    most_similar_column_name = res_list[0][0]
    if res_list[0][1] > 0.6:
        size_idx = column_names.index(most_similar_column_name)
        size_name = df.columns.tolist()[size_idx]
        dn_list = df[size_name].tolist()
        selected_index.append(size_idx)
    else:
        dn_list = [''] * len(device_name_list)
    return dn_list   

def dea_with_pn(column_names):
    name_list = ["公称压力","压力"]
    res_list = []
    for name in name_list:
        device_name_doc = nlp(name)
        similarities = [(column_name, device_name_doc.similarity(
            nlp(column_name))) for column_name in column_names]
        similarities.sort(key=lambda x: x[1], reverse=True)
        tmp_column_name = similarities[0][0]
        res_list.append((tmp_column_name,similarities[0][1]))
    res_list.sort(key=lambda x: x[1], reverse=True)
    most_similar_column_name = res_list[0][0]
    if res_list[0][1] > 0.6:
        size_idx = column_names.index(most_similar_column_name)
        size_name = df.columns.tolist()[size_idx]
        pn_list = df[size_name].tolist()
        selected_index.append(size_idx)
    else:
        pn_list = [''] * len(device_name_list)
    return pn_list   

def deal_with_dn_pn(column_names):
    size_doc = nlp("规格")
    similarities = [(column_name, size_doc.similarity(nlp(column_name)))
                    for column_name in column_names]
    # 按相似度排序，找到最相近的列名
    similarities.sort(key=lambda x: x[1], reverse=True)
    most_similar_column_name = similarities[0][0]

    if similarities[0][1] > 0.6 and judge_content_too_long(most_similar_column_name):
        size_idx = column_names.index(most_similar_column_name)
        size_name = df.columns.tolist()[size_idx]
        selected_index.append(size_idx)
        df_size_names = df[size_name].tolist()
        size_names = []
        dn_list = []
        pn_list = []
        for text in df_size_names:
            dn_values = re.findall(r'DN\d+-?\d*', text)
            pn_value = re.search(r'PN(\d+.?\d)', text)
            if dn_values:
                dn_list.append('*'.join(dn_values))
            else:
                dn_list.append('')
            if pn_value:
                pn_list.append(pn_value.group())
            else:
                pn_list.append('')
        return dn_list,pn_list
    else:
        return dea_with_dn(column_names),dea_with_pn(column_names)
    
def join_string(column):
    df[column] = df[column].apply(str) 
    concatenated_string = df[column].str.cat(sep='')   
    return concatenated_string

def judge_content_too_long(column):
    df[column] = df[column].apply(str) 
    string_lengths = df[column].str.len()
    average_length = string_lengths.mean()
    return average_length > 10


def deal_with_material_name_nlp(column_names):  
    need_nlp_column_name = None   
    concatenated_column_names = []
    for column_name in raw_column_names:
        concatenated_column_names.append(join_string(column_name))
           
    name_list = ["材质","材料"]
    res_list = []
    for name in name_list:
        device_name_doc = nlp(name)
        similarities = [(column_name, device_name_doc.similarity(
            nlp(column_name))) for column_name in concatenated_column_names]
        similarities.sort(key=lambda x: x[1], reverse=True)
        tmp_column_name = similarities[0][0]
        index = concatenated_column_names.index(tmp_column_name)
        res_list.append((column_names[index],similarities[0][1])) 

    res_list.sort(key=lambda x: x[1], reverse=True)
    most_similar_column_name = res_list[0][0]

    size_idx = column_names.index(most_similar_column_name)
    size_name = df.columns.tolist()[size_idx]
    
    df_size_names = df[size_name].tolist()
    

    material_list = []
    for text in df_size_names:
        doc  = HanLP([text])   
        tree = doc['con'][0]
        search_list = list(tree.subtrees(lambda t: t.height() == 2 and t.label() != 'PU'))
        for idx,subtree in enumerate(search_list):
            if "体" in subtree[0]:
                break
        if idx+1 >= len(search_list):
            return None,None    
        res =  search_list[idx+1]   
        material_list.append(res[0])  

    return material_list,size_idx
    


def deal_with_material_name(column_names):
    name_list = ["材质","材料"]
    res_list = []
    for name in name_list:
        device_name_doc = nlp(name)
        similarities = [(column_name, device_name_doc.similarity(
            nlp(column_name))) for column_name in column_names]
        similarities.sort(key=lambda x: x[1], reverse=True)
        tmp_column_name = similarities[0][0]
        res_list.append((tmp_column_name,similarities[0][1]))

    res_list.sort(key=lambda x: x[1], reverse=True)
    most_similar_column_name = res_list[0][0]
    
    if res_list[0][1] > 0.6:
        size_idx = column_names.index(most_similar_column_name)
        size_name = df.columns.tolist()[size_idx]
        df_material_names = df[size_name].tolist()
        selected_index.append(size_idx)
    else:
        df_material_names,size_idx = deal_with_material_name_nlp(column_names)
        if df_material_names:
             nlp_selected_index.append(size_idx)
             return df_material_names
        df_material_names = [''] * len(device_name_list)

    return df_material_names

def deal_with_unit_name(column_names):
    size_doc = nlp("单价")
    similarities = [(column_name, size_doc.similarity(nlp(column_name)))
                    for column_name in column_names]
    similarities.sort(key=lambda x: x[1], reverse=True)
    most_similar_column_name = similarities[0][0]


    if similarities[0][1] > 0.6:
        size_idx = column_names.index(most_similar_column_name)
        size_name = df.columns.tolist()[size_idx]
        df_unit_names = df[size_name].tolist()
        selected_index.append(size_idx)
    else:
        df_unit_names = [''] * len(device_name_list)
    return df_unit_names    

def deal_with_num_name(column_names):
    size_doc = nlp("数量")
    similarities = [(column_name, size_doc.similarity(nlp(column_name)))
                    for column_name in column_names]
    similarities.sort(key=lambda x: x[1], reverse=True)
    most_similar_column_name = similarities[0][0]
    if similarities[0][1] > 0.5:
        size_idx = column_names.index(most_similar_column_name)
        size_name = df.columns.tolist()[size_idx]
        df_num_names = df[size_name].tolist()
        df_num_names = [str(num) for num in df_num_names]
        selected_index.append(size_idx)
    else:
        df_num_names = [''] * len(device_name_list)
    return df_num_names    

def deal_with_device_name(column_names):
 
    name_list = ["设备名称","位号"]
    res_list = []
    for name in name_list:
        device_name_doc = nlp(name)
        similarities = [(column_name, device_name_doc.similarity(
            nlp(column_name))) for column_name in column_names]
        similarities.sort(key=lambda x: x[1], reverse=True)
        tmp_column_name = similarities[0][0]
        res_list.append((tmp_column_name,float(similarities[0][1])))

    res_list.sort(key=lambda x: x[1], reverse=True)
    most_similar_column_name = res_list[0][0]
    device_idx = column_names.index(most_similar_column_name)
    device_column_name = df.columns.tolist()[device_idx]

    df_device_names = df[device_column_name].tolist()
    device_names = []
    if res_list[0][1] < 0.7:
        for device in df_device_names:
            name, _ = device.split('\\')
            device_names.append(name)
    else:
        device_names = df_device_names
    selected_index.append(device_idx)    
    device_names = [s.strip() for s in device_names]
    return device_names


def deal_with_model_name(column_names):
    name_list = ["型号","阀门型号","规格型号"]
    res_list = []
    for name in name_list:
        device_name_doc = nlp(name)
        similarities = [(column_name, device_name_doc.similarity(
            nlp(column_name))) for column_name in column_names]
        similarities.sort(key=lambda x: x[1], reverse=True)
        tmp_column_name = similarities[0][0]
        res_list.append((tmp_column_name,similarities[0][1]))

    res_list.sort(key=lambda x: x[1], reverse=True)
    most_similar_column_name = res_list[0][0]
    model_index = column_names.index(most_similar_column_name)
    device_column_name = df.columns.tolist()[model_index]

    df_model_names = df[device_column_name].tolist()
    model_names = []
    model_names = df_model_names
    if res_list[0][1] > 0.7:
        selected_index.append(model_index)    
        model_names = [s.strip() for s in model_names]
    else:
        model_names = [''] * len(device_name_list)   
    return model_names

def get_all_price_list(df_num_names,df_unit_names):
    all_price_list = []
    if df_unit_names[0] != '':
        for i in range(len(df_num_names)):
            all_price_list.append(float(df_num_names[i])*float(df_unit_names[i]))
    else:
        all_price_list = [''] * len(device_name_list)  
    return all_price_list    

def get_device_model_dn_pn_material_list(df):
    column_name = df.columns[2]
    column_data = df[column_name].tolist()
    device_name_list = []
    model_list = []
    material_list = []
    dn_list=  []
    pn_list = []
    for i,data in enumerate(column_data): 
        device_name,model,dn,pn,material = None,None,None,None,None
        device_name,text = str(data).split('\\')
        doc  = HanLP([text])
        tree = doc['con'][0]
        search_list = list(tree.subtrees(lambda t: t.height() == 2 and t.label() != 'PU'))
        for idx,subtree in enumerate(search_list):
            if "DN" in subtree[0]:
                res =  search_list[idx][0]
                if 'DN' != res[:2]: # 解决DN和型号连在一起的问题
                    dn ='DN'+res.split('DN')[1]
                    model = res.split('DN')[0]
                else:
                    model =  search_list[idx-1][0]
                    model = re.sub('[\u4e00-\u9fff]+', '', model)
                    dn = res
            elif "PN" in subtree[0]:
                pn =  search_list[idx][0]
                if 'PN' != pn[:2]:
                    pn ='PN'+pn.split('PN')[1]
            elif "MPa" in subtree[0]:  
                pn =  search_list[idx][0]
            elif subtree[0] in ["不锈钢","304"]:
                material = search_list[idx][0]

        if model and '-' not in model: # 筛选掉错误的型号 不含‘-’的
            model = None
        device_name_list.append(device_name)
        model_list.append(model)   

        dn = str(dn).split(' ')[0] # 尾处理
        dn_list.append(dn)    
        pn_list.append(pn) 
        material_list.append(material)         

    return device_name_list,model_list,dn_list,pn_list,material_list    
    

def concatenate_sheets(filename):
    sheets = pd.read_excel(filename, sheet_name=None)
    concatenated_df = pd.concat(sheets.values(), ignore_index=True)
    return concatenated_df

def main_code(xlsx_path):

    global device_name_list,model_list,dn_list,pn_list,material_list,num_list,unit_price_list, all_price_list 
    global selected_index,nlp_selected_index,raw_column_names
    global df 
    device_name_list,model_list,dn_list,pn_list,material_list,num_list,unit_price_list, all_price_list = [],[],[],[],[],[],[],[]
    selected_index = []  # 已经选择过的列
    nlp_selected_index = [] # 算法处理过的列
    #xlsx_path = input("please input xlsx path: ")
    df = concatenate_sheets(xlsx_path)
    if df.columns[1] == "浙江德卡控制阀仪表有限公司——技术文件": ## 5.xlsx的预处理
        df = df.drop([0,1,3])
        new_columns = df.iloc[0]
        df = df.rename(columns=new_columns)
        df = df.iloc[1:].dropna().reset_index(drop=True)
    elif df.columns[2] == "描述": ## 6.xlsx的预处理
        df = df.drop([0])    
        new_column_name = '标志位-无意义'
        df.rename(columns={df.columns[0]: new_column_name}, inplace=True)
        new_column_name = '设备名称'
        df.rename(columns={df.columns[1]: new_column_name}, inplace=True)
        pre_line = df.iloc[0, 0]
        pre_name =  df.iloc[0, 1]
        for index, line in df['标志位-无意义'].iteritems():
            if pre_line == line:
                df.loc[index, '设备名称'] = pre_name
            pre_name = df.loc[index, '设备名称'] 
            pre_line = line
        df = df.drop(df.columns[0], axis=1)   
    elif df.columns[1] == "物料编码" and df.columns[2] == "规格型号":
        device_name_list,model_list,dn_list,pn_list,material_list  = get_device_model_dn_pn_material_list(df)
        nlp_selected_index.append(2)
    else:
        new_xlsx = regular_matching(xlsx_path)
        return new_xlsx
      
    raw_column_names = df.columns.tolist()    

    column_names = [re.sub(r'[^\u4e00-\u9fa5]', '', column_name)
                    for column_name in raw_column_names]  # 过滤英文

    if not device_name_list:    
        device_name_list = deal_with_device_name(column_names)

    if not model_list:
        model_list = deal_with_model_name(column_names)

    if not num_list:
        num_list = deal_with_num_name(column_names)

    if not unit_price_list:
        unit_price_list = deal_with_unit_name(column_names)

    if not material_list:
        material_list = deal_with_material_name(column_names)    

    if not dn_list or not pn_list:
        dn_list,pn_list = deal_with_dn_pn(column_names)

    if not all_price_list:
        all_price_list = get_all_price_list(num_list,unit_price_list)
    
    number_list = range(1,len(device_name_list)+1)
      
    output_df = pd.DataFrame({
        '序号': number_list,
        '名称': device_name_list,
        '型号': model_list,
        '公称通径(DN)': dn_list,
        '公称压力(PN)': pn_list,
        '材质': material_list,
        '数量': num_list,
        '单价(元)': unit_price_list,  
        '合计(元)': all_price_list,
    })
    #xlsx_name = os.path.basename(xlsx_path)
    xlsx_name = xlsx_path.split('.xlsx')[0]
    new_xlsx = xlsx_name + "_output.xlsx"

    ## 添加未被选中的列
    column_name_index = range(len(column_names))
    drop_index = list(set(column_name_index) - set(selected_index))
    for i in range(len(drop_index)):
        column_name = raw_column_names[drop_index[i]]
        output_df[column_name] = df[column_name].tolist()

    ## 添加算法处理过的列
    for i in range(len(nlp_selected_index)):
        column_name = raw_column_names[nlp_selected_index[i]]
        output_df[column_name] = df[column_name].tolist()

    output_df.to_excel(f'{xlsx_name}_output.xlsx', index=False)

    print(f"please check  output filepath: {xlsx_name}_output.xlsx")
    print("finish work ..")

    return new_xlsx


main_code("/media/disk4/ldf/NLP/nlp_project/data_excel/111.xlsx")

###这是ldf分支的修改