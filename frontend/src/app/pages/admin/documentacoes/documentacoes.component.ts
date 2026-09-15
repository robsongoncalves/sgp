import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { Documentation, DocumentationPayload, DocumentationService } from '../../../core/services/documentation.service';

@Component({
  selector: 'app-documentacoes',
  standalone: true,
  imports: [FormsModule, MatButtonModule, MatIconModule, MatCheckboxModule],
  templateUrl: './documentacoes.component.html',
  styleUrl: './documentacoes.component.scss'
})
export class DocumentacoesComponent implements OnInit {
  items: Documentation[] = [];
  filter = '';
  editingId: number | null = null;
  formVisible = false;
  loading = false;
  saving = false;
  importing = false;
  syncing = false;
  syncErrors: { id: number; url: string; message: string }[] = [];
  error = '';
  message = '';
  headings = 'DEFINIÇÃO\nQUEM FAZ?';
  form: DocumentationPayload = { url: '', description: '', headings: [], sync_enabled: false };
  constructor(private readonly service: DocumentationService) {}
  ngOnInit(): void { this.load(); }
  summary(item: Documentation): string {
    const text = (item.description_text ?? '').replace(/\s+/g, ' ').trim();
    if (!text) return '';
    const sentence = text.match(/^.*?[.!?](?:\s|$)/)?.[0].trim() || text;
    return sentence.slice(0, 140).trimEnd().replace(/[.!?]+$/, '') + '...';
  }
  get filteredItems(): Documentation[] {
    const term = this.filter.trim().toLocaleLowerCase();
    return this.items.filter(item => `${item.url} ${item.description_text || item.description}`.toLocaleLowerCase().includes(term));
  }
  load(): void {
    this.loading = true;
    this.service.list().subscribe({
      next: items => { this.items = items; this.loading = false; },
      error: () => { this.error = 'Nao foi possivel carregar as documentacoes.'; this.loading = false; }
    });
  }
  edit(item?: Documentation): void {
    if (this.syncing) return;
    this.editingId = item?.id ?? null;
    this.form = { url: item?.url || '', description: item?.description || '', headings: [...(item?.headings || [])], sync_enabled: item?.sync_enabled ?? false };
    this.syncErrors = [];
    this.headings = (item?.headings ?? ['DEFINIÇÃO', 'QUEM FAZ?']).join('\n');
    this.error = ''; this.message = ''; this.formVisible = true;
  }
  save(): void {
    if (this.saving || this.importing) return;
    this.error = ''; this.message = '';
    const payload = { ...this.form, url: this.form.url.trim(), headings: this.headingList() };
    this.saving = true;
    const request = this.editingId === null ? this.service.create(payload) : this.service.update(this.editingId, payload);
    request.subscribe({
      next: () => { this.saving = false; this.formVisible = false; this.message = 'Documentacao salva.'; this.load(); },
      error: response => { this.saving = false; this.error = response?.error?.message || 'Nao foi possivel salvar.'; }
    });
  }
  remove(item: Documentation): void {
    if (this.syncing) return;
    if (!window.confirm(`Excluir a documentacao ${item.url || '#' + item.id}?`)) return;
    this.error = ''; this.message = '';
    this.service.delete(item.id).subscribe({
      next: () => { this.message = 'Documentacao excluida.'; this.load(); },
      error: response => { this.error = response?.error?.message || 'Nao foi possivel excluir.'; }
    });
  }
  importDescription(): void {
    if (this.importing || this.saving) return;
    this.error = ''; this.message = '';
    const headings = this.headingList();
    this.importing = true;
    this.service.import({ url: this.form.url.trim(), headings, output_format: 'html', content_class: 'entry-content', heading_tags: ['h4'], text_tags: ['p'] }).subscribe({
      next: result => {
        this.importing = false;
        if (!result.description.trim()) { this.error = 'Nenhum texto encontrado para os topicos informados.'; return; }
        this.form.description = result.description;
        this.message = 'Descricao importada. Revise e salve a documentacao.';
      },
      error: response => { this.importing = false; this.error = response?.error?.message || 'Nao foi possivel importar.'; }
    });
  }
  syncAll(): void {
    if (this.syncing || this.loading) return;
    this.syncing = true;
    this.error = ''; this.message = ''; this.syncErrors = [];
    this.service.syncAll().subscribe({
      next: result => {
        this.syncing = false;
        this.syncErrors = result.errors;
        this.message = result.total
          ? `Sincronização concluída: ${result.updated} atualizada(s), ${result.failed} com falha.`
          : 'Nenhuma documentação está marcada para sincronizar.';
        this.load();
      },
      error: response => {
        this.syncing = false;
        this.error = response?.error?.message || 'Não foi possível concluir a sincronização. Confira a listagem antes de tentar novamente.';
        this.load();
      }
    });
  }
  private headingList(): string[] {
    return [...new Set(this.headings.split(/\r?\n/).map(value => value.trim()).filter(Boolean))];
  }
}
