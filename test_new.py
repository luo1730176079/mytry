import os

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
from main import main_code


if __name__ == '__main__':
    input_excel = input("请输入excel地址:")
    output_excel = main_code(input_excel)
    print("标准报价单输出地址为：{}".format(output_excel))