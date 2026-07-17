import os, json, io
from flask import Flask, request, jsonify, send_file, send_from_directory
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

app = Flask(__name__, static_folder='.')

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
    return send_from_directory('.', 'index.html')


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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
