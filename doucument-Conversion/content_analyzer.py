#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容分析模块
负责识别文档中的标题、正文、图片、表格和公式，并进行组织
"""

from typing import Dict, List, Any, Tuple
import re


class ContentAnalyzer:
    """
    内容分析器类，用于分析文档内容结构
    """
    
    def __init__(self):
        # 定义标题模式（用于PDF文档）
        self.title_patterns = [
            # 匹配类似 "1. 标题"、"2.1 子标题" 的格式
            re.compile(r'^\d+\.\s+.*$'),
            re.compile(r'^\d+\.\d+\s+.*$'),
            # 匹配全大写的行
            re.compile(r'^[A-Z\s\W]+$'),
        ]
        
        # 公式模式（简化版）
        self.formula_patterns = [
            re.compile(r'\\\[.*?\\\]'),  # 匹配 $$ 公式块
            re.compile(r'\\\(.*?\\\)'),  # 匹配 $ 行内公式
            re.compile(r'\$.+?\$'),      # 匹配 $ 公式
        ]
        # LaTeX公式提取模式
        self.latex_formula_pattern = re.compile(r'(\$[^$]*\$)')
    
    def analyze(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        分析文档内容，识别结构
        
        Args:
            document_data: 从DocumentReader获取的文档数据
            
        Returns:
            List[Dict]: 结构化的内容块列表
        """
        content_blocks = []
        
        # 分析文本内容
        if 'content' in document_data:
            content_blocks.extend(self._analyze_text_content(document_data['content']))
        
        # 分析表格内容
        if 'tables' in document_data and document_data['tables']:
            content_blocks.extend(self._analyze_tables(document_data['tables']))
        
        # 分析图片内容
        if 'images' in document_data and document_data['images']:
            for img_idx, image_info in enumerate(document_data['images']):
                content_blocks.append({
                    'type': 'image',
                    'path': image_info.get('path'),
                    'description': image_info.get('description', ''),
                    'position': image_info.get('position', len(content_blocks))
                })
        
        # 对内容块进行排序和组织
        content_blocks = self._organize_content_blocks(content_blocks)
        
        return content_blocks
    
    def _analyze_text_content(self, content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析文本内容，识别标题和正文
        
        Args:
            content: 文本内容列表
            
        Returns:
            List[Dict]: 分析后的内容块列表
        """
        blocks = []
        current_paragraphs = []
        current_title = None
        
        for item in content:
            text = item['text']
            
            # 检查是否包含公式
            has_formula = self._contains_formula(text)
            
            # 判断是否为标题
            is_heading = self._is_heading(item)
            
            if is_heading:
                # 如果当前有积累的段落，先将其添加为正文块
                if current_paragraphs:
                    blocks.append({
                        'type': 'paragraph',
                        'content': '\n'.join(current_paragraphs),
                        'title': current_title
                    })
                    current_paragraphs = []
                
                # 将当前标题作为新的标题块
                current_title = text
                blocks.append({
                    'type': 'heading',
                    'content': text,
                    'level': self._determine_heading_level(text, item)
                })
            elif has_formula:
                # 检查是否包含LaTeX公式
                latex_matches = self.latex_formula_pattern.findall(text)
                
                if latex_matches:
                    # 提取LaTeX公式
                    formula_content = ' '.join(latex_matches)
                    # 处理包含公式的内容
                    blocks.append({
                        'type': 'formula',
                        'content': formula_content,
                        'full_text': text,  # 保存完整文本
                        'is_latex': True,
                        'title': current_title
                    })
                else:
                    # 处理包含其他类型公式的内容
                    blocks.append({
                        'type': 'formula',
                        'content': text,
                        'title': current_title
                    })
            else:
                # 积累正文段落
                current_paragraphs.append(text)
        
        # 添加最后积累的段落
        if current_paragraphs:
            blocks.append({
                'type': 'paragraph',
                'content': '\n'.join(current_paragraphs),
                'title': current_title
            })
        
        return blocks
    
    def _is_heading(self, item: Dict[str, Any]) -> bool:
        """
        判断是否为标题
        
        Args:
            item: 内容项
            
        Returns:
            bool: 是否为标题
        """
        # 如果已经标记为标题，直接返回True
        if item.get('type') == 'heading':
            return True
        
        text = item['text']
        
        # 基于样式判断
        if 'font_size' in item and item['font_size'] is not None:
            # 字体较大的通常是标题
            if item['font_size'] > 14:
                return True
        
        # 基于模式匹配
        for pattern in self.title_patterns:
            if pattern.match(text):
                return True
        
        # 基于文本特征
        # 标题通常较短且首字母大写
        words = text.split()
        if len(words) > 0 and len(words) < 10 and words[0].istitle():
            # 检查是否大部分单词首字母大写
            capitalized = sum(1 for word in words if word.istitle())
            if capitalized / len(words) > 0.7:
                return True
        
        return False
    
    def _determine_heading_level(self, text: str, item: Dict[str, Any]) -> int:
        """
        确定标题级别
        
        Args:
            text: 标题文本
            item: 内容项
            
        Returns:
            int: 标题级别（1-6）
        """
        # 基于样式名称
        if 'style_name' in item:
            style_name = item['style_name'].lower()
            for i in range(1, 7):
                if f'heading {i}' in style_name or f'标题{i}' in style_name:
                    return i
        
        # 基于字体大小
        if 'font_size' in item and item['font_size'] is not None:
            font_size = item['font_size']
            if font_size >= 24:
                return 1
            elif font_size >= 20:
                return 2
            elif font_size >= 16:
                return 3
            elif font_size >= 14:
                return 4
            else:
                return 5
        
        # 基于模式（如1. 2.1 等）
        level_match = re.match(r'^(\d+)(\.\d+)*\s', text)
        if level_match:
            parts = level_match.group(0).strip().split('.')
            return len(parts)
        
        return 1  # 默认级别
    
    def _contains_formula(self, text: str) -> bool:
        """
        检查文本是否包含公式
        
        Args:
            text: 文本内容
            
        Returns:
            bool: 是否包含公式
        """
        # 优先检查LaTeX公式格式
        if self.latex_formula_pattern.search(text):
            return True
            
        for pattern in self.formula_patterns:
            if pattern.search(text):
                return True
        
        # 检查是否包含数学符号
        math_symbols = ['+', '-', '=', '×', '÷', 'π', '√', '∫', '∑', '∏', '^', '_']
        # 检查是否有多个数学符号连续出现，这可能是公式
        symbol_count = sum(1 for char in text if char in math_symbols)
        if symbol_count > 1:
            return True
            
        return False
    
    def _extract_formula(self, text: str) -> str:
        """
        从文本中提取公式内容
        
        Args:
            text: 包含公式的文本
            
        Returns:
            str: 提取的公式内容
        """
        # 提取LaTeX公式
        latex_matches = self.latex_formula_pattern.findall(text)
        if latex_matches:
            return ' '.join(latex_matches)
        
        # 查找包含数学符号的部分
        math_symbols = ['+', '-', '=', '×', '÷', 'π', '√', '∫', '∑', '∏', '^', '_']
        words = text.split()
        formula_parts = []
        
        for word in words:
            if any(symbol in word for symbol in math_symbols):
                formula_parts.append(word)
        
        if formula_parts:
            return ' '.join(formula_parts)
            
        return text  # 如果没有找到明确的公式部分，返回原文本
    
    def _analyze_tables(self, tables: List[List[List[str]]]) -> List[Dict[str, Any]]:
        """
        分析表格内容
        
        Args:
            tables: 表格数据列表
            
        Returns:
            List[Dict]: 表格内容块列表
        """
        table_blocks = []
        
        for i, table in enumerate(tables):
            # 过滤空表格
            non_empty_rows = [row for row in table if any(cell.strip() for cell in row)]
            if not non_empty_rows:
                continue
            
            # 为表格添加标题（可以从上下文推断）
            table_title = f"表格{i+1}"
            
            table_blocks.append({
                'type': 'table',
                'content': non_empty_rows,
                'title': table_title
            })
        
        return table_blocks
    
    def _organize_content_blocks(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        组织内容块，建立层次结构
        
        Args:
            blocks: 内容块列表
            
        Returns:
            List[Dict]: 组织后的内容块列表
        """
        # 首先根据position属性排序内容块（如果存在）
        blocks_with_position = [block for block in blocks if 'position' in block]
        blocks_without_position = [block for block in blocks if 'position' not in block]
        
        # 对有position的块进行排序
        blocks_with_position.sort(key=lambda x: x['position'])
        
        # 合并排序后的块和无position的块
        sorted_blocks = blocks_with_position + blocks_without_position
        
        # 组织内容到章节中
        organized_blocks = []
        current_section = None
        
        for block in sorted_blocks:
            if block['type'] == 'heading':
                # 开始新的节
                current_section = {
                    'type': 'section',
                    'title': block['content'],
                    'level': block.get('level', 1),
                    'content': []
                }
                organized_blocks.append(current_section)
            elif current_section is not None:
                # 添加内容到当前节
                current_section['content'].append(block)
            else:
                # 如果没有当前节，直接添加
                organized_blocks.append(block)
        
        return organized_blocks
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        文本摘要，用于简化演示文稿中的内容
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            str: 摘要后的文本
        """
        # 简单的摘要逻辑，实际应用可能需要使用NLP库进行更智能的摘要
        if len(text) <= max_length:
            return text
        
        # 尝试在句子边界截断
        sentences = re.split(r'(?<=[。！？.!?])\s+', text)
        summary = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) + 4 > max_length:  # +4 用于考虑省略号
                break
            summary.append(sentence)
            current_length += len(sentence)
        
        if summary:
            result = ' '.join(summary) + '...'
            # 确保最终结果不超过最大长度
            if len(result) > max_length:
                return text[:max_length-3] + '...'  # 直接截断并添加省略号
            return result
        else:
            return text[:max_length-3] + '...'  # 直接截断并添加省略号


if __name__ == "__main__":
    # 测试代码
    analyzer = ContentAnalyzer()
    print("内容分析模块已创建")