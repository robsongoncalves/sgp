import { AsyncPipe } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';

import { User } from '../../../core/models/user';
import { AuthService } from '../../../core/services/auth.service';

interface MenuItem {
  icon: string;
  label: string;
  route: string;
}

interface MenuSection {
  title?: string;
  adminOnly?: boolean;
  items: MenuItem[];
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    AsyncPipe,
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
  currentUser$ = this.authService.currentUser$;

  constructor(private readonly authService: AuthService) {}

  menuSections: MenuSection[] = [
    {
      items: [
        {
          icon: 'apps',
          label: 'Serviços Disponíveis',
          route: '/'
        },
        {
          icon: 'assignment_turned_in',
          label: 'Minhas Solicitações',
          route: '/minhas-solicitacoes'
        }
      ]
    },
    {
      items: [
        {
          icon: 'inbox',
          label: 'Caixa Postal',
          route: '/caixa-postal'
        },
        {
          icon: 'bar_chart',
          label: 'Relatórios',
          route: '/relatorios'
        }
      ]
    },
    {
      title: 'Área Restrita',
      adminOnly: true,
      items: [
        {
          icon: 'category',
          label: 'Serviços',
          route: '/admin/servicos'
        },
        {
          icon: 'folder',
          label: 'Categorias de Servico',
          route: '/admin/categorias-servico'
        },
        {
          icon: 'description',
          label: 'Tipos de Documentos',
          route: '/admin/tipos-documentos'
        },
        {
          icon: 'dynamic_form',
          label: 'Formulários',
          route: '/admin/formularios'
        },
        {
          icon: 'rate_review',
          label: 'Modelos de Parecer',
          route: '/admin/modelos-parecer'
        },
        {
          icon: 'groups',
          label: 'Grupos de Usuarios',
          route: '/admin/grupos'
        },
        {
          icon: 'person',
          label: 'Usuarios',
          route: '/admin/usuarios'
        },
        {
          icon: 'code',
          label: 'Functions',
          route: '/admin/functions'
        },
        {
          icon: 'data_object',
          label: 'Mapa de Campos',
          route: '/admin/mapa-campos'
        },
        {
          icon: 'settings',
          label: 'Configurações',
          route: '/configuracoes'
        },
        {
          icon: 'receipt_long',
          label: 'Logs',
          route: '/admin/logs'
        }
      ]
    }
  ];

  canShowSection(section: MenuSection, user: User | null): boolean {
    return !section.adminOnly || this.authService.isSystemAdminUser(user);
  }
}
