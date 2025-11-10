"""
Servicio de búsqueda de literatura científica educativa
Integra Semantic Scholar y OpenAlex APIs (gratuitas)
"""
import requests
import logging
from typing import List, Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class ResearchSearchService:
    """Servicio para buscar artículos científicos en bases de datos académicas"""
    
    SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    OPENALEX_URL = "https://api.openalex.org/works"
    
    def __init__(self):
        self.timeout = 10
        self.max_results = 5
    
    def search_semantic_scholar(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Buscar en Semantic Scholar API
        
        Args:
            query: Términos de búsqueda
            limit: Número máximo de resultados
            
        Returns:
            Lista de papers con estructura normalizada
        """
        try:
            params = {
                'query': query,
                'limit': limit,
                'fields': 'title,abstract,year,authors,url,citationCount'
            }
            
            response = requests.get(
                self.SEMANTIC_SCHOLAR_URL,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                papers = data.get('data', [])
                return self._normalize_semantic_scholar(papers)
            else:
                logger.error(f"Semantic Scholar error: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Semantic Scholar search: {e}")
            return []
    
    def search_openalex(self, query: str, per_page: int = 5) -> List[Dict]:
        """
        Buscar en OpenAlex API
        
        Args:
            query: Términos de búsqueda
            per_page: Número de resultados por página
            
        Returns:
            Lista de papers con estructura normalizada
        """
        try:
            params = {
                'search': query,
                'per_page': per_page,
                'mailto': 'research@evalai.com'  # Requerido por OpenAlex para mayor rate limit
            }
            
            response = requests.get(
                self.OPENALEX_URL,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                papers = data.get('results', [])
                return self._normalize_openalex(papers)
            else:
                logger.error(f"OpenAlex error: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching OpenAlex: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in OpenAlex search: {e}")
            return []
    
    def search_combined(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Busca en ambas APIs y combina resultados
        
        Args:
            query: Términos de búsqueda
            limit: Total de resultados deseados
            
        Returns:
            Lista combinada de papers únicos
        """
        # Buscar en ambas fuentes
        semantic_papers = self.search_semantic_scholar(query, limit=limit)
        openalex_papers = self.search_openalex(query, per_page=limit)
        
        # Combinar y deduplicar por título
        all_papers = semantic_papers + openalex_papers
        unique_papers = self._deduplicate_papers(all_papers)
        
        # Ordenar por relevancia (citaciones + año)
        sorted_papers = sorted(
            unique_papers,
            key=lambda p: (p.get('citations', 0) * 0.7 + (p.get('year', 2000) - 2000) * 0.3),
            reverse=True
        )
        
        return sorted_papers[:limit]
    
    def _normalize_semantic_scholar(self, papers: List[Dict]) -> List[Dict]:
        """Normaliza la respuesta de Semantic Scholar"""
        normalized = []
        
        for paper in papers:
            try:
                authors = [
                    author.get('name', 'Unknown')
                    for author in paper.get('authors', [])
                ]
                
                normalized.append({
                    'title': paper.get('title', 'Sin título'),
                    'abstract': paper.get('abstract', 'Sin resumen disponible'),
                    'year': paper.get('year', None),
                    'authors': authors[:5],  # Limitar a 5 autores
                    'url': paper.get('url', ''),
                    'citations': paper.get('citationCount', 0),
                    'source': 'Semantic Scholar'
                })
            except Exception as e:
                logger.warning(f"Error normalizing Semantic Scholar paper: {e}")
                continue
        
        return normalized
    
    def _normalize_openalex(self, papers: List[Dict]) -> List[Dict]:
        """Normaliza la respuesta de OpenAlex"""
        normalized = []
        
        for paper in papers:
            try:
                # Extraer autores
                authorships = paper.get('authorships', [])
                authors = [
                    auth.get('author', {}).get('display_name', 'Unknown')
                    for auth in authorships
                ]
                
                # Extraer abstract (puede estar en inverted_abstract)
                abstract = ''
                inverted_abstract = paper.get('abstract_inverted_index', {})
                if inverted_abstract:
                    # Reconstruir abstract desde índice invertido
                    words = []
                    for word, positions in inverted_abstract.items():
                        for pos in positions:
                            words.append((pos, word))
                    words.sort()
                    abstract = ' '.join([w[1] for w in words])
                
                normalized.append({
                    'title': paper.get('title', 'Sin título'),
                    'abstract': abstract or 'Sin resumen disponible',
                    'year': paper.get('publication_year', None),
                    'authors': authors[:5],
                    'url': paper.get('doi', '') or paper.get('id', ''),
                    'citations': paper.get('cited_by_count', 0),
                    'source': 'OpenAlex'
                })
            except Exception as e:
                logger.warning(f"Error normalizing OpenAlex paper: {e}")
                continue
        
        return normalized
    
    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """Elimina papers duplicados por título similar"""
        unique = {}
        
        for paper in papers:
            # Usar título normalizado como clave
            title_key = paper.get('title', '').lower().strip()
            
            if title_key and title_key not in unique:
                unique[title_key] = paper
            elif title_key in unique:
                # Si ya existe, quedarse con el que tiene más citaciones
                if paper.get('citations', 0) > unique[title_key].get('citations', 0):
                    unique[title_key] = paper
        
        return list(unique.values())


# Instancia global del servicio
research_search_service = ResearchSearchService()
