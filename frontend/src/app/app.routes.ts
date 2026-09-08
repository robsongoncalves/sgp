import { Routes } from '@angular/router';

import { LoginComponent } from './pages/login/login.component';
import { MinhasSolicitacoesComponent } from './pages/minhas-solicitacoes/minhas-solicitacoes.component';
import { PlaceholderPageComponent } from './pages/placeholder/placeholder-page.component';
import { ProgressaoDocenteComponent } from './pages/progressao-docente/progressao-docente.component';
import { ServicoDetalheComponent } from './pages/servico-detalhe/servico-detalhe.component';
import { ServicosComponent } from './pages/servicos/servicos.component';
import { TodosServicosComponent } from './pages/todos-servicos/todos-servicos.component';
import { authGuard } from './core/guards/auth.guard';
import { systemAdminGuard } from './core/guards/system-admin.guard';

export const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: '',
    component: ServicosComponent,
    canActivate: [authGuard]
  },
  {
    path: 'minhas-solicitacoes',
    component: MinhasSolicitacoesComponent,
    canActivate: [authGuard]
  },
  {
    path: 'todos-servicos',
    component: TodosServicosComponent,
    canActivate: [authGuard]
  },
  {
    path: 'servicos/:slug',
    component: ServicoDetalheComponent,
    canActivate: [authGuard]
  },
  {
    path: 'progressao-docente',
    component: ProgressaoDocenteComponent,
    canActivate: [authGuard]
  },
  {
    path: 'caixa-postal',
    loadComponent: () =>
      import('./pages/caixa-postal/caixa-postal.component').then(
        (component) => component.CaixaPostalComponent
      ),
    canActivate: [authGuard]
  },
  {
    path: 'solicitacoes-recebidas',
    redirectTo: 'caixa-postal',
    pathMatch: 'full'
  },
  {
    path: 'relatorios',
    component: PlaceholderPageComponent,
    canActivate: [authGuard],
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
      ),
    canActivate: [systemAdminGuard]
  },
  {
    path: 'admin/servicos',
    loadComponent: () =>
      import('./pages/admin/servicos/servicos-admin.component').then(
        (component) => component.ServicosAdminComponent
      ),
    canActivate: [systemAdminGuard]
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
      ),
    canActivate: [systemAdminGuard]
  },
  {
    path: 'admin/usuarios',
    loadComponent: () =>
      import('./pages/admin/usuarios/usuarios.component').then(
        (component) => component.UsuariosComponent
      ),
    canActivate: [systemAdminGuard]
  },
  {
    path: 'configuracoes',
    component: PlaceholderPageComponent,
    canActivate: [systemAdminGuard],
    data: {
      title: 'Configuracoes',
      icon: 'settings'
    }
  }
];
