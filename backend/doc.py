from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import json

from dify import dify_request, dify_chatflow_request


def create_docx(data: dict):
    """
    将结构化 JSON 自动转为美观的 Word 文档

    :param data: JSON 数据（包含 sections）
    """
    doc = Document()
    title = data.get("title", "")
    output_path = f"{title}.docx"

    # ===== 全局字体（中文友好）=====
    style = doc.styles["Normal"]
    style.font.name = "宋体"
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    style.font.size = Pt(12)

    # ===== 文档主标题 =====
    title_p = doc.add_paragraph()
    title_run = title_p.add_run(title)
    title_run.bold = True
    title_run.font.size = Pt(20)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_after = Pt(20)

    # ===== 正文内容 =====
    sections = data.get("sections", [])
    for section in sections:
        # 二级标题
        heading_p = doc.add_heading(section.get("heading", ""), level=2)
        heading_p.paragraph_format.space_before = Pt(12)
        heading_p.paragraph_format.space_after = Pt(6)

        # 正文段落
        content_p = doc.add_paragraph()
        content_run = content_p.add_run(section.get("content", ""))
        content_run.font.size = Pt(12)

        content_p.paragraph_format.first_line_indent = Inches(0.3)
        content_p.paragraph_format.line_spacing = 1.5
        content_p.paragraph_format.space_after = Pt(12)

    # ===== 保存 =====
    doc.save(output_path)
    return output_path


if __name__ == '__main__':
    json = dify_request("今天A股的行情如何")
    create_docx(json)
