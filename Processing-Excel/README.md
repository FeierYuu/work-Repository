# 教师课程表处理工具

从Excel文件读取教师课程信息，并生成PDF格式的教师时间表。

## 功能

- 读取Excel格式的课程表文件
- 自动提取所有教师及其课程信息
- 生成时间表格式的PDF文件
- 支持生成所有教师或指定教师的课程表

## 安装依赖

```bash
pip install openpyxl reportlab
```

或使用虚拟环境：

```bash
source .venv/bin/activate
pip install openpyxl reportlab
```

## 使用方法

### 列出所有教师

```bash
python main.py --list-teachers
```

### 生成所有教师的课程表

```bash
python main.py --output all_schedules.pdf
```

### 生成指定教师的课程表

```bash
python main.py --teacher "Игонина Е.В." --output igonina_schedule.pdf
```

### 指定输入文件

```bash
python main.py --input your_schedule.xlsx --output output.pdf
```

## 项目结构

- `schedule_processor.py` - Excel文件读取器
- `pdf_generator.py` - PDF生成器
- `main.py` - 主程序入口

## 示例

找到40位教师，共418节课程。
