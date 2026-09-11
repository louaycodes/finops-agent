import { Component, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FinopsService } from '../../core/services/finops.service';
import { marked } from 'marked';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  isMarkdown: boolean;
  sourcesCount?: number;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="chat-container glass-card">
      <div class="chat-header">
        <div class="header-info">
          <h2>FinOps Assistant RAG</h2>
          <p>Posez vos questions sur vos coûts, anomalies ou prévisions AWS.</p>
        </div>
        <button class="btn-primary reindex-btn" (click)="reindex()" [disabled]="isReindexing">
          <svg *ngIf="!isReindexing" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>
          <div *ngIf="isReindexing" class="spinner-small"></div>
          {{ isReindexing ? 'Indexation...' : 'Réindexer ChromaDB' }}
        </button>
      </div>

      <div class="chat-messages" #scrollMe>
        <div class="message" *ngFor="let msg of messages" [ngClass]="msg.role">
          <div class="avatar">{{ msg.role === 'user' ? 'Vous' : 'IA' }}</div>
          <div class="message-content-wrapper">
            <div class="message-bubble" 
                 [class.markdown]="msg.isMarkdown"
                 [innerHTML]="msg.isMarkdown ? renderMarkdown(msg.content) : msg.content">
            </div>
            <div class="sources-badge" *ngIf="msg.sourcesCount !== undefined">
              Basé sur {{ msg.sourcesCount }} document(s) RAG
            </div>
          </div>
        </div>
        
        <div class="message assistant typing" *ngIf="isLoading">
          <div class="avatar">IA</div>
          <div class="message-bubble">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <input 
          type="text" 
          [(ngModel)]="currentQuestion" 
          (keyup.enter)="askQuestion()"
          placeholder="Ex: Pourquoi mes coûts S3 ont-ils augmenté hier ?" 
          [disabled]="isLoading"
          class="chat-input"
        />
        <button class="send-btn" (click)="askQuestion()" [disabled]="isLoading || !currentQuestion.trim()">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
      </div>
    </div>
    
    <!-- Toast Notification -->
    <div class="toast" [class.show]="toastMessage">
      {{ toastMessage }}
    </div>
  `,
  styleUrl: './chat.component.scss'
})
export class ChatComponent implements AfterViewChecked {
  @ViewChild('scrollMe') private myScrollContainer!: ElementRef;

  messages: ChatMessage[] = [
    { role: 'assistant', content: 'Bonjour ! Je suis votre assistant FinOps. Je suis connecté à votre base de données ChromaDB. Que voulez-vous savoir ?', isMarkdown: false }
  ];
  
  currentQuestion = '';
  isLoading = false;
  isReindexing = false;
  toastMessage = '';

  constructor(private finopsService: FinopsService) {}

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      this.myScrollContainer.nativeElement.scrollTop = this.myScrollContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }

  renderMarkdown(content: string): any {
    return marked.parse(content);
  }

  askQuestion() {
    const q = this.currentQuestion.trim();
    if (!q) return;

    // Add user message
    this.messages.push({ role: 'user', content: q, isMarkdown: false });
    this.currentQuestion = '';
    this.isLoading = true;

    this.finopsService.askQuestion(q).subscribe({
      next: (res) => {
        this.messages.push({
          role: 'assistant',
          content: res.answer,
          isMarkdown: true,
          sourcesCount: res.sources_count
        });
        this.isLoading = false;
      },
      error: () => {
        this.messages.push({
          role: 'assistant',
          content: "Désolé, une erreur est survenue lors de la communication avec l'API.",
          isMarkdown: false
        });
        this.isLoading = false;
      }
    });
  }

  reindex() {
    this.isReindexing = true;
    this.finopsService.reindexData().subscribe({
      next: (res) => {
        this.showToast('Indexation ChromaDB terminée avec succès.');
        this.isReindexing = false;
      },
      error: () => {
        this.showToast('Erreur lors de la ré-indexation.');
        this.isReindexing = false;
      }
    });
  }

  showToast(msg: string) {
    this.toastMessage = msg;
    setTimeout(() => this.toastMessage = '', 3000);
  }
}
