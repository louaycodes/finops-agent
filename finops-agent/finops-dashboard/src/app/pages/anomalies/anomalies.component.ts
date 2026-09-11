import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FinopsService } from '../../core/services/finops.service';

@Component({
  selector: 'app-anomalies',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="page-header">
      <h1>Anomalies Détectées</h1>
      <p>Liste des comportements anormaux détectés dans la facturation AWS.</p>
    </div>

    <div class="filters glass-card">
      <span class="filter-label">Filtrer par sévérité :</span>
      <button class="filter-btn" [class.active]="filter === 'All'" (click)="setFilter('All')">Tout</button>
      <button class="filter-btn" [class.active]="filter === 'High'" (click)="setFilter('High')">High</button>
      <button class="filter-btn" [class.active]="filter === 'Medium'" (click)="setFilter('Medium')">Medium</button>
      <button class="filter-btn" [class.active]="filter === 'Low'" (click)="setFilter('Low')">Low</button>
    </div>

    <div class="glass-card table-container">
      <div *ngIf="isLoading" class="loading-state">Chargement des anomalies...</div>
      
      <table *ngIf="!isLoading" class="modern-table">
        <thead>
          <tr>
            <th>Service</th>
            <th>Type</th>
            <th>Sévérité</th>
            <th>Description</th>
            <th>Surcoût Estimé</th>
            <th>Recommandation</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let anomaly of filteredAnomalies">
            <td><strong>{{ anomaly.service }}</strong></td>
            <td>{{ anomaly.type }}</td>
            <td>
              <span class="badge" [ngClass]="anomaly.severity.toLowerCase()">{{ anomaly.severity }}</span>
            </td>
            <td>{{ anomaly.description }}</td>
            <td class="cost-cell">{{ anomaly.estimated_cost_usd | currency:'USD' }}</td>
            <td>{{ anomaly.recommendation }}</td>
          </tr>
          <tr *ngIf="filteredAnomalies.length === 0">
            <td colspan="6" class="empty-state">Aucune anomalie correspondant aux critères.</td>
          </tr>
        </tbody>
      </table>
    </div>
  `,
  styleUrl: './anomalies.component.scss'
})
export class AnomaliesComponent implements OnInit {
  anomalies: any[] = [];
  filteredAnomalies: any[] = [];
  filter: string = 'All';
  isLoading = true;

  constructor(private finopsService: FinopsService) {}

  ngOnInit() {
    this.finopsService.getAnomalies().subscribe({
      next: (data) => {
        console.log("Anomalies Data:", data);
        if (data && data.anomalies) {
          this.anomalies = data.anomalies.sort((a: any, b: any) => b.estimated_cost_usd - a.estimated_cost_usd);
          this.filteredAnomalies = [...this.anomalies];
        }
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  setFilter(severity: string) {
    this.filter = severity;
    if (severity === 'All') {
      this.filteredAnomalies = [...this.anomalies];
    } else {
      this.filteredAnomalies = this.anomalies.filter(a => a.severity === severity);
    }
  }
}
