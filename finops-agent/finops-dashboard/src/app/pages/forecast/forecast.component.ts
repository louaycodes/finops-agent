import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FinopsService } from '../../core/services/finops.service';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions, ChartType } from 'chart.js';

@Component({
  selector: 'app-forecast',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  template: `
    <div class="page-header">
      <h1>Prévision des Coûts</h1>
      <p>Projection des dépenses AWS sur les 30 prochains jours générée par le modèle prédictif.</p>
    </div>

    <div class="summary-cards glass-card">
      <div class="stat">
        <span class="label">Total Prévu (30j)</span>
        <span class="value">{{ totalForecast | currency:'USD' }}</span>
      </div>
      <div class="stat">
        <span class="label">Période</span>
        <span class="value period" *ngIf="startDate">{{ startDate | date:'dd MMM yyyy' }} - {{ endDate | date:'dd MMM yyyy' }}</span>
      </div>
    </div>

    <div class="chart-container glass-card">
      <div *ngIf="isLoading" class="loading-state">
        <div class="spinner"></div>
        Chargement des prévisions...
      </div>
      <div class="chart-wrapper" *ngIf="!isLoading">
        <canvas baseChart
          [data]="lineChartData"
          [options]="lineChartOptions"
          [type]="lineChartType">
        </canvas>
      </div>
    </div>
  `,
  styleUrl: './forecast.component.scss'
})
export class ForecastComponent implements OnInit {
  isLoading = true;
  totalForecast = 0;
  startDate: string | null = null;
  endDate: string | null = null;

  public lineChartType: ChartType = 'line';
  public lineChartData: ChartConfiguration['data'] = {
    datasets: [],
    labels: []
  };
  
  public lineChartOptions: ChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    elements: {
      line: { tension: 0.4 },
      point: { radius: 4, hoverRadius: 6 }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#94a3b8' }
      },
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)' },
        ticks: { color: '#94a3b8', maxTicksLimit: 15 }
      }
    },
    plugins: {
      legend: {
        labels: { color: '#f8fafc', font: { family: 'Inter', size: 14 } }
      },
      tooltip: {
        backgroundColor: 'rgba(26, 29, 46, 0.9)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        padding: 12
      }
    }
  };

  constructor(private finopsService: FinopsService) {}

  ngOnInit() {
    this.finopsService.getForecast().subscribe({
      next: (data) => {
        console.log("Forecast Data:", data);
        if (data && data.daily_forecast) {
          this.totalForecast = data.total_predicted_cost_usd;
          
          const items = data.daily_forecast;
          if (items.length > 0) {
            this.startDate = items[0].date;
            this.endDate = items[items.length - 1].date;
          }

          const dates = items.map((i: any) => i.date);
          const values = items.map((i: any) => i.predicted_cost_usd);

          this.lineChartData = {
            datasets: [
              {
                data: values,
                label: 'Coût Quotidien (USD)',
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: '#6366f1',
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#fff',
                fill: 'origin'
              }
            ],
            labels: dates
          };
        }
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }
}
