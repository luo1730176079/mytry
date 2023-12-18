from flask import Flask, request
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
from main import main_code



app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 从表单中获取用户输入的内容
        input_excel = request.form['user_input']

        output_excel = main_code(input_excel)

        # 返回内容
        return f'标准报价单地址为：{output_excel}'
    else:
        # 显示一个简单的表单，让用户输入内容
        return '''
        <form method="post" action="/">
            <label for="user_input">请输入excel地址：</label>
            <input type="text" id="user_input" name="user_input" required>
            <input type="submit" value="提交">
        </form>
        '''

if __name__ == '__main__':
    # 在8080端口运行应用
    app.run(port=8080)