# 文档转演示文稿工具


github：https://github.com/FeierYuu/work-Repository/tree/main/doucument-Conversion

将包含图片、表格和公式的文档文件（doc、docx、pdf）转换为演示文稿（pptx）。

## 功能特点

- 支持多种文档格式：`.doc`, `.docx`, `.pdf`
- 智能识别文档结构：自动识别标题、正文、表格和公式
- 优化的演示文稿布局：每张幻灯片表达一个完整思想，配有标题
- 美观的样式设计：大字体、横向排版、合理的颜色搭配
- 命令行操作：简单易用的命令行接口

## 安装说明
 
### 前提条件

- Python 3.7 或更高版本
- pip 包管理器

### 安装依赖

```bash
pip install python-docx PyPDF2 python-pptx pillow pdfplumber pytesseract
```

## 使用方法

### 基本使用

```bash
python main.py -i 输入文件路径
```

### 示例

```bash
# 转换docx文件
python main.py -i 报告.docx

# 转换pdf文件并指定输出路径
python main.py -i 论文.pdf -o 演示文稿.pptx

# 启用详细输出模式
python main.py -i 文档.doc -o 成果.pptx --verbose

# 添加装饰元素
python main.py -i 演示.docx -o 美化版.pptx --decorations

# 限制最大幻灯片数量
python main.py -i 长文档.pdf -o 精简版.pptx --max-slides 20

# 禁用样式优化
python main.py -i 文档.docx -o 原始版.pptx --no-style
```

## 命令行参数

- `-i`, `--input`：输入文档文件路径（必需）
- `-o`, `--output`：输出演示文稿文件路径（可选，默认为输入文件名 + "_presentation.pptx"）
- `--verbose`：显示详细处理信息
- `--max-slides`：最大幻灯片数量（默认：50）
- `--no-style`：不应用样式优化
- `--decorations`：添加装饰元素

## 工作原理

1. **文档读取**：使用专用库读取不同格式的文档内容
2. **内容分析**：智能识别标题、正文、表格和公式，组织内容结构
3. **演示文稿生成**：将分析后的内容转换为幻灯片，每张幻灯片表达一个完整思想
4. **样式优化**：应用美观的排版和样式，确保字体大小合理、布局清晰

## 项目结构

```
ai-work/
├── main.py                # 主程序入口
├── document_reader.py     # 文档读取模块
├── content_analyzer.py    # 内容分析模块
├── presentation_generator.py  # 演示文稿生成模块
├── style_optimizer.py     # 样式优化模块
├── tests/                 # 测试目录
│   └── test_document_converter.py  # 测试用例
└── README.md              # 本说明文件
```

## 注意事项

1. **文档格式**：确保文档格式规范，标题、段落结构清晰，有助于更好地识别内容
2. **公式识别**：目前支持简单的公式识别，复杂公式可能需要手动调整
3. **图片处理**：PDF和DOCX中的图片会被保留，但可能需要根据实际情况调整大小和位置
4. **性能考虑**：处理大文件时可能需要较长时间，建议合理设置`--max-slides`参数

## 常见问题

### Q: 支持哪些操作系统？
A: 支持所有主流操作系统（Windows、macOS、Linux），只要安装了Python和相关依赖。

### Q: 如何提高转换质量？
A: 确保原始文档结构清晰，使用标准的标题样式和段落格式。

### Q: 生成的演示文稿能否进一步编辑？
A: 是的，生成的PPTX文件可以在Microsoft PowerPoint或其他兼容软件中进一步编辑和调整。

## 许可证

本项目采用MIT许可证。

## 更新日志

### v1.0.0
- 初始版本
- 支持DOC、DOCX、PDF格式转换
- 实现标题识别、内容组织功能
- 添加样式优化和排版调整