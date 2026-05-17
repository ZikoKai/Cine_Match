# -*- coding: utf-8 -*-
"""Orchestrateur Principal - Pipeline de Production Cinématographique"""

import asyncio
import time
from typing import Dict, Optional, List, Callable
from datetime import datetime
from pathlib import Path

from task2.core.dalle_client import AzureDalleClient
from task2.core.gpt_client import GPT4oClient
from task2.core.vision_analysis import VisionAnalyzer
from task2.enhancement.image_enhancer import ImageEnhancer
from task2.enhancement.fallback import CanvasFallback
from task2.storage.local_storage import LocalStorage
from task2.storage.cloud_storage import R2Storage
from task2.utils.logger import get_logger
from task2.utils.metrics import MetricsCollector

logger = get_logger(__name__)


class PosterOrchestrator:
    """
    Orchestre la pipeline complÃ¨te : 
    Metadata -> Poster Analysis (Vision) -> Prompt Artistique -> Image DALL-E -> Post-prod Pro.
    
    Styles de prompt disponibles:
    - "realistic": Personnages rÃ©alistes, dÃ©tails peau/capture du regard
    - "abstract": MÃ©taphores visuelles, compositions artistiques
    - "minimal": Ã‰purÃ©, design Ã©purÃ©, impact maximal
    - "hybrid": MÃ©lange de rÃ©alisme et d'abstraction pour un style unique

    
    Styles d'amÃ©lioration disponibles:
    - "cinematic": Effets hollywoodiens (bloom, glow, particules)
    - "minimal": Style Ã©purÃ©, peu d'effets
    - "vintage": Grain sÃ©pia, rayures, style rÃ©tro
    - "neon": Cyberpunk, lueurs nÃ©on, grilles
    - "neonoir": Style noir et blanc avec des touches nÃ©on
    """
    
    def __init__(
        self, 
        prompt_style: str = "minimal",
        enhancement_style: str = "minimal",
        enable_cloud: bool = False,
        enable_vision_analysis: bool = True,
        max_retries: int = 2
    ):
        """
        Initialise l'orchestrateur avec les styles choisis
        
        Args:
            prompt_style: Style de prompt GPT-4o ("realistic", "abstract", "minimal", "hybrid")
            enhancement_style: Style d'amÃ©lioration ("cinematic", "minimal", "vintage", "neon", "neonoir")
            enable_cloud: Activer le stockage cloud (R2)
            enable_vision_analysis: Analyser le poster original TMDB avec GPT-4o Vision avant gÃ©nÃ©ration (activÃ© par dÃ©faut)
            max_retries: Nombre maximum de tentatives
        """
        self.dalle = AzureDalleClient()
        self.gpt = GPT4oClient(prompt_style=prompt_style)
        self.vision = VisionAnalyzer() if enable_vision_analysis else None
        self.enhancer = ImageEnhancer()
        self.fallback = CanvasFallback()
        self.storage = LocalStorage()
        self.cloud_storage = R2Storage() if enable_cloud else None
        
        self.prompt_style = prompt_style
        self.enhancement_style = enhancement_style
        self.enable_vision_analysis = enable_vision_analysis
        self.max_retries = max_retries
        
        # MÃ©triques
        self.metrics = MetricsCollector()
        self.session_stats = {
            'start_time': None,
            'total_generations': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'dalle_used': 0,
            'fallback_used': 0,
            'vision_analyses': 0,
            'total_duration': 0
        }
        
        logger.info(f"ðŸŽ¬ Orchestrateur initialisÃ©")
        logger.info(f"   Style prompt: {prompt_style}")
        logger.info(f"   Style enhancement: {enhancement_style}")
        logger.info(f"   Vision analysis: {'ActivÃ©e' if enable_vision_analysis else 'DÃ©sactivÃ©e'}")
        logger.info(f"   Cloud storage: {'ActivÃ©' if enable_cloud else 'DÃ©sactivÃ©'}")
    
    async def generate_poster(
        self, 
        movie: Dict, 
        save_local: bool = True, 
        enhance: bool = True,
        upload_cloud: bool = False,
        callback: Optional[Callable] = None,
        generate_variations: bool = False,
        analyze_original_poster: bool = True
    ) -> Optional[Dict]:
        """
        GÃ©nÃ¨re une affiche haute qualitÃ© pour un film.
        
        Args:
            movie: Dictionnaire du film (id, title, genres, year, synopsis/overview, poster_path)
            save_local: Sauvegarder localement
            enhance: Appliquer la post-production
            upload_cloud: Upload vers Cloudflare R2
            callback: Fonction de callback pour la progression
            generate_variations: GÃ©nÃ©rer des variations de l'affiche
            analyze_original_poster: Analyser le poster original TMDB avec Vision (si activÃ© dans __init__)
            
        Returns:
            Dictionnaire avec les rÃ©sultats
        """
        # DÃ©marrer la session
        if self.session_stats['start_time'] is None:
            self.session_stats['start_time'] = time.time()
        
        movie_id = movie.get('id', 0)
        title = movie.get('title', 'Unknown')
        genres = movie.get('genres', [])
        year = movie.get('year', 'Unknown')
        poster_path = movie.get('poster_path', movie.get('poster', ''))
        
        logger.info(f"{'='*60}")
        logger.info(f"ðŸš€ Lancement de la pipeline pour : {title}")
        logger.info(f"   ID: {movie_id}")
        logger.info(f"   Genres: {', '.join(genres[:3])}")
        logger.info(f"   Synopsis: {movie.get('synopsis', 'Aucun rÃ©sumÃ© disponible')}")
        logger.info(f"   AnnÃ©e: {year}")
        logger.info(f"   Style prompt: {self.prompt_style}")
        logger.info(f"   Style enhancement: {self.enhancement_style}")
        logger.info(f"   Vision analysis: {'Oui' if analyze_original_poster and self.vision else 'Non'}")
        logger.info(f"{'='*60}")
        
        # Callback dÃ©but
        if callback:
            await callback({'stage': 'start', 'movie_id': movie_id, 'title': title})
        
        start_time = time.time()
        retry_count = 0
        vision_analysis_result = None
        
        while retry_count <= self.max_retries:
            try:
                # --- Ã‰TAPE 0 (optionnelle): ANALYSE DU POSTER ORIGINAL ---
                if analyze_original_poster and self.vision and poster_path:
                    logger.info("  [0/5] GPT-4o Vision : Analyse du poster original TMDB...")
                    if callback:
                        await callback({'stage': 'vision_analysis', 'progress': 10})
                    
                    vision_analysis_result = await self.vision.analyze_from_path(poster_path)
                    
                    if vision_analysis_result and not vision_analysis_result.get("description", "").startswith("Failed"):
                        self.session_stats['vision_analyses'] += 1
                        logger.info(f"  âœ… Poster analysÃ©: {len(vision_analysis_result.get('color_palette', []))} couleurs extraites")
                        logger.debug(f"  Style canvas: {vision_analysis_result.get('style_canvas', 'N/A')}")
                        
                        # Enrichir le movie dict avec l'analyse visuelle
                        movie['vision_analysis'] = vision_analysis_result
                    else:
                        reason = vision_analysis_result.get("description", "Reason unknown") if vision_analysis_result else "Poster path missing"
                        logger.warning(f"  âš ï¸ Analyse Vision ignorÃ©e: {reason}")
                
                # --- Ã‰TAPE 1: RÃ‰DACTION DU BRIEF ARTISTIQUE ---
                logger.info("  [1/5] GPT-4o : CrÃ©ation du concept visuel...")
                if callback:
                    await callback({'stage': 'prompt', 'progress': 25})
                
                art_prompt = await self.gpt.build_prompt(movie)
                logger.debug(f"  Prompt gÃ©nÃ©rÃ© ({len(art_prompt)} caractÃ¨res)")
                
                # --- Ã‰TAPE 2: GÃ‰NÃ‰RATION DE L'IMAGE BRUTE ---
                logger.info("  [2/5] DALL-E 3 : GÃ©nÃ©ration de l'image haute dÃ©finition...")
                if callback:
                    await callback({'stage': 'generation', 'progress': 50})
                
                dalle_result = await self.dalle.generate(art_prompt)
                
                image_bytes = None
                source = "dalle"
                
                if dalle_result:
                    image_bytes, _ = dalle_result
                    self.session_stats['dalle_used'] += 1
                    logger.info(f"  âœ… Image brute gÃ©nÃ©rÃ©e ({len(image_bytes) // 1024} KB)")
                else:
                    # Fallback automatique en cas de rejet
                    logger.warning("  âš ï¸ DALL-E a Ã©chouÃ©. Utilisation du fallback Canvas...")
                    if callback:
                        await callback({'stage': 'fallback', 'progress': 60})
                    
                    image_bytes = await self.fallback.generate(
                        title, 
                        genres, 
                        style=self.enhancement_style
                    )
                    source = "fallback"
                    self.session_stats['fallback_used'] += 1
                    logger.info(f"  âœ… Fallback gÃ©nÃ©rÃ© ({len(image_bytes) // 1024} KB)")
                
                if not image_bytes:
                    raise ValueError("Ã‰chec critique : aucune donnÃ©e d'image n'a pu Ãªtre produite.")
                
                # --- Ã‰TAPE 3: SAUVEGARDE ---
                local_raw_path = None
                if save_local:
                    logger.info("  [3/5] Sauvegarde de l'image brute...")
                    if callback:
                        await callback({'stage': 'saving', 'progress': 75})
                    
                    local_raw_path = await self.storage.save(image_bytes, movie_id, f"{title}_raw")
                    if local_raw_path:
                        logger.info(f"  ðŸ’¾ SauvegardÃ©e: {Path(local_raw_path).name}")
                
                # --- Ã‰TAPE 4: POST-PRODUCTION ---
                enhanced_path = None
                if enhance and local_raw_path:
                    logger.info(f"  [4/5] Enhancer Pro : Post-production ({self.enhancement_style})...")
                    if callback:
                        await callback({'stage': 'enhancing', 'progress': 90})
                    
                    enhanced_path = await self.enhancer.enhance_poster(
                        local_raw_path, 
                        title, 
                        genres, 
                        year,
                        style=self.enhancement_style
                    )
                    
                    if enhanced_path:
                        logger.info(f"  âœ¨ Post-production terminÃ©e: {Path(enhanced_path).name}")
                
                # Upload cloud si demandÃ©
                cloud_url = None
                if upload_cloud and self.cloud_storage and enhanced_path:
                    logger.info("  â˜ï¸ Upload vers le cloud...")
                    cloud_url = await self.cloud_storage.upload(
                        enhanced_path, 
                        f"posters/{movie_id}.png"
                    )
                    if cloud_url:
                        logger.info(f"  â˜ï¸ URL cloud: {cloud_url}")
                
                # GÃ©nÃ©ration de variations (optionnel)
                variations = []
                if generate_variations and local_raw_path:
                    logger.info("  ðŸŽ¨ GÃ©nÃ©ration de variations...")
                    variations = await self.dalle.generate_variations(local_raw_path, n=4)
                    logger.info(f"  âœ… {len(variations)} variations gÃ©nÃ©rÃ©es")
                
                # MÃ©triques
                duration = time.time() - start_time
                self.session_stats['total_generations'] += 1
                self.session_stats['successful_generations'] += 1
                self.session_stats['total_duration'] += duration
                
                # RÃ©sultat
                result = {
                    'success': True,
                    'movie_id': movie_id,
                    'title': title,
                    'source': source,
                    'prompt_style': self.prompt_style,
                    'enhancement_style': self.enhancement_style,
                    'raw_path': local_raw_path,
                    'final_path': enhanced_path or local_raw_path,
                    'cloud_url': cloud_url,
                    'variations': variations,
                    'art_brief': art_prompt[:200] + "...",
                    'vision_analysis': vision_analysis_result,
                    'duration_seconds': round(duration, 2),
                    'retry_count': retry_count,
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"âœ… Pipeline terminÃ©e en {duration:.1f}s pour '{title}'")
                
                # Callback succÃ¨s
                if callback:
                    await callback({'stage': 'completed', 'progress': 100, 'result': result})
                
                return result
                
            except Exception as e:
                retry_count += 1
                logger.error(f"  âŒ Erreur (tentative {retry_count}/{self.max_retries}): {e}")
                
                if callback:
                    await callback({'stage': 'error', 'error': str(e), 'retry': retry_count})
                
                if retry_count <= self.max_retries:
                    wait_time = 2 ** retry_count
                    logger.info(f"  â³ Attente {wait_time}s avant nouvelle tentative...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"âŒ Ã‰chec final pour '{title}' aprÃ¨s {self.max_retries} tentatives")
                    
                    self.session_stats['total_generations'] += 1
                    self.session_stats['failed_generations'] += 1
                    
                    return {
                        'success': False,
                        'movie_id': movie_id,
                        'title': title,
                        'error': str(e),
                        'retry_count': retry_count - 1,
                        'timestamp': datetime.now().isoformat()
                    }
        
        return None
    
    async def generate_batch(
        self,
        movies: List[Dict],
        save_local: bool = True,
        enhance: bool = True,
        upload_cloud: bool = False,
        max_concurrent: int = 2,
        analyze_original_posters: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> List[Dict]:
        """
        GÃ©nÃ¨re des affiches pour plusieurs films en parallÃ¨le
        
        Args:
            movies: Liste des films
            save_local: Sauvegarder localement
            enhance: Appliquer post-production
            upload_cloud: Upload vers cloud
            max_concurrent: Nombre max de gÃ©nÃ©rations parallÃ¨les
            analyze_original_posters: Analyser le poster original TMDB avec Vision
            progress_callback: Callback pour progression globale
            
        Returns:
            Liste des rÃ©sultats
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"ðŸ“¦ DÃ‰MARRAGE DU BATCH")
        logger.info(f"   Films: {len(movies)}")
        logger.info(f"   Concurrence max: {max_concurrent}")
        logger.info(f"   Style prompt: {self.prompt_style}")
        logger.info(f"   Style enhancement: {self.enhancement_style}")
        logger.info(f"   Vision analysis: {'Oui' if analyze_original_posters and self.vision else 'Non'}")
        logger.info(f"{'='*60}")
        
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        completed = 0
        total = len(movies)
        
        async def generate_one(movie: Dict, idx: int):
            nonlocal completed
            async with semaphore:
                logger.info(f"\n[{idx+1}/{total}] Traitement: {movie.get('title')}")
                
                if progress_callback:
                    await progress_callback({
                        'current': idx + 1,
                        'total': total,
                        'movie': movie.get('title')
                    })
                
                result = await self.generate_poster(
                    movie, 
                    save_local=save_local, 
                    enhance=enhance,
                    upload_cloud=upload_cloud,
                    analyze_original_poster=analyze_original_posters
                )
                
                completed += 1
                
                if progress_callback:
                    await progress_callback({
                        'progress': int(completed / total * 100),
                        'completed': completed,
                        'total': total
                    })
                
                return result
        
        tasks = [generate_one(movie, i) for i, movie in enumerate(movies)]
        results = await asyncio.gather(*tasks)
        
        # Statistiques batch
        success_count = sum(1 for r in results if r and r.get('success'))
        failed_count = len(results) - success_count
        
        logger.info(f"\n{'='*60}")
        logger.info(f"ðŸ“Š RÃ‰SUMÃ‰ DU BATCH")
        logger.info(f"   Total: {len(results)}")
        logger.info(f"   âœ… SuccÃ¨s: {success_count}")
        logger.info(f"   âŒ Ã‰checs: {failed_count}")
        logger.info(f"   ðŸ“ˆ Taux: {success_count/len(results)*100:.1f}%")
        logger.info(f"{'='*60}")
        
        return results
    
    async def generate_with_preview(
        self, 
        movie: Dict,
        preview_callback: Optional[Callable] = None
    ) -> Optional[Dict]:
        """
        GÃ©nÃ©ration avec aperÃ§u intermÃ©diaire (pour interface utilisateur)
        
        Args:
            movie: DonnÃ©es du film
            preview_callback: Callback pour envoyer l'aperÃ§u Ã  chaque Ã©tape
        """
        async def internal_callback(data: Dict):
            if preview_callback:
                await preview_callback(data)
        
        return await self.generate_poster(movie, callback=internal_callback)
    
    def get_session_stats(self) -> Dict:
        """Retourne les statistiques de la session"""
        total_duration = time.time() - self.session_stats['start_time'] if self.session_stats['start_time'] else 0
        
        return {
            'session_duration_seconds': round(total_duration, 2),
            'total_generations': self.session_stats['total_generations'],
            'successful_generations': self.session_stats['successful_generations'],
            'failed_generations': self.session_stats['failed_generations'],
            'success_rate': round(
                self.session_stats['successful_generations'] / max(1, self.session_stats['total_generations']) * 100, 
                1
            ),
            'dalle_usage': self.session_stats['dalle_used'],
            'fallback_usage': self.session_stats['fallback_used'],
            'vision_analyses': self.session_stats['vision_analyses'],
            'avg_generation_time': round(
                self.session_stats['total_duration'] / max(1, self.session_stats['total_generations']), 
                2
            ),
            'prompt_style': self.prompt_style,
            'enhancement_style': self.enhancement_style
        }
    
    def print_summary(self):
        """Affiche un rÃ©sumÃ© de la session"""
        stats = self.get_session_stats()
        
        print("\n" + "="*60)
        print("ðŸ“Š RÃ‰SUMÃ‰ DE LA SESSION")
        print("="*60)
        print(f"DurÃ©e:              {stats['session_duration_seconds']} secondes")
        print(f"Total gÃ©nÃ©rations:  {stats['total_generations']}")
        print(f"SuccÃ¨s:             {stats['successful_generations']}")
        print(f"Ã‰checs:             {stats['failed_generations']}")
        print(f"Taux de succÃ¨s:     {stats['success_rate']}%")
        print(f"DALLÂ·E utilisÃ©:     {stats['dalle_usage']} fois")
        print(f"Fallback utilisÃ©:   {stats['fallback_usage']} fois")
        print(f"Vision analyses:    {stats['vision_analyses']} fois")
        print(f"Temps moyen:        {stats['avg_generation_time']} secondes")
        print(f"Style prompt:       {stats['prompt_style']}")
        print(f"Style enhancement:  {stats['enhancement_style']}")
        print("="*60)
