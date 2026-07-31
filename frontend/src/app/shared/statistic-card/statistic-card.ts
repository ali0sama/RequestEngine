import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-statistic-card',
  imports: [CommonModule],
  templateUrl: './statistic-card.html',
  styleUrl: './statistic-card.css',
})
export class StatisticCard {
  @Input() icon = 'fa-solid fa-chart-bar';
  @Input() label = 'Statistic';
  @Input() value: number | string = 0;
  @Input() color = '#E60000';
}
