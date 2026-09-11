import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { AnomaliesComponent } from './pages/anomalies/anomalies.component';
import { ForecastComponent } from './pages/forecast/forecast.component';
import { RecommendationsComponent } from './pages/recommendations/recommendations.component';
import { ChatComponent } from './pages/chat/chat.component';
import { ReportsComponent } from './pages/reports/reports.component';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'anomalies', component: AnomaliesComponent },
  { path: 'forecast', component: ForecastComponent },
  { path: 'recommendations', component: RecommendationsComponent },
  { path: 'reports', component: ReportsComponent },
  { path: 'chat', component: ChatComponent },
  { path: '**', redirectTo: 'dashboard' }
];
