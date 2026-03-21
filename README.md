# Viterbi
## 环境依赖
在运行前，请先安装项目所需依赖包，确保语料库和input文件都在正确位置：
```bash
pip install -r requirements.txt
```

#### 二字模型
```bash
python main.py <data/input.txt >data/output.txt
```

#### 二词模型
请先将bigram.py从src文件夹中移到当前文件夹下
```bash
python bigram.py <data/input.txt >data/output.txt
```