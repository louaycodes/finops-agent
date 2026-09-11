import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FinopsService } from '../../core/services/finops.service';

@Component({
  selector: 'app-recommendations',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="page-header">
      <h1>Recommandations d'Optimisation</h1>
      <p>Actions concrètes suggérées par l'IA pour réduire vos coûts AWS.</p>
    </div>

    <div *ngIf="isLoading" class="loading-state glass-card">
      Chargement des recommandations...
    </div>

    <div *ngIf="!isLoading && recommendations.length === 0" class="empty-state glass-card">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
      <h3>Tout est optimisé !</h3>
      <p>Aucune recommandation n'a été générée par l'agent FinOps pour le moment.</p>
    </div>

    <div class="recommendations-grid" *ngIf="!isLoading && recommendations.length > 0">
      <div class="rec-card glass-card" *ngFor="let rec of recommendations">
        <div class="rec-header">
          <div class="service-tag">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>
            {{ rec.service }}
          </div>
          <span class="badge" [ngClass]="rec.priority.toLowerCase()">{{ rec.priority }} Priority</span>
        </div>
        
        <h3 class="action-title">{{ rec.action }}</h3>
        <p class="description">{{ rec.description }}</p>
        
        <div class="rec-footer">
          <div class="savings">
            <span class="label">Économies (est.)</span>
            <span class="amount">{{ rec.estimated_savings_usd | currency:'USD' }}</span>
          </div>
          <div class="effort">
            <span class="label">Effort</span>
            <span class="value">{{ rec.implementation_effort }}</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrl: './recommendations.component.scss'
})
export class RecommendationsComponent implements OnInit {
  recommendations: any[] = [];
  isLoading = true;

  constructor(private finopsService: FinopsService) {}

  ngOnInit() {
    this.finopsService.getRecommendations().subscribe({
      next: (data) => {
        console.log("Recommendations Data:", data);
        if (data && data.recommendations) {
          // Tri par priorité High -> Medium -> Low
          const priorityWeight: any = { 'High': 3, 'Medium': 2, 'Low': 1 };
          this.recommendations = data.recommendations.sort((a: any, b: any) => {
            const weightA = priorityWeight[a.priority] || 0;
            const weightB = priorityWeight[b.priority] || 0;
            return weightB - weightA;
          });
        }
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}
