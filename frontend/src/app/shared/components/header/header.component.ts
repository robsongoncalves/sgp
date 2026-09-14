import { AsyncPipe } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { MatBadgeModule } from '@angular/material/badge';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from '@angular/material/tooltip';

import { User } from '../../../core/models/user';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [
    AsyncPipe,
    RouterLink,
    MatBadgeModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatToolbarModule,
    MatTooltipModule
  ],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  @Output() menuToggle = new EventEmitter<void>();

  appName = 'Portal de Serviços';
  appSubtitle = 'UNIPAMPA-PROGEPE';
  unreadMessages = 3;
  currentUser$ = this.authService.currentUser$;

  constructor(
    private readonly authService: AuthService,
    private readonly router: Router
  ) {}

  onMenuToggle(): void {
    this.menuToggle.emit();
  }

  initials(user: User | null): string {
    if (!user?.name) {
      return '--';
    }

    return user.name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0].toUpperCase())
      .join('');
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
