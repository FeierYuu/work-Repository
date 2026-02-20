"""
PDF生成模块
将教师课程表生成为PDF格式的时间表
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import List, Dict
import os

from schedule_processor import ScheduleEntry


class PDFGenerator:
    """PDF时间表生成器"""

    # 星期顺序
    DAY_ORDER = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

    def __init__(self, output_path: str):
        self.output_path = output_path
        self.doc = None
        self.story = []
        self.styles = getSampleStyleSheet()

        # 设置支持俄语的字体
        self._setup_fonts()

    def _setup_fonts(self):
        """设置字体以支持俄语"""
        # 尝试使用系统字体
        font_paths = [
            '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',  # macOS - 支持俄语
            '/System/Library/Fonts/Supplemental/Arial.ttf',  # macOS
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            'C:\\Windows\\Fonts\\arial.ttf',  # Windows
        ]

        self.font_name = 'Helvetica'  # 默认字体
        font_registered = False

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # 注册字体
                    pdfmetrics.registerFont(TTFont('ArialUnicode', font_path))
                    self.font_name = 'ArialUnicode'
                    font_registered = True
                    print(f"已注册字体: {font_path}")
                    break
                except Exception as e:
                    print(f"字体注册失败 {font_path}: {e}")
                    continue

        if not font_registered:
            print("警告: 未找到支持俄语的字体，PDF可能显示为方框")

        # 创建自定义样式
        self.styles.add(ParagraphStyle(
            name='RussianHeader',
            parent=self.styles['Heading1'],
            fontName=self.font_name,
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12,
        ))
        self.styles.add(ParagraphStyle(
            name='RussianNormal',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=10,
        ))
        self.styles.add(ParagraphStyle(
            name='RussianSmall',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=9,
        ))

    def create_schedule_pdf(self, schedules: Dict[str, List[ScheduleEntry]]):
        """创建包含所有教师时间表的PDF"""
        self.doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )

        # 为每个教师生成时间表
        for teacher, entries in schedules.items():
            self._add_teacher_schedule(teacher, entries)
            self.story.append(PageBreak())

        # 构建PDF
        self.doc.build(self.story)

    def _add_teacher_schedule(self, teacher_name: str, entries: List[ScheduleEntry]):
        """添加单个教师的时间表"""
        # 标题
        title_style = self.styles.get('RussianHeader', self.styles['Heading1'])
        title = Paragraph(f"РАСПИСАНИЕ<br/>{teacher_name}", title_style)
        self.story.append(title)
        self.story.append(Spacer(1, 0.5*cm))

        # 按星期分组
        schedule_by_day = {day: [] for day in self.DAY_ORDER}
        for entry in entries:
            if entry.day in schedule_by_day:
                schedule_by_day[entry.day].append(entry)

        # 创建时间表表格
        table_data = []

        # 表头
        table_data.append([
            'День', 'Время', 'Предмет', 'Аудитория',
            'Группа', 'Тип занятия'
        ])

        # 添加每天的课程
        for day in self.DAY_ORDER:
            day_entries = schedule_by_day.get(day, [])
            if day_entries:
                # 合并同一天的第一个单元格
                first_entry = True
                for entry in day_entries:
                    if first_entry:
                        day_cell = day
                        first_entry = False
                    else:
                        day_cell = ''

                    table_data.append([
                        day_cell,
                        entry.time,
                        entry.subject[:40] + '...' if len(entry.subject) > 40 else entry.subject,
                        entry.room,
                        entry.group,
                        entry.activity_type
                    ])

        # 创建表格
        if len(table_data) > 1:
            # 列宽: [День, Время, Предмет, Аудитория, Группа, Тип занятия]
            table = Table(table_data, colWidths=[2.2*cm, 2.2*cm, 7.5*cm, 1.8*cm, 1.8*cm, 2.2*cm])

            # 设置表格样式
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))

            self.story.append(table)
        else:
            # 没有课程数据
            no_data = Paragraph("Нет данных о расписании", self.styles['Normal'])
            self.story.append(no_data)

    def create_single_teacher_pdf(self, teacher_name: str, entries: List[ScheduleEntry]):
        """创建单个教师的PDF"""
        self.doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm
        )

        self._add_teacher_schedule(teacher_name, entries)
        self.doc.build(self.story)


if __name__ == '__main__':
    # 测试代码
    from schedule_processor import ExcelReader

    reader = ExcelReader('ITsTiM_Raspisanie_2_polugodie_25-26_mag__pechat.xlsx')
    reader.load()

    teachers = reader.get_all_teachers()
    if teachers:
        test_teacher = teachers[0]
        schedule = reader.get_teacher_schedule(test_teacher)

        print(f"教师: {test_teacher}")
        print(f"课程数量: {len(schedule)}")
        for entry in schedule[:5]:
            print(f"  {entry.day} {entry.time}: {entry.subject}")
