import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FinopsService } from '../../core/services/finops.service';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="page-header">
      <h1>Rapports PDF</h1>
      <p>Générez et téléchargez des rapports d'analyse AWS complets au format PDF.</p>
    </div>

    <!-- Toast Notification -->
    <div class="toast" [class.show]="toastMessage">
      {{ toastMessage }}
    </div>

    <div class="generate-section glass-card">
      <div class="info">
        <h3>Nouveau Rapport</h3>
        <p>Compile les dernières anomalies, prévisions et recommandations en un seul document.</p>
      </div>
      <button class="btn-primary" (click)="generateReport()" [disabled]="isGenerating">
        <svg *ngIf="!isGenerating" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
        <div *ngIf="isGenerating" class="spinner-small"></div>
        {{ isGenerating ? 'Génération en cours...' : 'Générer un rapport' }}
      </button>
    </div>

    <div class="reports-list glass-card">
      <h2>Historique des rapports</h2>
      
      <div *ngIf="isLoading" class="loading-state">Chargement des rapports...</div>
      
      <table *ngIf="!isLoading" class="modern-table">
        <thead>
          <tr>
            <th>Nom du fichier</th>
            <th>Date de génération</th>
            <th>Taille</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let report of reports">
            <td>
              <div class="file-name">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                {{ report.filename }}
              </div>
            </td>
            <td>{{ report.generated_at }}</td>
            <td>{{ report.size_kb }} KB</td>
            <td>
              <button class="btn-download" (click)="downloadReport(report.filename)" [disabled]="isDownloading === report.filename">
                <svg *ngIf="isDownloading !== report.filename" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                <div *ngIf="isDownloading === report.filename" class="spinner-small-dark"></div>
                Télécharger
              </button>
            </td>
          </tr>
          <tr *ngIf="reports.length === 0">
            <td colspan="4" class="empty-state">Aucun rapport généré pour le moment.</td>
          </tr>
        </tbody>
      </table>
    </div>
  `,
  styleUrl: './reports.component.scss'
})
export class ReportsComponent implements OnInit {
  reports: any[] = [];
  isLoading = true;
  isGenerating = false;
  isDownloading: string | null = null;
  toastMessage = '';

  constructor(private finopsService: FinopsService) {}

  ngOnInit() {
    this.loadReports();
  }

  loadReports() {
    this.isLoading = true;
    this.finopsService.getReportsList().subscribe({
      next: (data) => {
        if (data && data.reports) {
          this.reports = data.reports;
        }
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  generateReport() {
    this.isGenerating = true;
    this.finopsService.generateReport().subscribe({
      next: (blob) => {
        this.triggerDownload(blob, `finops_report_${this.getTimestamp()}.pdf`);
        this.showToast('Rapport généré avec succès !');
        this.isGenerating = false;
        this.loadReports(); // Refresh the list
      },
      error: () => {
        this.showToast('Erreur lors de la génération du rapport.');
        this.isGenerating = false;
      }
    });
  }

  downloadReport(filename: string) {
    this.isDownloading = filename;
    this.finopsService.downloadReport(filename).subscribe({
      next: (blob) => {
        this.triggerDownload(blob, filename);
        this.isDownloading = null;
      },
      error: () => {
        this.showToast('Erreur lors du téléchargement.');
        this.isDownloading = null;
      }
    });
  }

  private triggerDownload(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  private getTimestamp(): string {
    const now = new Date();
    return now.toISOString().replace(/T/, '_').replace(/:/g, '').split('.')[0];
  }

  showToast(msg: string) {
    this.toastMessage = msg;
    setTimeout(() => this.toastMessage = '', 3000);
  }
}
