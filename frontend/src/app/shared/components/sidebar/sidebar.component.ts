import { Component, Input } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';

interface MenuItem {
  icon: string;
  label: string;
  route: string;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    RouterLink,
    RouterLinkActive,
    MatIconModule,
    MatListModule,
    MatTooltipModule
  ],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent {
  @Input() collapsed = false;

  menuItems: MenuItem[] = [
    {
      icon: 'dashboard',
      label: 'Dashboard',
      route: '/'
    },
    {
      icon: 'groups',
      label: 'Clientes',
      route: '/clientes'
    },
    {
      icon: 'inventory_2',
      label: 'Produtos',
      route: '/produtos'
    },
    {
      icon: 'receipt_long',
      label: 'Vendas',
      route: '/vendas'
    },
    {
      icon: 'settings',
      label: 'Configuracoes',
      route: '/configuracoes'
    }
  ];
}
