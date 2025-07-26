from pypdf import PdfReader, PdfWriter
from pypdf.constants import UserAccessPermissions
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from io import BytesIO
import copy
import os


def overlay_page_number(base_page, page_num, total_pages, x=42, y=63):
    # Create a small overlay with the correct page number
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 10)
    # Draw a white rectangle to cover the old text (digital whiteout)
    can.setFillColorRGB(1, 1, 1)
    can.rect(x-2, y-2, 77, 11, fill=1, stroke=0)
    # Draw the new page number text
    can.setFillColorRGB(0, 0, 0)
    can.drawString(x, y, f"ICS 214, Page {page_num+1} of {total_pages}")
    can.save()
    packet.seek(0)
    overlay_pdf = PdfReader(packet)
    base_page.merge_page(overlay_pdf.pages[0])
    return base_page


def create_ics214_overlay(entries, field_map, page_num, report, offset=2):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 10)
    page_suffix = f'_p{page_num+1}'
    prev_date = None
    period = report.get('period', {})

    date_from_key = f'date_from{page_suffix}'
    date_to_key = f'date_to{page_suffix}'
    time_from_key = f'time_from{page_suffix}'
    time_to_key = f'time_to{page_suffix}'
    prepared_by_name_key = f'prepared_by_name{page_suffix}'
    position_title_key = f'position_title{page_suffix}'
    signature_key = f'signature{page_suffix}'
    datetime_key = f'datetime{page_suffix}'
    incident_name_key = f'incident_name{page_suffix}'

    def parse_datetime(dtstr):
        if not dtstr:
            return None
        if dtstr.endswith('Z'):
            dtstr = dtstr[:-1]
        for fmt in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M'):
            try:
                return datetime.strptime(dtstr, fmt)
            except Exception:
                continue
        return None

    def format_date(dtstr):
        dt_obj = parse_datetime(dtstr)
        return dt_obj.strftime('%m/%d/%Y') if dt_obj else ''

    def format_time(dtstr):
        dt_obj = parse_datetime(dtstr)
        return dt_obj.strftime('%H:%M') if dt_obj else ''

    # Overlay Section 3, 4, 5: Name, ICS Position, Home Agency (from period)
    if page_num == 0:
        period = report.get('period', {})
        name_key = 'name_p1'
        ics_position_key = 'ics_position_p1'
        home_agency_key = 'home_agency_p1'
        if name_key in field_map:
            x, y = field_map[name_key]['x'], field_map[name_key]['y']
            can.drawString(x+offset, y+offset, period.get('name', ''))
        if ics_position_key in field_map:
            x, y = field_map[ics_position_key]['x'], field_map[ics_position_key]['y']
            can.drawString(x+offset, y+offset, period.get('icsPosition', ''))
        if home_agency_key in field_map:
            x, y = field_map[home_agency_key]['x'], field_map[home_agency_key]['y']
            can.drawString(x+offset, y+offset, period.get('homeAgency', ''))

    # Overlay Section 6: Resources Assigned (volunteers)
    if page_num == 0:
        volunteers = report.get('volunteers', [])[:8]
        for idx, v in enumerate(volunteers):
            name_key = f'name_row{idx+1}_p1'
            pos_key = f'ics_position_row{idx+1}_p1'
            agency_key = f'home_agency_row{idx+1}_p1'
            if name_key in field_map:
                x, y = field_map[name_key]['x'], field_map[name_key]['y']
                can.drawString(x+offset, y+offset, v.get('name', ''))
            if pos_key in field_map:
                x, y = field_map[pos_key]['x'], field_map[pos_key]['y']
                can.drawString(x+offset, y+offset, v.get('icsPosition', ''))
            if agency_key in field_map:
                x, y = field_map[agency_key]['x'], field_map[agency_key]['y']
                can.drawString(x+offset, y+offset, v.get('homeAgency', ''))

    # Overlay Section 7: Notable Activities (activities log)
    for i, entry in enumerate(entries):
        dt_field = f'datetime_row{(i+1):02d}{page_suffix}'
        act_field = f'notable_activities_row{(i+1):02d}{page_suffix}'
        dt_obj = parse_datetime(entry['timestamp'])
        is_last = (i == len(entries) - 1)
        full_format = "%m/%d/%Y %H:%M"
        time_format = "%H:%M"
        # Calculate right edge for timestamp column
        full_width = len(datetime.now().strftime(full_format))
        # time_width = len(datetime.now().strftime(time_format))
        if dt_obj:
            date_str = dt_obj.strftime('%m/%d/%Y')
            time_str = dt_obj.strftime('%H:%M')
            if prev_date != date_str or i == 0 or is_last:
                display_ts = f"{date_str} {time_str}"
                prev_date = date_str
            else:
                # Right-justify time-only string to align with right edge of full timestamp
                display_ts = time_str.rjust(full_width)
        else:
            # If not a valid datetime, right-justify raw string
            display_ts = entry['timestamp'].rjust(full_width)
        if dt_field in field_map:
            x, y = field_map[dt_field]['x'], field_map[dt_field]['y']
            can.drawString(x+offset, y+offset, display_ts)
        if act_field in field_map:
            x, y = field_map[act_field]['x'], field_map[act_field]['y']
            can.drawString(x+offset, y+offset, entry['details'])

    # Overlay Section 8: Prepared By
    if prepared_by_name_key in field_map:
        x, y = field_map[prepared_by_name_key]['x'], field_map[prepared_by_name_key]['y']
        can.drawString(x+offset, y+offset,
                       report.get('preparedBy', {}).get('name', ''))
    if position_title_key in field_map:
        x, y = field_map[position_title_key]['x'], field_map[position_title_key]['y']
        can.drawString(x+offset, y+offset, report.get('positionTitle', ''))
    if signature_key in field_map:
        x, y = field_map[signature_key]['x'], field_map[signature_key]['y']
        name = report.get('preparedBy', {}).get('name', '')
        signature = f"/s/ {name}" if name else ''
        can.drawString(x+offset, y+offset, signature)
    if datetime_key in field_map:
        x, y = field_map[datetime_key]['x'], field_map[datetime_key]['y']
        can.drawString(x+offset, y+offset,
                       datetime.now().strftime('%m/%d/%Y %H:%M'))

    # Overlay Section 1: Incident Name
    if incident_name_key in field_map:
        x, y = field_map[incident_name_key]['x'], field_map[incident_name_key]['y']
        can.setFont("Helvetica", 16)
        can.drawString(x+offset, y+offset,
                       report.get('period', {}).get('incidentName', ''))
        can.setFont("Helvetica", 10)

    # Overlay Section 2: Operations Period Dates
    if date_from_key in field_map:
        x, y = field_map[date_from_key]['x'], field_map[date_from_key]['y']
        can.drawString(x+offset, y+offset,
                       format_date(period.get('startTime', '')))
    if date_to_key in field_map:
        x, y = field_map[date_to_key]['x'], field_map[date_to_key]['y']
        can.drawString(x+offset, y+offset,
                       format_date(period.get('endTime', '')))
    if time_from_key in field_map:
        x, y = field_map[time_from_key]['x'], field_map[time_from_key]['y']
        can.drawString(x+offset, y+offset,
                       format_time(period.get('startTime', '')))
    if time_to_key in field_map:
        x, y = field_map[time_to_key]['x'], field_map[time_to_key]['y']
        can.drawString(x+offset, y+offset+1,
                       format_time(period.get('endTime', '')))

    can.save()
    packet.seek(0)
    return PdfReader(packet)


def generate_ics214_report(
    input_pdf_path,
    output_pdf,
    fields_json,
    log_entries,
    report
):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    # Page capacities
    first_page_capacity = 24
    other_page_capacity = 36
    total_pages = 1 + ((len(log_entries) - first_page_capacity +
                       other_page_capacity - 1) // other_page_capacity)
    # Fill first page
    first_batch = log_entries[:first_page_capacity]
    overlay_pdf = create_ics214_overlay(
        first_batch, fields_json, page_num=0, report=report)
    first_page = reader.pages[0]
    first_page.merge_page(overlay_pdf.pages[0])
    first_page = overlay_page_number(first_page, 0, total_pages)
    # Remove /Annots if present (makes page non-fillable)
    if "/Annots" in first_page:
        del first_page["/Annots"]
    writer.add_page(first_page)

    # Fill subsequent pages
    remaining = log_entries[first_page_capacity:]
    page_num = 1
    for page_num, i in enumerate(range(0, len(remaining), other_page_capacity), start=1):
        batch = remaining[i:i+other_page_capacity]
        # Use a blank overlay for subsequent pages (no fillable fields)
        overlay_pdf = create_ics214_overlay(
            batch, fields_json, page_num=1, report=report)
        # Use a blank copy of page 2 (remove annotations if any)
        page2 = copy.deepcopy(reader.pages[1])
        # Remove /Annots if present (makes page non-fillable)
        if "/Annots" in page2:
            del page2["/Annots"]
        page2.merge_page(overlay_pdf.pages[0])
        page2 = overlay_page_number(page2, page_num, total_pages)
        writer.add_page(page2)

    # Append the original 3rd page (e.g., instructions/signature page)
    if len(reader.pages) > 2:
        page3 = copy.deepcopy(reader.pages[2])
        writer.add_page(page3)

    # Write to buffer
    buffer = BytesIO()
    writer.write(buffer)
    buffer.seek(0)

    # Lock the PDF using JWT_SECRET or fallback
    owner_pwd = os.environ.get("JWT_SECRET", "change_me")
    locked_writer = PdfWriter()
    locked_writer.append_pages_from_reader(PdfReader(buffer))
    # Set PDF metadata
    locked_writer.add_metadata({
        "/Title": report.get("period", {}).get("incidentName", "ICS 214 Activity Log"),
        "/Author": report.get("preparedBy", {}).get("name", ""),
        "/CreationDate": datetime.now().strftime("D:%Y%m%d%H%M%S")
    })
    # Enable stricter security: block editing, copying, and printing if supported
    # pypdf >= 5.0.0 supports permissions argument
    try:
        locked_writer.encrypt(
            algorithm="AES-256-R5",
            user_password="",  # No password required to view
            owner_password=owner_pwd,
            permissions_flag=UserAccessPermissions.PRINT | UserAccessPermissions.EXTRACT
        )
    except TypeError:
        # Fallback for older pypdf: only password protection
        locked_writer.encrypt(
            user_password="",  # No password required to view
            owner_password=owner_pwd
        )

    # Support both file path (str) and file-like object
    if isinstance(output_pdf, str):
        with open(output_pdf, 'wb') as f:
            locked_writer.write(f)
    else:
        # Assume file-like object
        locked_writer.write(output_pdf)
