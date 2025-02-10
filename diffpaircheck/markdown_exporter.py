# diffpaircheck/markdown_exporter.py

def generate_markdown_report(rows, input_filename, overall_status, timestamp):
    """
    Generate a Markdown report with a header section and a formatted table.
    The overall status header is colored: green for PASS, red for FAIL.
    """
    md_lines = []
    md_lines.append("# Differential Pair Length Check Report")
    md_lines.append("")
    md_lines.append(f"**Input File:** {input_filename}")
    md_lines.append(f"**Date/Time:** {timestamp}")
    md_lines.append("")
    if overall_status.upper() == "PASS":
        status_str = '<span style="color:green">PASS</span>'
    else:
        status_str = '<span style="color:red">FAIL</span>'
    md_lines.append(f"## Overall Status: {status_str}")
    md_lines.append("")
    headers = ["**Group**", "**Pair**", "**Diff (mm)**", "**Tolerance (mm)**", "**Status**"]
    md_lines.append("| " + " | ".join(headers) + " |")
    md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        row_list = list(row)
        status = str(row_list[-1]).upper()
        if status == "PASS":
            row_list[-1] = '<span style="color:green">PASS</span>'
        elif status == "FAIL":
            row_list[-1] = '<span style="color:red">FAIL</span>'
        md_lines.append("| " + " | ".join(str(item) for item in row_list) + " |")
    return "\n".join(md_lines)
