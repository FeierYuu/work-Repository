#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档转演示文稿主程序
将包含图片、表格和公式的文档文件转换为演示文稿
"""

import os
import sys
import argparse
import time
from document_reader import DocumentReader
from content_analyzer import ContentAnalyzer
from presentation_generator import PresentationGenerator


def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description='将文档转换为演示文稿')
    parser.add_argument('-i', '--input', required=True, help='输入文档文件路径 (支持 .doc, .docx, .pdf)')
    parser.add_argument('-o', '--output', help='输出演示文稿文件路径 (默认为输入文件名 + .pptx)')
    parser.add_argument('--verbose', action='store_true', help='显示详细处理信息')
    parser.add_argument('--max-slides', type=int, default=50, help='最大幻灯片数量')
    parser.add_argument('--no-style', action='store_false', dest='optimize_style', 
                        help='不应用样式优化')
    parser.add_argument('--decorations', action='store_true', help='添加装饰元素')
    
    return parser.parse_args()

def validate_input_file(file_path):
    """
    验证输入文件是否存在且格式正确
    
    Args:
        file_path: 输入文件路径
        
    Returns:
        bool: 文件是否有效
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 '{file_path}'")
        return False
    
    # 检查文件格式
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in ['.doc', '.docx', '.pdf']:
        print(f"错误: 不支持的文件格式 '{file_ext}'，只支持 .doc, .docx 和 .pdf")
        return False
    
    return True

def determine_output_path(input_path, output_path=None):
    """
    确定输出文件路径
    
    Args:
        input_path: 输入文件路径
        output_path: 指定的输出文件路径
        
    Returns:
        str: 最终的输出文件路径
    """
    if output_path:
        # 如果指定了输出路径，确保使用 .pptx 扩展名
        if not output_path.lower().endswith('.pptx'):
            output_path += '.pptx'
        return output_path
    else:
        # 否则，基于输入文件名生成输出路径
        base_name = os.path.splitext(input_path)[0]
        return f"{base_name}_presentation.pptx"

def convert_document_to_presentation(input_file, output_file, verbose=False, max_slides=50, 
                                    optimize_style=True, add_decorations=False):
    """
    将文档转换为演示文稿
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        verbose: 是否显示详细信息
        max_slides: 最大幻灯片数量
        
    Returns:
        bool: 转换是否成功
    """
    start_time = time.time()
    
    try:
        # 1. 读取文档
        if verbose:
            print(f"正在读取文档: {input_file}")
        
        reader = DocumentReader()
        document_data = reader.read(input_file)
        
        if verbose:
            print(f"成功读取文档，检测到 {len(document_data.get('content', []))} 个文本元素")
            if 'tables' in document_data:
                print(f"检测到 {len(document_data['tables'])} 个表格")
            if 'images' in document_data:
                print(f"检测到 {len(document_data['images'])} 个图片")
        
        # 2. 分析内容
        if verbose:
            print("正在分析文档内容...")
        
        analyzer = ContentAnalyzer()
        content_blocks = analyzer.analyze(document_data)
        
        if verbose:
            print(f"内容分析完成，生成 {len(content_blocks)} 个内容块")
        
        # 生成演示文稿
        if verbose:
            print(f"正在生成演示文稿: {output_file}")
        
        generator = PresentationGenerator()
        
        # 如果内容块数量超过最大幻灯片限制，进行截断
        if len(content_blocks) > max_slides:
            if verbose:
                print(f"警告: 内容块数量 ({len(content_blocks)}) 超过最大幻灯片限制 ({max_slides})")
                print(f"将只处理前 {max_slides} 个内容块")
            content_blocks = content_blocks[:max_slides]
        
        # 设置样式优化选项
        style_options = {}
        if optimize_style:
            if verbose:
                print("应用样式优化...")
            style_options['add_decorations'] = add_decorations
        else:
            style_options = None
        
        output_path = generator.generate(content_blocks, output_file, style_options)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✓ 转换完成！")
        print(f"输出文件: {output_path}")
        print(f"处理时间: {processing_time:.2f} 秒")
        
        return True
        
    except Exception as e:
        print(f"错误: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False

def main():
    """
    主函数
    """
    print("=" * 60)
    print("文档转演示文稿工具")
    print("支持格式: .doc, .docx, .pdf")
    print("=" * 60)
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 验证输入文件
    if not validate_input_file(args.input):
        sys.exit(1)
    
    # 确定输出路径
    output_file = determine_output_path(args.input, args.output)
    
    # 初始化读取器，用于后续可能的清理操作
    reader = None
    try:
        # 创建读取器实例
        reader = DocumentReader()
        
        # 转换文档
        success = convert_document_to_presentation(
            input_file=args.input,
            output_file=output_file,
            verbose=args.verbose,
            max_slides=args.max_slides,
            optimize_style=args.optimize_style,
            add_decorations=args.decorations
        )
        
        if not success:
            sys.exit(1)
    finally:
        # 清理临时文件
        if reader and hasattr(reader, 'cleanup_temp_files'):
            reader.cleanup_temp_files()


if __name__ == "__main__":
    main()