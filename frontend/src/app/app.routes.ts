import { Routes } from '@angular/router';

import { LoginComponent } from './pages/login/login.component';
import { MinhasSolicitacoesComponent } from './pages/minhas-solicitacoes/minhas-solicitacoes.component';
import { PlaceholderPageComponent } from './pages/placeholder/placeholder-page.component';
import { ProgressaoDocenteComponent } from './pages/progressao-docente/progressao-docente.component';
import { ServicosComponent } from './pages/servicos/servicos.component';
import { TodosServicosComponent } from './pages/todos-servicos/todos-servicos.component';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: '',
    component: ServicosComponent
  },
  {
    path: 'minhas-solicitacoes',
    component: MinhasSolicitacoesComponent
  },
  {
    path: 'todos-servicos',
    component: TodosServicosComponent
  },
  {
    path: 'progressao-docente',
    component: ProgressaoDocenteComponent
  },
  {
    path: 'solicitacoes-recebidas',
    component: PlaceholderPageComponent,
    data: {
      title: 'Solicitações Recebidas',
      icon: 'inbox'
    }
  },
  {
    path: 'relatorios',
    component: PlaceholderPageComponent,
    data: {
      title: 'Relatórios',
      icon: 'bar_chart'
    }
  },
  {
    path: 'admin/servicos',
    component: PlaceholderPageComponent,
    data: {
      title: 'Serviços',
      icon: 'manage_search'
    }
  },
  {
    path: 'admin/tipos-solicitacao',
    component: PlaceholderPageComponent,
    data: {
      title: 'Tipos de Solicitação',
      icon: 'category'
    }
  },
  {
    path: 'admin/situacoes',
    component: PlaceholderPageComponent,
    data: {
      title: 'Situações',
      icon: 'fact_check'
    }
  },
  {
    path: 'admin/equipes',
    component: PlaceholderPageComponent,
    data: {
      title: 'Equipes',
      icon: 'groups'
    }
  },
  {
    path: 'configuracoes',
    component: PlaceholderPageComponent,
    data: {
      title: 'Configuracoes',
      icon: 'settings'
    }
  }
];
