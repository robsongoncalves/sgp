import { Routes } from '@angular/router';

import { LoginComponent } from './pages/login/login.component';
import { MinhasSolicitacoesComponent } from './pages/minhas-solicitacoes/minhas-solicitacoes.component';
import { PlaceholderPageComponent } from './pages/placeholder/placeholder-page.component';
import { ProgressaoDocenteComponent } from './pages/progressao-docente/progressao-docente.component';
import { ServicoDetalheComponent } from './pages/servico-detalhe/servico-detalhe.component';
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
    path: 'servicos/:slug',
    component: ServicoDetalheComponent
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
    path: 'admin/categorias-servico',
    loadComponent: () =>
      import('./pages/admin/categorias-servico/categorias-servico.component').then(
        (component) => component.CategoriasServicoComponent
      )
  },
  {
    path: 'admin/servicos',
    loadComponent: () =>
      import('./pages/admin/servicos/servicos-admin.component').then(
        (component) => component.ServicosAdminComponent
      )
  },
  {
    path: 'admin/equipes',
    redirectTo: 'admin/grupos',
    pathMatch: 'full'
  },
  {
    path: 'admin/grupos',
    loadComponent: () =>
      import('./pages/admin/grupos/grupos.component').then(
        (component) => component.GruposComponent
      )
  },
  {
    path: 'admin/usuarios',
    loadComponent: () =>
      import('./pages/admin/usuarios/usuarios.component').then(
        (component) => component.UsuariosComponent
      )
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
