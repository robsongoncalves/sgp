import { Routes } from '@angular/router';

import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { PlaceholderPageComponent } from './pages/placeholder/placeholder-page.component';

export const routes: Routes = [
  {
    path: '',
    component: DashboardComponent
  },
  {
    path: 'clientes',
    component: PlaceholderPageComponent,
    data: {
      title: 'Clientes',
      icon: 'groups'
    }
  },
  {
    path: 'produtos',
    component: PlaceholderPageComponent,
    data: {
      title: 'Produtos',
      icon: 'inventory_2'
    }
  },
  {
    path: 'vendas',
    component: PlaceholderPageComponent,
    data: {
      title: 'Vendas',
      icon: 'receipt_long'
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
