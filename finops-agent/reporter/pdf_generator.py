import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, ListFlowable, ListItem
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import numpy as np

class PDFGenerator:
    """Generates the AWS FinOps PDF Report."""
    
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Define custom ParagraphStyles for the report."""
        self.styles.add(ParagraphStyle(name='CoverTitle', parent=self.styles['Heading1'], fontSize=28, textColor=colors.HexColor("#232F3E"), alignment=1, spaceAfter=30))
        self.styles.add(ParagraphStyle(name='CoverSub', parent=self.styles['Normal'], fontSize=16, textColor=colors.HexColor("#666666"), alignment=1, spaceAfter=20))
        self.styles.add(ParagraphStyle(name='SectionHeader', parent=self.styles['Heading2'], fontSize=18, textColor=colors.HexColor("#FF9900"), spaceBefore=20, spaceAfter=15))
        self.styles.add(ParagraphStyle(name='KpiValue', parent=self.styles['Normal'], fontSize=24, textColor=colors.HexColor("#232F3E"), alignment=1, fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='KpiLabel', parent=self.styles['Normal'], fontSize=12, textColor=colors.HexColor("#666666"), alignment=1))
        
        self.styles.add(ParagraphStyle(name='TableCell', parent=self.styles['Normal'], fontSize=10, textColor=colors.black))
        self.styles.add(ParagraphStyle(name='TableHigh', parent=self.styles['TableCell'], textColor=colors.HexColor("#D13212"), fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='TableMedium', parent=self.styles['TableCell'], textColor=colors.HexColor("#FF9900"), fontName='Helvetica-Bold'))
        self.styles.add(ParagraphStyle(name='TableLow', parent=self.styles['TableCell'], textColor=colors.HexColor("#1D8102"), fontName='Helvetica-Bold'))

    def _header_footer(self, canvas, doc):
        """Draws the header and footer on each page."""
        canvas.saveState()
        
        # Header
        canvas.setFillColor(colors.HexColor("#232F3E"))
        canvas.setFont('Helvetica-Bold', 12)
        canvas.drawString(inch, A4[1] - 0.5 * inch, "FinOps Agent")
        
        canvas.setStrokeColor(colors.HexColor("#FF9900"))
        canvas.setLineWidth(2)
        canvas.line(inch, A4[1] - 0.6 * inch, A4[0] - inch, A4[1] - 0.6 * inch)
        
        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor("#666666"))
        page_num = canvas.getPageNumber()
        text = f"Page {page_num} | Généré le {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        canvas.drawRightString(A4[0] - inch, 0.5 * inch, text)
        canvas.line(inch, 0.7 * inch, A4[0] - inch, 0.7 * inch)
        
        canvas.restoreState()

    def _generate_forecast_chart(self, forecasts_data) -> io.BytesIO:
        """Generates a Matplotlib chart and returns it as a BytesIO buffer."""
        dates = [item['date'] for item in forecasts_data.get('forecast_30_days', [])]
        values = [item['forecast_cost_usd'] for item in forecasts_data.get('forecast_30_days', [])]
        
        if not dates or not values:
            return None
            
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(dates, values, color='#FF9900', marker='o', linestyle='-', linewidth=2, markersize=4)
        ax.set_title('Prévision des Coûts (30 jours)', fontsize=14, color='#232F3E')
        ax.set_ylabel('Coût (USD)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Reduce ticks to avoid crowding
        if len(dates) > 10:
            ax.set_xticks(np.arange(0, len(dates), len(dates)//10))
            
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        plt.close(fig)
        buf.seek(0)
        return buf

    def generate(self, data: dict, discovered_services: list) -> io.BytesIO:
        """Generates the full PDF report and returns it as a BytesIO buffer."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=inch, leftMargin=inch,
            topMargin=inch, bottomMargin=inch
        )
        
        elements = []
        
        # --- COVER PAGE ---
        elements.append(Spacer(1, 2 * inch))
        elements.append(Paragraph("FinOps Agent — Rapport d'analyse AWS", self.styles['CoverTitle']))
        
        date_str = datetime.datetime.now().strftime('%d %B %Y')
        elements.append(Paragraph(f"Date de génération : {date_str}", self.styles['CoverSub']))
        elements.append(Paragraph(f"Compte AWS : {self.account_id}", self.styles['CoverSub']))
        elements.append(PageBreak())

        # --- EXECUTIVE SUMMARY ---
        elements.append(Paragraph("Résumé Exécutif", self.styles['SectionHeader']))
        
        anomalies_data = data.get('anomalies', {})
        forecasts_data = data.get('forecasts', {})
        recs_data = data.get('recommendations', {})
        
        total_anomalies = anomalies_data.get('total_anomalies', len(anomalies_data.get('anomalies', [])))
        total_forecast = forecasts_data.get('total_predicted_cost_usd', forecasts_data.get('total_forecast_usd', 0))
        total_savings = recs_data.get('total_estimated_savings_usd', 
                            sum(r.get('estimated_savings_usd', 0) for r in recs_data.get('recommendations', [])))

        # KPI Table
        kpi_data = [
            [
                Paragraph("Anomalies Détectées", self.styles['KpiLabel']),
                Paragraph("Économies Potentielles", self.styles['KpiLabel']),
                Paragraph("Coût Prévu (30j)", self.styles['KpiLabel'])
            ],
            [
                Paragraph(str(total_anomalies), self.styles['KpiValue']),
                Paragraph(f"${total_savings:,.2f}", self.styles['KpiValue']),
                Paragraph(f"${total_forecast:,.2f}", self.styles['KpiValue'])
            ]
        ]
        
        kpi_table = Table(kpi_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
        kpi_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('TOPPADDING', (0,1), (-1,1), 10),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 0.5 * inch))

        # --- FORECAST CHART ---
        elements.append(Paragraph("Prévision à 30 jours", self.styles['SectionHeader']))
        chart_buf = self._generate_forecast_chart(forecasts_data)
        if chart_buf:
            elements.append(Image(chart_buf, width=6*inch, height=3*inch))
        else:
            elements.append(Paragraph("Aucune donnée de prévision disponible.", self.styles['Normal']))
            
        elements.append(PageBreak())

        # --- ANOMALIES TABLE ---
        elements.append(Paragraph("Anomalies Détectées", self.styles['SectionHeader']))
        anomalies_list = anomalies_data.get('anomalies', [])
        
        if anomalies_list:
            # Sort by cost desc
            anomalies_list.sort(key=lambda x: x.get('estimated_cost_usd', 0), reverse=True)
            
            table_data = [['Service', 'Sévérité', 'Type', 'Économies']]
            for a in anomalies_list:
                sev = a.get('severity', 'Low')
                sev_style = self.styles['TableHigh'] if sev == 'High' else (self.styles['TableMedium'] if sev == 'Medium' else self.styles['TableLow'])
                
                table_data.append([
                    Paragraph(a.get('service', 'N/A'), self.styles['TableCell']),
                    Paragraph(sev, sev_style),
                    Paragraph(a.get('type', 'N/A'), self.styles['TableCell']),
                    Paragraph(f"${a.get('estimated_cost_usd', 0):.2f}", self.styles['TableCell'])
                ])
                
            t = Table(table_data, colWidths=[1.5*inch, 1*inch, 2*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#232F3E")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F9F9F9")),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#DDDDDD"))
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("Aucune anomalie détectée.", self.styles['Normal']))
            
        elements.append(Spacer(1, 0.5 * inch))

        # --- RECOMMENDATIONS ---
        elements.append(Paragraph("Recommandations", self.styles['SectionHeader']))
        recs_list = recs_data.get('recommendations', [])
        if recs_list:
            # Sort by priority
            priority_map = {'High': 3, 'Medium': 2, 'Low': 1}
            recs_list.sort(key=lambda x: priority_map.get(x.get('priority', 'Low'), 0), reverse=True)
            
            list_items = []
            for r in recs_list:
                text = f"<b>[{r.get('priority', 'Low')}] {r.get('action', '')}</b><br/>"
                text += f"{r.get('description', '')}<br/>"
                text += f"<i>Délai: {r.get('implementation_effort', 'N/A')} | Économies: ${r.get('estimated_savings_usd', 0):.2f}</i>"
                list_items.append(ListItem(Paragraph(text, self.styles['Normal']), spaceAfter=10))
                
            elements.append(ListFlowable(list_items, bulletType='1'))
        else:
            elements.append(Paragraph("Aucune recommandation disponible.", self.styles['Normal']))
            
        elements.append(PageBreak())

        # --- MONITORED SERVICES ---
        elements.append(Paragraph("Services Monitorés", self.styles['SectionHeader']))
        if discovered_services:
            services_text = ", ".join(discovered_services)
            elements.append(Paragraph(services_text, self.styles['Normal']))
        else:
            elements.append(Paragraph("Aucun service monitoré n'a été découvert.", self.styles['Normal']))

        # Build the PDF
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        
        buffer.seek(0)
        return buffer
