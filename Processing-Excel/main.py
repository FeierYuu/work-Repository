#!/usr/bin/env python3
"""
课程表处理主程序
从Excel文件读取教师课程信息，并生成PDF格式的教师时间表
"""

import sys
import argparse
from schedule_processor import ExcelReader
from pdf_generator import PDFGenerator


def main():
    parser = argparse.ArgumentParser(description='教师课程表处理工具')
    parser.add_argument(
        '--input',
        default='ITsTiM_Raspisanie_2_polugodie_25-26_mag__pechat.xlsx',
        help='Excel输入文件路径'
    )
    parser.add_argument(
        '--output',
        default='teacher_schedules.pdf',
        help='PDF输出文件路径'
    )
    parser.add_argument(
        '--teacher',
        help='只生成指定教师的课程表（格式: "Фамилия И.О."）'
    )
    parser.add_argument(
        '--list-teachers',
        action='store_true',
        help='列出所有可用的教师'
    )

    args = parser.parse_args()

    # 读取Excel文件
    print(f"正在读取文件: {args.input}")
    reader = ExcelReader(args.input)

    try:
        reader.load()
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.input}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 读取文件失败 - {e}")
        sys.exit(1)

    # 列出所有教师
    teachers = reader.get_all_teachers()

    if args.list_teachers:
        print(f"\n找到 {len(teachers)} 位教师:")
        for i, teacher in enumerate(teachers, 1):
            print(f"  {i:2d}. {teacher}")
        return

    # 处理指定教师或所有教师
    if args.teacher:
        if args.teacher not in teachers:
            print(f"错误: 未找到教师 '{args.teacher}'")
            print(f"可用教师: {', '.join(teachers[:5])}...")
            sys.exit(1)

        print(f"正在生成 {args.teacher} 的课程表...")
        schedules = {args.teacher: reader.get_teacher_schedule(args.teacher)}
    else:
        print(f"正在生成 {len(teachers)} 位教师的课程表...")
        schedules = reader.get_all_schedules()

    # 生成PDF
    print(f"正在生成PDF文件: {args.output}")
    generator = PDFGenerator(args.output)
    generator.create_schedule_pdf(schedules)

    print(f"完成! PDF文件已保存到: {args.output}")

    # 显示统计信息
    total_lessons = sum(len(entries) for entries in schedules.values())
    print(f"\n统计信息:")
    print(f"  教师数量: {len(schedules)}")
    print(f"  课程总数: {total_lessons}")


if __name__ == '__main__':
    main()
