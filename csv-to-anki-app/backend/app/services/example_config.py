"""
Configuration for Enhanced Example Sources
"""

class ExampleSourceConfig:
    """Configuration for different example sentence sources"""
    
    # Available sources and their characteristics
    SOURCES = {
        'tatoeba': {
            'name': 'Tatoeba',
            'description': 'Community-curated sentence database with high-quality examples',
            'api_url': 'https://tatoeba.org/en/api_v0/search',
            'quality': 'high',
            'coverage': 'excellent',
            'free': True,
            'rate_limit': None,
            'enabled': True
        },
        'jisho': {
            'name': 'Jisho.org',
            'description': 'Popular Japanese-English dictionary with basic examples',
            'api_url': 'https://jisho.org/api/v1/search/words',
            'quality': 'medium',
            'coverage': 'good',
            'free': True,
            'rate_limit': None,
            'enabled': True
        },
        'weblio': {
            'name': 'Weblio',
            'description': 'Professional dictionary with business-grade examples',
            'api_url': 'https://weblio.jp/api',
            'quality': 'very_high',
            'coverage': 'good',
            'free': False,
            'rate_limit': '1000/day',
            'enabled': False,  # Requires API key
            'api_key_required': True
        },
        'linguee': {
            'name': 'Linguee',
            'description': 'Real-world usage examples from published sources',
            'api_url': 'https://linguee-api.herokuapp.com',
            'quality': 'high',
            'coverage': 'medium',
            'free': True,
            'rate_limit': 'moderate',
            'enabled': False,  # Placeholder for future implementation
        }
    }
    
    # Default priority order (higher priority sources are tried first)
    DEFAULT_PRIORITY = ['tatoeba', 'jisho', 'weblio', 'linguee']
    
    # Quality scoring weights
    QUALITY_WEIGHTS = {
        'length_optimal': 1.0,      # Sentence length is in optimal range
        'contains_target': 2.0,     # Contains the exact target word
        'has_punctuation': 0.5,     # Has proper punctuation
        'particle_count': 0.2,      # Number of particles (per particle, max 1.0)
        'common_patterns': 0.3,     # Contains common Japanese patterns
        'source_quality': {         # Bonus based on source quality
            'very_high': 1.0,
            'high': 0.7,
            'medium': 0.4,
            'low': 0.0
        }
    }
    
    # Example selection preferences
    SELECTION_PREFS = {
        'max_examples_per_source': 3,
        'optimal_sentence_length': (10, 50),  # characters
        'min_sentence_length': 5,
        'max_sentence_length': 100,
        'prefer_natural_speech': True,
        'avoid_technical_terms': True,
        'prefer_common_vocabulary': True
    }

    @classmethod
    def get_enabled_sources(cls):
        """Get list of enabled sources in priority order"""
        enabled = []
        for source in cls.DEFAULT_PRIORITY:
            if source in cls.SOURCES and cls.SOURCES[source]['enabled']:
                enabled.append(source)
        return enabled
    
    @classmethod
    def get_source_info(cls, source_name):
        """Get information about a specific source"""
        return cls.SOURCES.get(source_name, {})
    
    @classmethod
    def is_source_available(cls, source_name):
        """Check if a source is available and enabled"""
        source_info = cls.get_source_info(source_name)
        return source_info.get('enabled', False)
