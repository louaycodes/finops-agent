import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';


// Interfaces pour typer les données
export interface HealthResponse {
  status: string;
}

export interface TriggerResponse {
  status: string;
  message?: string;
}

export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  answer: string;
  sources_count: number;
}

export interface ReindexResponse {
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class FinopsService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getHealth(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.apiUrl}/health`);
  }

  getAnomalies(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/anomalies`);
  }

  getForecast(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/forecast`);
  }

  getRecommendations(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/recommendations`);
  }

  getMetrics(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/metrics`);
  }

  triggerPipeline(): Observable<TriggerResponse> {
    return this.http.post<TriggerResponse>(`${this.apiUrl}/api/trigger`, {});
  }

  askQuestion(question: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat`, { question });
  }

  reindexData(): Observable<ReindexResponse> {
    return this.http.get<ReindexResponse>(`${this.apiUrl}/reindex`);
  }

  getReportsList(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/api/report/list`);
  }

  generateReport(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/api/report/generate`, { responseType: 'blob' });
  }

  downloadReport(filename: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/api/report/download/${filename}`, { responseType: 'blob' });
  }
}
