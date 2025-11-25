#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档转演示文稿工具测试用例
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from document_reader import DocumentReader
from content_analyzer import ContentAnalyzer
from presentation_generator import PresentationGenerator


class TestDocumentConverter(unittest.TestCase):
    """
    文档转换器测试类
    """
    
    def setUp(self):
        """
        测试前的设置
        """
        # 创建临时目录用于测试文件
        self.temp_dir = tempfile.mkdtemp()
        
        # 创建测试用的读取器、分析器和生成器
        self.reader = DocumentReader()
        self.analyzer = ContentAnalyzer()
        self.generator = PresentationGenerator()
    
    def tearDown(self):
        """
        测试后的清理
        """
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_document_reader_initialization(self):
        """
        测试文档读取器初始化
        """
        self.assertIsInstance(self.reader, DocumentReader)
    
    def test_content_analyzer_initialization(self):
        """
        测试内容分析器初始化
        """
        self.assertIsInstance(self.analyzer, ContentAnalyzer)
    
    def test_presentation_generator_initialization(self):
        """
        测试演示文稿生成器初始化
        """
        self.assertIsInstance(self.generator, PresentationGenerator)
    
    @patch('document_reader.Document')
    def test_read_docx_mock(self, mock_document):
        """
        模拟测试DOCX文件读取
        """
        # 设置模拟对象
        mock_doc = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.text = "测试段落"
        mock_paragraph.style.name = "Normal"
        mock_run = MagicMock()
        mock_run.font.size.pt = 12
        mock_paragraph.runs = [mock_run]
        mock_doc.paragraphs = [mock_paragraph]
        mock_doc.tables = []
        mock_document.return_value = mock_doc
        
        # 创建一个临时的docx文件（空文件即可，因为我们使用mock）
        temp_docx = os.path.join(self.temp_dir, "test.docx")
        with open(temp_docx, 'w') as f:
            f.write("dummy content")
        
        # 测试读取（实际会使用mock）
        with patch('document_reader.DocumentReader._read_docx', 
                  return_value={'content': [{'text': '测试段落', 'type': 'paragraph', 'font_size': 12}], 
                               'tables': [], 'format': 'docx', 'file_path': temp_docx}):
            result = self.reader.read(temp_docx)
            self.assertEqual(result['format'], 'docx')
            self.assertEqual(len(result['content']), 1)
    
    def test_content_analyzer_summarize_text(self):
        """
        测试文本摘要功能
        """
        long_text = "这是一段很长的文本，用于测试摘要功能。文档转演示文稿工具需要能够将长文本自动摘要，以便在幻灯片中更好地显示。摘要后的文本应该简洁明了，同时保留关键信息。"
        summarized = self.analyzer.summarize_text(long_text, max_length=50)
        self.assertTrue(len(summarized) <= 50)
        self.assertTrue(summarized.endswith('...'))
    
    def test_is_heading(self):
        """
        测试标题识别功能
        """
        # 测试基于字体大小的标题识别
        heading_item = {'text': '这是一个标题', 'font_size': 24}
        self.assertTrue(self.analyzer._is_heading(heading_item))
        
        # 测试基于模式的标题识别
        numbered_heading = {'text': '1. 第一章', 'font_size': 12}
        self.assertTrue(self.analyzer._is_heading(numbered_heading))
        
        # 测试普通段落
        normal_paragraph = {'text': '这是一个普通段落，不应该被识别为标题。', 'font_size': 12}
        self.assertFalse(self.analyzer._is_heading(normal_paragraph))
    
    def test_contains_formula(self):
        """
        测试公式识别功能
        """
        # 测试包含公式的文本
        formula_text = "这是一个包含公式的文本: E = mc^2"
        self.assertTrue(self.analyzer._contains_formula(formula_text))
        
        # 测试LaTeX格式的公式
        latex_formula = "这是一个LaTeX公式: $\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$"
        self.assertTrue(self.analyzer._contains_formula(latex_formula))
        
        # 测试普通文本
        normal_text = "这是一个不包含公式的普通文本。"
        self.assertFalse(self.analyzer._contains_formula(normal_text))
    
    @patch('presentation_generator.Presentation')
    def test_presentation_generation_mock(self, mock_presentation):
        """
        模拟测试演示文稿生成
        """
        # 设置模拟对象
        mock_prs = MagicMock()
        mock_presentation.return_value = mock_prs
        
        # 创建测试内容块
        test_content = [
            {
                'type': 'section',
                'title': '测试章节',
                'level': 1,
                'content': [
                    {
                        'type': 'paragraph',
                        'content': '这是测试章节的内容。',
                        'title': '测试章节'
                    }
                ]
            }
        ]
        
        # 测试生成
        output_path = os.path.join(self.temp_dir, "output.pptx")
        result = self.generator.generate(test_content, output_path)
        
        # 验证结果
        self.assertEqual(result, output_path)
        mock_prs.save.assert_called_once_with(output_path)


if __name__ == '__main__':
    unittest.main()