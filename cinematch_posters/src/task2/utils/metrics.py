# -*- coding: utf-8 -*-
"""Collecteur de métriques de performance pour la génération d'affiches"""

import time
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime


@dataclass
class GenerationMetrics:
    """MÃ©triques de gÃ©nÃ©ration"""
    movie_id: int
    title: str
    start_time: float
    end_time: float = None
    success: bool = False
    source: str = None
    size_bytes: int = 0
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return 0
    
    def to_dict(self) -> Dict:
        return {
            'movie_id': self.movie_id,
            'title': self.title,
            'duration': self.duration,
            'success': self.success,
            'source': self.source,
            'size_bytes': self.size_bytes,
            'timestamp': datetime.now().isoformat()
        }


class MetricsCollector:
    """Collecteur de mÃ©triques"""
    
    def __init__(self):
        self.metrics: List[GenerationMetrics] = []
        self.start_time = time.time()
    
    def start_generation(self, movie_id: int, title: str) -> GenerationMetrics:
        """DÃ©marre le chronomÃ©trage pour un film"""
        metric = GenerationMetrics(
            movie_id=movie_id,
            title=title,
            start_time=time.time()
        )
        self.metrics.append(metric)
        return metric
    
    def end_generation(self, metric: GenerationMetrics, success: bool, source: str, size_bytes: int):
        """Termine le chronomÃ©trage"""
        metric.end_time = time.time()
        metric.success = success
        metric.source = source
        metric.size_bytes = size_bytes
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques globales"""
        if not self.metrics:
            return {}
        
        total = len(self.metrics)
        successful = sum(1 for m in self.metrics if m.success)
        failed = total - successful
        
        durations = [m.duration for m in self.metrics if m.success]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        sources = {}
        for m in self.metrics:
            if m.source:
                sources[m.source] = sources.get(m.source, 0) + 1
        
        return {
            'total': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'avg_duration_seconds': avg_duration,
            'total_duration_seconds': time.time() - self.start_time,
            'sources': sources
        }
    
    def print_summary(self):
        """Affiche un rÃ©sumÃ©"""
        stats = self.get_stats()
        print("\n" + "="*60)
        print("ðŸ“Š STATISTIQUES DE GÃ‰NÃ‰RATION")
        print("="*60)
        print(f"Total films:        {stats.get('total', 0)}")
        print(f"SuccÃ¨s:             {stats.get('successful', 0)}")
        print(f"Ã‰checs:             {stats.get('failed', 0)}")
        print(f"Taux de succÃ¨s:     {stats.get('success_rate', 0):.1f}%")
        print(f"DurÃ©e moyenne:      {stats.get('avg_duration_seconds', 0):.1f} secondes")
        print(f"DurÃ©e totale:       {stats.get('total_duration_seconds', 0):.1f} secondes")
        
        if stats.get('sources'):
            print(f"\nSources:")
            for source, count in stats['sources'].items():
                print(f"  - {source}: {count}")
        print("="*60)
