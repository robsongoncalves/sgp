import { Component, HostListener } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';

import { HeaderComponent } from './shared/components/header/header.component';
import { SidebarComponent } from './shared/components/sidebar/sidebar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    HeaderComponent,
    SidebarComponent,
    MatSidenavModule
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  isMenuCollapsed = this.isMobileViewport();

  constructor(private readonly router: Router) {}

  get isAuthLayout(): boolean {
    return this.router.url.startsWith('/login');
  }

  toggleMenu(): void {
    this.isMenuCollapsed = !this.isMenuCollapsed;
  }

  @HostListener('window:resize')
  onResize(): void {
    if (this.isMobileViewport()) {
      this.isMenuCollapsed = true;
    }
  }

  private isMobileViewport(): boolean {
    return typeof window !== 'undefined' && window.innerWidth < 700;
  }
}
