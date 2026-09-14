import { AsyncPipe } from '@angular/common';
import { Component, Input, OnInit } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';

import { User } from '../../../core/models/user';
import { AuthService } from '../../../core/services/auth.service';
import { ServiceCategoryService } from '../../../core/services/service-category.service';

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
export class SidebarComponent implements OnInit {
  @Input() collapsed = false;
  currentUser$ = this.authService.currentUser$;

  constructor(
    private readonly authService: AuthService,
    private readonly serviceCategoryService: ServiceCategoryService
  ) {}

  menuSections: MenuSection[] = [
    {
      items: [
        {
          icon: 'apps',
          label: 'Serviços Disponíveis',
          route: '/'
        }
      ]
    },
    {
      items: [
        {
          icon: 'assignment_turned_in',
          label: 'Minhas Solicitações',
          route: '/minhas-solicitacoes'
        },
        {
          icon: 'inbox',
          label: 'Caixa Postal',
          route: '/caixa-postal'
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
          label: 'Unidades',
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

  ngOnInit(): void {
    this.loadMainMenuCategories();
  }

  canShowSection(section: MenuSection, user: User | null): boolean {
    return !section.adminOnly || this.authService.isSystemAdminUser(user);
  }

  private loadMainMenuCategories(): void {
    this.serviceCategoryService.list().subscribe({
      next: (categories) => {
        const categoryItems = categories
          .filter((category) => category.active && category.show_on_main_menu)
          .sort((first, second) => {
            const order = first.display_order - second.display_order;
            return order || first.name.localeCompare(second.name, 'pt-BR');
          })
          .map((category) => ({
            icon: 'folder_open',
            label: category.name,
            route: `/categorias/${category.id}`
          }));

        const mainItems = this.menuSections[0].items;
        this.menuSections[0].items = [
          mainItems[0],
          ...categoryItems
        ];
      }
    });
  }
}
