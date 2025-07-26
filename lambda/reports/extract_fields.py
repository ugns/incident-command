import sys
import json
from pypdf import PdfReader
import re

def extract_field_widgets(annot_obj, parent_field_name=None):
    widgets = []
    this_field_name = annot_obj.get('/T', parent_field_name)
    if this_field_name:
        if isinstance(this_field_name, bytes):
            this_field_name = this_field_name.decode('utf-8')
        this_field_name = this_field_name.strip('()')
    if '/Kids' in annot_obj:
        for kid in annot_obj['/Kids']:
            kid_obj = kid.get_object()
            widgets.extend(extract_field_widgets(kid_obj, parent_field_name=this_field_name))
    else:
        resolved_name = this_field_name
        if not resolved_name:
            parent_obj = annot_obj.get('/Parent', None)
            max_depth = 10
            depth = 0
            while parent_obj is not None and depth < max_depth:
                parent_obj = parent_obj.get_object()
                tval = parent_obj.get('/T', None)
                if tval:
                    if isinstance(tval, bytes):
                        tval = tval.decode('utf-8')
                    tval = tval.strip('()')
                    resolved_name = tval
                    break
                parent_obj = parent_obj.get('/Parent', None)
                depth += 1
        if '/Rect' in annot_obj:
            rect = annot_obj['/Rect']
            x = float(rect[0])
            y = float(rect[1])
            widgets.append((resolved_name, annot_obj, x, y))
    return widgets

def extract_normalized_fields(pdf_path):
    reader = PdfReader(pdf_path)
    fields = {}
    for page_num, page in enumerate(reader.pages):
        if '/Annots' in page:
            annots = page['/Annots']
            if not isinstance(annots, list):
                annots = [annots]
            for annot in annots:
                annot_obj = annot.get_object()
                for field_name, widget_obj, x, y in extract_field_widgets(annot_obj):
                    widget_page_num = None
                    if '/P' in widget_obj:
                        for idx, pg in enumerate(reader.pages):
                            if widget_obj['/P'] == pg:
                                widget_page_num = idx
                                break
                    if widget_page_num is None:
                        widget_page_num = page_num
                    if widget_page_num != page_num:
                        continue
                    # Normalization logic (matches generate.py)
                    norm_name = None

                    # ICS-214 section 1, Incident Name
                    if field_name == '1 Incident Name_19':
                        norm_name = 'incident_name_p1'
                    elif field_name == '1 Incident Name_20':
                        norm_name = 'incident_name_p2'

                    # ICS-214 section 2, Operations Period
                    elif field_name == 'Date From':
                        norm_name = f'date_from_p{page_num+1}'
                    elif field_name == 'Date To':
                        norm_name = f'date_to_p{page_num+1}'
                    elif field_name == 'Time From':
                        norm_name = f'time_from_p{page_num+1}'
                    elif field_name == 'Time To':
                        norm_name = f'time_to_p{page_num+1}'

                    # ICS-214 section 3, Name
                    elif field_name == '3 Name':
                        norm_name = f'name_p{page_num+1}'

                    # ICS-214 section 4, ICS Position
                    elif field_name == '4 ICS Position':
                        norm_name = f'ics_position_p{page_num+1}'

                    # ICS-214 section 5, Home Agency and Unit
                    elif field_name == '5 Home Agency and Unit':
                        norm_name = f'home_agency_p{page_num+1}'

                    # ICS-214 section 6, Resources Assigned
                    elif field_name and field_name.startswith('NameRow'):
                        m = re.match(r'NameRow(\d+)(_3)?', field_name)
                        if m:
                            row_num = int(m.group(1))
                            norm_name = f'name_row{row_num}_p{page_num+1}'
                    elif field_name and field_name.startswith('ICS PositionRow'):
                        m = re.match(r'ICS PositionRow(\d+)', field_name)
                        if m:
                            row_num = int(m.group(1))
                            norm_name = f'ics_position_row{row_num}_p{page_num+1}'
                    elif field_name and field_name.startswith('Home Agency and UnitRow'):
                        m = re.match(r'Home Agency and UnitRow(\d+)', field_name)
                        if m:
                            row_num = int(m.group(1))
                            norm_name = f'home_agency_row{row_num}_p{page_num+1}'

                    # ICS-214 section 7, Activity Log
                    elif field_name and field_name.startswith('DateTimeRow'):
                        m = re.match(r'DateTimeRow(\d+)(_2)?', field_name)
                        if m:
                            row_num = int(m.group(1))
                            norm_name = f'datetime_row{row_num:02d}_p{page_num+1}'
                    elif field_name and field_name.startswith('Notable ActivitiesRow'):
                        m = re.match(r'Notable ActivitiesRow(\d+)(_2)?', field_name)
                        if m:
                            row_num = int(m.group(1))
                            norm_name = f'notable_activities_row{row_num:02d}_p{page_num+1}'

                    # ISC-214 section 8, Prepared By
                    elif field_name == '8 Prepared by Name':
                        norm_name = 'prepared_by_name_p1'
                    elif field_name == '8 Prepared by Name_2':
                        norm_name = 'prepared_by_name_p2'
                    elif field_name == 'PositionTitle_15':
                        norm_name = 'position_title_p1'
                    elif field_name == 'PositionTitle_16':
                        norm_name = 'position_title_p2'
                    elif field_name == 'DateTime_15':
                        norm_name = 'datetime_p1'
                    elif field_name == 'DateTime_16':
                        norm_name = 'datetime_p2'
                    elif field_name == 'Signature_21':
                        norm_name = 'signature_p1'
                    elif field_name == 'Signature_22':
                        norm_name = 'signature_p2'

                    if norm_name:
                        fields[norm_name] = {
                            'field_name': field_name,
                            'page': page_num,
                            'x': x,
                            'y': y
                        }
    return fields

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Extract and normalize PDF field coordinates.')
    parser.add_argument('input_pdf', help='Input PDF filename')
    parser.add_argument('output_json', help='Output JSON filename')
    args = parser.parse_args()
    fields = extract_normalized_fields(args.input_pdf)
    with open(args.output_json, 'w') as f:
        json.dump(fields, f, indent=2, sort_keys=True)
    print(f"Extracted {len(fields)} normalized fields to {args.output_json}")

if __name__ == '__main__':
    main()
