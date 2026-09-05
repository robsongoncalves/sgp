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

interface MenuSection {
  title?: string;
  items: MenuItem[];
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
      title: 'Gestão de Pessoas',
      items: [
        {
          icon: 'inbox',
          label: 'Solicitações Recebidas',
          route: '/solicitacoes-recebidas'
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
      items: [
        {
          icon: 'folder',
          label: 'Categorias de Servico',
          route: '/admin/categorias-servico'
        },
        {
          icon: 'category',
          label: 'Serviços',
          route: '/admin/servicos'
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
          icon: 'settings',
          label: 'Configurações',
          route: '/configuracoes'
        }
      ]
    }
  ];
}
