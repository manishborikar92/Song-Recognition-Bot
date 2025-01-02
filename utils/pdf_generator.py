from fpdf import FPDF

# Function to wrap text within a cell
def wrap_text(text, width, pdf):
    """
    Splits the text into lines that fit within the specified width.
    """
    return pdf.multi_cell(width, 10, text, border=0, split_only=True)

# Function to create PDF
def create_pdf(filename, title, headers, content):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_title(title)

    # Add title
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(10)

    # Determine column widths based on page width
    page_width = pdf.w - 2 * pdf.l_margin  # Full page width minus margins
    col_widths = [15]  # Serial number column fixed width
    col_widths += [(page_width - col_widths[0]) / len(headers)] * len(headers)

    # Add table headers
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(col_widths[0], 10, "Sr. No", border=1, align='C')  # Serial number header
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i + 1], 10, header, border=1, align='C')
    pdf.ln()

    # Add table rows
    pdf.set_font("Arial", size=12)
    for idx, row in enumerate(content, start=1):
        # Wrap text for each cell and calculate the maximum height for the row
        row_lines = []
        for i, cell in enumerate(row):
            cell_text = str(cell).encode("latin-1", "replace").decode("latin-1")
            lines = wrap_text(cell_text, col_widths[i + 1], pdf)
            row_lines.append(lines)

        max_lines = max(len(lines) for lines in row_lines)
        row_height = max_lines * 10  # Adjust row height based on the maximum number of lines

        # Draw cells for the current row
        pdf.cell(col_widths[0], row_height, str(idx), border=1, align='C')  # Serial number column
        for i, lines in enumerate(row_lines):
            x, y = pdf.get_x(), pdf.get_y()
            if i == 1:  # Center align "Date and Time" column
                pdf.multi_cell(
                    col_widths[i + 1],
                    10,
                    "\n".join(lines),
                    border=1,
                    align='C',
                )
            else:  # Left align other columns
                pdf.multi_cell(
                    col_widths[i + 1],
                    10,
                    "\n".join(lines),
                    border=1,
                    align='L',
                )
            pdf.set_xy(x + col_widths[i + 1], y)  # Reset x-coordinate after writing the cell
        pdf.ln(row_height)

    # Save the PDF
    pdf.output(filename)
