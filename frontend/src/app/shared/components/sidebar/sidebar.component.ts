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

  mainMenuItems: MenuItem[] = [
    {
      icon: 'apps',
      label: 'Serviços',
      route: '/'
    },
    {
      icon: 'assignment_turned_in',
      label: 'Minhas Solicitações',
      route: '/minhas-solicitacoes'
    }
  ];

  restrictedMenuItems: MenuItem[] = [
    {
      icon: 'settings',
      label: 'Configurações',
      route: '/configuracoes'
    }
  ];
}
