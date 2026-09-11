import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FinopsService } from '../../core/services/finops.service';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions, ChartType } from 'chart.js';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  template: `
    <div class="dashboard-header">
      <div>
        <h1>Dashboard</h1>
        <p>Aperçu global de l'infrastructure AWS et des coûts.</p>
      </div>
      
      <div class="actions">
        <div class="status-badge" [class.online]="healthStatus === 'ok'" [class.offline]="healthStatus !== 'ok'">
          <span class="dot"></span>
          API {{ healthStatus === 'ok' ? 'Online' : 'Offline' }}
        </div>
        <button class="btn-primary" (click)="triggerPipeline()" [disabled]="isTriggering">
          <svg *ngIf="!isTriggering" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
          <div *ngIf="isTriggering" class="spinner"></div>
          {{ isTriggering ? 'Pipeline en cours...' : 'Lancer le pipeline' }}
        </button>
      </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast" [class.show]="toastMessage">
      {{ toastMessage }}
    </div>

    <div class="kpi-grid">
      <div class="kpi-card glass-card">
        <div class="kpi-icon total">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
        </div>
        <div class="kpi-content">
          <h3>Total Prévision (30j)</h3>
          <div class="value">{{ totalForecast | currency:'USD' }}</div>
        </div>
      </div>
      
      <div class="kpi-card glass-card">
        <div class="kpi-icon anomalies">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        </div>
        <div class="kpi-content">
          <h3>Anomalies Actives</h3>
          <div class="value">{{ anomaliesCount }}</div>
        </div>
      </div>
      
      <div class="kpi-card glass-card">
        <div class="kpi-icon savings">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
        </div>
        <div class="kpi-content">
          <h3>Économies Potentielles</h3>
          <div class="value">{{ potentialSavings | currency:'USD' }}</div>
        </div>
      </div>
      
      <div class="kpi-card glass-card">
        <div class="kpi-icon recs">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
        </div>
        <div class="kpi-content">
          <h3>Actions Requises</h3>
          <div class="value">{{ recommendationsCount }}</div>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="chart-container glass-card">
        <h2>Prévision des coûts (30 jours)</h2>
        <div class="chart-wrapper">
          <canvas *ngIf="isChartReady" baseChart
            [data]="lineChartData"
            [options]="lineChartOptions"
            [type]="lineChartType">
          </canvas>
          <div *ngIf="!isChartReady" class="loading-state">
            Chargement du graphique...
          </div>
        </div>
      </div>
      
      <div class="recent-anomalies glass-card">
        <h2>Dernières Anomalies</h2>
        <div class="anomalies-list">
          <div *ngFor="let anomaly of recentAnomalies" class="anomaly-item">
            <div class="anomaly-header">
              <span class="badge" [ngClass]="anomaly.severity.toLowerCase()">{{ anomaly.severity }}</span>
              <span class="service">{{ anomaly.service }}</span>
            </div>
            <p class="desc">{{ anomaly.description }}</p>
            <div class="cost">Coût estimé: <span>{{ anomaly.estimated_cost_usd | currency:'USD' }}</span></div>
          </div>
          <div *ngIf="recentAnomalies.length === 0" class="empty-state">
            Aucune anomalie détectée.
          </div>
        </div>
      </div>
    </div>
    
    <div class="services-section glass-card" style="margin-top: 1.5rem;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
        <h2>Services AWS Monitorés</h2>
        <div style="text-align: right; color: var(--text-secondary); font-size: 0.875rem;">
          <div>Ressources totales : <strong>{{ totalMonitoredResources }}</strong></div>
          <div *ngIf="lastCollected">Dernière collecte : {{ lastCollected }}</div>
        </div>
      </div>
      <div class="services-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem;">
        <div class="service-card" *ngFor="let srv of monitoredServices" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px;">
          <div style="font-weight: 500; margin-bottom: 0.5rem;">{{ srv.name }}</div>
          <div style="color: var(--text-secondary); font-size: 0.875rem;">Coût: <span style="color: var(--text-primary)">{{ srv.cost | currency:'USD' }}</span></div>
        </div>
      </div>
    </div>
  `,
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  healthStatus = 'checking';
  isTriggering = false;
  toastMessage = '';
  
  totalForecast = 0;
  anomaliesCount = 0;
  potentialSavings = 0;
  recommendationsCount = 0;
  
  recentAnomalies: any[] = [];
  
  monitoredServices: any[] = [];
  totalMonitoredResources = 0;
  lastCollected = '';
  
  isChartReady = false;
  public lineChartType: ChartType = 'line';
  public lineChartData: ChartConfiguration['data'] = {
    datasets: [],
    labels: []
  };
  public lineChartOptions: ChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#94a3b8' }
      },
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#94a3b8' }
      }
    },
    plugins: {
      legend: {
        labels: { color: '#f8fafc' }
      }
    }
  };

  constructor(private finopsService: FinopsService) {}

  ngOnInit() {
    this.checkHealth();
    this.loadData();
  }

  checkHealth() {
    this.finopsService.getHealth().subscribe({
      next: (res) => this.healthStatus = res.status,
      error: () => this.healthStatus = 'error'
    });
  }

  loadData() {
    // Load Forecast
    this.finopsService.getForecast().subscribe(data => {
      console.log("Dashboard Forecast:", data);
      if (data && data.daily_forecast) {
        this.totalForecast = data.total_predicted_cost_usd;
        
        const dates = data.daily_forecast.map((item: any) => item.date);
        const values = data.daily_forecast.map((item: any) => item.predicted_cost_usd);
        
        this.lineChartData = {
          datasets: [
            {
              data: values,
              label: 'Coût prévu (USD)',
              backgroundColor: 'rgba(99, 102, 241, 0.2)',
              borderColor: '#6366f1',
              pointBackgroundColor: '#6366f1',
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: '#6366f1',
              fill: 'origin',
              tension: 0.4
            }
          ],
          labels: dates
        };
        this.isChartReady = true;
      }
    });

    // Load Anomalies
    this.finopsService.getAnomalies().subscribe(data => {
      console.log("Dashboard Anomalies:", data);
      if (data && data.anomalies) {
        this.anomaliesCount = data.total_anomalies !== undefined ? data.total_anomalies : data.anomalies.length;
        // Tri par sévérité ou coût
        this.recentAnomalies = data.anomalies
          .sort((a: any, b: any) => b.estimated_cost_usd - a.estimated_cost_usd)
          .slice(0, 3);
      }
    });

    // Load Recommendations
    this.finopsService.getRecommendations().subscribe(data => {
      console.log("Dashboard Recommendations:", data);
      if (data && data.recommendations) {
        this.recommendationsCount = data.recommendations.length;
        this.potentialSavings = data.total_estimated_savings_usd !== undefined ? 
            data.total_estimated_savings_usd : 
            data.recommendations.reduce((sum: number, rec: any) => sum + (rec.estimated_savings_usd || 0), 0);
      }
    });

    // Load Metrics
    this.finopsService.getMetrics().subscribe(data => {
      console.log("Dashboard Metrics:", data);
      if (data) {
        this.totalMonitoredResources = data.monitored_resources || 0;
        this.lastCollected = data.last_collected || '';
        
        if (data.cost_by_service_usd) {
          this.monitoredServices = Object.keys(data.cost_by_service_usd).map(key => ({
            name: key,
            cost: data.cost_by_service_usd[key]
          }));
        }
      }
    });
  }

  triggerPipeline() {
    this.isTriggering = true;
    this.finopsService.triggerPipeline().subscribe({
      next: (res) => {
        this.showToast('Pipeline exécuté avec succès !');
        this.isTriggering = false;
        this.loadData();
      },
      error: (err) => {
        this.showToast('Erreur lors de l\'exécution du pipeline.');
        this.isTriggering = false;
      }
    });
  }

  showToast(msg: string) {
    this.toastMessage = msg;
    setTimeout(() => this.toastMessage = '', 3000);
  }
}
