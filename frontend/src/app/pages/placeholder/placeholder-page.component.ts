import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-placeholder-page',
  standalone: true,
  imports: [
    MatIconModule
  ],
  templateUrl: './placeholder-page.component.html',
  styleUrl: './placeholder-page.component.scss'
})
export class PlaceholderPageComponent {
  @Input() title = '';
  @Input() icon = 'article';
}
