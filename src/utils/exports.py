import pandas as pd
from io import BytesIO
from flask import make_response

def generar_excel(data, filename, sheet_name='Datos'):
    """Generar archivo Excel desde datos"""
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Ajustar ancho de columnas
        worksheet = writer.sheets[sheet_name]
        for column in df:
            column_length = max(df[column].astype(str).map(len).max(), len(column))
            col_letter = worksheet[f'{df.columns.get_loc(column) + 1}1'].column_letter
            worksheet.column_dimensions[col_letter].width = min(column_length + 2, 50)
    
    output.seek(0)
    
    response = make_response(output.read())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
    
    return response

def generar_csv(data, filename):
    """Generar archivo CSV desde datos"""
    df = pd.DataFrame(data)
    
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    response = make_response(output.read())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'
    
    return response

def exportar_a_pdf(data, filename, titulo='Reporte'):
    """Generar reporte PDF (requiere reportlab)"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    
    # Contenido
    story = []
    
    # Título
    title = Paragraph(titulo, title_style)
    story.append(title)
    
    # Tabla
    if data:
        # Encabezados
        headers = list(data[0].keys())
        table_data = [headers]
        
        # Datos
        for row in data:
            table_data.append([str(row[col]) for col in headers])
        
        # Crear tabla
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
    
    # Generar PDF
    doc.build(story)
    output.seek(0)
    
    response = make_response(output.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}.pdf'
    
    return response