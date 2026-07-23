import os, json, io
from flask import Flask, request, jsonify, send_file, send_from_directory
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from fpdf import FPDF
from fpdf.enums import TableCellFillMode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR)

BATCH_FILLS = [
    PatternFill(start_color='D5F5E3', end_color='D5F5E3', fill_type='solid'),  # green
    PatternFill(start_color='D6E4F0', end_color='D6E4F0', fill_type='solid'),  # blue
    PatternFill(start_color='FEF9C3', end_color='FEF9C3', fill_type='solid'),  # yellow
]


def build_xlsx(data):
    wb = Workbook()
    ws = wb.active
    ws.title = '排班表'

    thin = Side(style='thin')
    border_all = Border(left=thin, right=thin, top=thin, bottom=thin)
    title_font = Font(name='微软雅黑', bold=True, size=14)
    hdr_font = Font(name='微软雅黑', bold=True, size=11, color='FFFFFF')
    data_font = Font(name='微软雅黑', size=10)
    note_font = Font(name='微软雅黑', size=9, italic=True, color='555555')
    hdr_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    center = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left_wrap = Alignment(horizontal='left', vertical='center', wrap_text=True)

    batchnames = data.get('batchNames', ['批号1', '批号2', '批号3'])
    headers = ['日期', batchnames[0], batchnames[1], batchnames[2],
               '早班人员', '小夜班人员', '大夜班人员', '休班人员']
    ncols = len(headers)
    last_letter = get_column_letter(ncols)

    col_widths = [16, 36, 36, 36, 30, 30, 30, 16]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # Row 1: Title
    ws.merge_cells(f'A1:{last_letter}1')
    c = ws['A1']
    c.value = data.get('batchLabel', '排班表')
    c.font = title_font
    c.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[1].height = 38

    # Row 2: Info
    ws.merge_cells(f'A2:{last_letter}2')
    c = ws['A2']
    dr = data.get('dateRange', '')
    c.value = '周期: ' + dr if dr else ''
    c.font = note_font
    c.alignment = Alignment(horizontal='left', vertical='center')
    ws.row_dimensions[2].height = 22

    # Row 3: Header
    for i, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=i, value=h)
        cell.font = hdr_font
        cell.fill = hdr_fill
        cell.alignment = center
        cell.border = border_all
    ws.row_dimensions[3].height = 30

    # Data
    rows = data.get('rows', [])
    for idx, r in enumerate(rows):
        rn = 4 + idx
        vals = [r.get(k, '') for k in
                ['date', 'batch1', 'batch2', 'batch3', 'morning', 'evening', 'night', 'off']]
        for col, val in enumerate(vals, 1):
            cell = ws.cell(row=rn, column=col, value=val)
            cell.font = data_font
            cell.border = border_all
            cell.alignment = center if col == 1 else left_wrap
            if 2 <= col <= 4:
                cell.fill = BATCH_FILLS[col - 2]
        ws.row_dimensions[rn].height = 72

    # Summary
    sr = 4 + len(rows)
    ws.merge_cells(f'A{sr}:D{sr}')
    c = ws.cell(row=sr, column=1, value='合计')
    c.font = Font(name='微软雅黑', bold=True, size=10)
    c.alignment = center
    c.border = border_all
    for col in range(2, ncols + 1):
        ws.cell(row=sr, column=col).border = border_all
    ws.cell(row=sr, column=5, value=data.get('summaryText', '')).font = Font(name='微软雅黑', size=10)
    ws.cell(row=sr, column=5).alignment = left_wrap
    ws.cell(row=sr, column=5).border = border_all
    ws.row_dimensions[sr].height = 25

    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out


@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')


@app.route('/export', methods=['POST'])
def export():
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'no data'}), 400
    try:
        buf = build_xlsx(payload)
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='57车间排班表.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== PDF Export =====

class SchedulePDF(FPDF):
    FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

    def __init__(self):
        super().__init__('L', 'mm', 'A4')  # Landscape 297x210mm
        self.set_auto_page_break(auto=False)
        # Register Noto Sans SC (Chinese)
        font_dir = self.FONT_DIR
        self.add_font('NotoSC', '', os.path.join(font_dir, 'NotoSansSC-Regular-subset.ttf'))
        self.add_font('NotoSC', 'B', os.path.join(font_dir, 'NotoSansSC-Bold-subset.ttf'))

    def footer(self):
        self.set_y(-12)
        self.set_font('NotoSC', '', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'57\u8f66\u95f4\u6392\u73ed\u8868 - \u7b2c {self.page_no()}/{{nb}} \u9875', align='C')


def _draw_cell(pdf, x, y, w, h, text, align='L', font_size=None, bold=False,
               fill_color=None, text_color=None, border=True):
    """Draw a single PDF cell with consistent border and fill."""
    fam = 'NotoSC'
    style = 'B' if bold else ''
    if font_size:
        pdf.set_font(fam, style, font_size)
    if text_color:
        pdf.set_text_color(*text_color)

    pdf.set_xy(x, y)

    if fill_color:
        pdf.set_fill_color(*fill_color)
        pdf.cell(w, h, text, border=1 if border else 0, fill=True, align=align)
    else:
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(w, h, text, border=1 if border else 0, fill=False, align=align)


def build_pdf(data):
    pdf = SchedulePDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Colors
    HDR_BG = (68, 114, 196)
    HDR_FG = (255, 255, 255)
    BATCH_COLORS = [
        (213, 245, 227),  # green
        (214, 228, 240),  # blue
        (254, 249, 195),  # yellow
    ]
    SUM_BG = (240, 240, 240)
    BLACK = (30, 30, 30)
    GRAY = (120, 120, 120)

    batchnames = data.get('batchNames', ['批号1', '批号2', '批号3'])
    headers = ['日期', batchnames[0], batchnames[1], batchnames[2],
               '早班人员', '小夜班人员', '大夜班人员', '休班人员']

    # Column widths (mm) for A4 landscape usable area ~277mm
    col_w = [22, 48, 48, 48, 33, 33, 33, 12]  # sum = 277
    ncols = len(col_w)

    title = data.get('batchLabel', '57车间排班表')
    date_range = data.get('dateRange', '')

    # Page geometry
    margin_left = 10
    page_w = 297
    content_start_y = 15
    max_y = 190  # stop before footer

    # --- Title ---
    pdf.set_xy(margin_left, content_start_y)
    _draw_cell(pdf, margin_left, content_start_y, page_w - 20, 10, title,
               align='C', font_size=13, bold=True, text_color=BLACK, border=False)
    cy = content_start_y + 12

    # --- Date range (use NotoSC) ---
    pdf.set_xy(margin_left, cy)
    pdf.set_font('NotoSC', '', 8)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, f'周期: {date_range}', align='L')
    cy += 9

    ROW_H = 8  # fixed row height

    def draw_header(y):
        x = margin_left
        for i, h in enumerate(headers):
            _draw_cell(pdf, x, y, col_w[i], ROW_H, h,
                       align='C', font_size=7, bold=True,
                       text_color=HDR_FG, fill_color=HDR_BG)
            x += col_w[i]
        return y + ROW_H + 1

    def draw_data_row(y, vals):
        x = margin_left
        for col_i, val in enumerate(vals):
            align = 'C' if col_i == 0 else 'L'
            display_text = str(val)
            # Truncate if too long
            max_chars = int(col_w[col_i] / 1.6)
            if len(display_text) > max_chars:
                display_text = display_text[:max_chars - 2] + '..'
            fill = BATCH_COLORS[col_i - 1] if 1 <= col_i <= 3 else None
            _draw_cell(pdf, x, y, col_w[col_i], ROW_H, display_text,
                       align=align, font_size=7, fill_color=fill, text_color=BLACK)
            x += col_w[col_i]
        return y + ROW_H

    def draw_summary_row(y, summary_text=''):
        x = margin_left
        merge_w = sum(col_w[:4])
        pdf.set_font('NotoSC', 'B', 8)
        pdf.set_fill_color(*SUM_BG)
        pdf.set_text_color(*BLACK)
        pdf.set_xy(x, y)
        pdf.cell(merge_w, ROW_H, '合计', border=1, fill=True, align='C')
        x += merge_w

        sum_remain = sum(col_w[4:])
        pdf.set_font('NotoSC', '', 7)
        pdf.set_fill_color(*SUM_BG)
        pdf.set_xy(x, y)
        display = str(summary_text)[:60] if summary_text else ''
        pdf.cell(sum_remain, ROW_H, display, border=1, fill=True, align='L')
        return y + ROW_H

    # --- Draw header ---
    cy = draw_header(cy)

    rows = data.get('rows', [])
    for idx, r in enumerate(rows):
        vals = [r.get(k, '') for k in
                ['date', 'batch1', 'batch2', 'batch3', 'morning', 'evening', 'night', 'off']]

        if cy + ROW_H > max_y:
            pdf.add_page()
            cy = content_start_y
            cy = draw_header(cy)

        cy = draw_data_row(cy, vals)

    # Summary row
    cy += 3
    if cy + ROW_H > max_y:
        pdf.add_page()
        cy = content_start_y
    draw_summary_row(cy, data.get('summaryText', ''))

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf


@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'no data'}), 400
    try:
        buf = build_pdf(payload)
        return send_file(
            buf,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='57车间排班表.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
