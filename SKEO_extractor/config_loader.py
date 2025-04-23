# config_loader.py - Loads and merges parameters

import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('skeo.config')

def load_params(params_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load parameters from YAML file, merging with defaults.

    Args:
        params_file: Optional path to parameters YAML file.

    Returns:
        Dict containing parameters.
    """
    # Define default parameters including API slugs and paths
    default_params = {
        "llm": {
            "api_endpoint": "https://api.openai.com", # Base URL
            "api_key": os.getenv("LLM_API_KEY"), # Get from env var by default
            "model": "gpt-4-1106-preview",
            "api_base_path": "/v1", # Base path for API calls
            "chat_endpoint": "/chat/completions", # Specific chat endpoint
            "health_endpoint": None, # Health check endpoint often unused
            "max_tokens": 4096,
            "temperature": 0.2,
            "retry_attempts": 3,
            "timeout_seconds": 120,
            "validation_mode": "strict" # strict or lenient
        },
        "pdf": {
            "extract_method": "docling", # 'docling' or 'pymupdf'
            "search_metadata": True,
            "max_text_length": 150000,
            "language_detection": True,
            # Docling specific options
            "docling_options": {
                "max_num_pages": None, # No limit by default
                "max_file_size": None, # No limit by default
                "artifacts_path": os.getenv("DOCLING_ARTIFACTS_PATH"), # Allow overriding via env var
                "enable_remote_services": False, # Default to False for privacy
                # Enrichment options (disabled by default)
                "do_code_enrichment": False,
                "do_formula_enrichment": False,
                "do_picture_classification": False,
                "do_picture_description": False,
                "generate_picture_images": False, # Required for picture classification/description
                "images_scale": 2,
                # Table structure options
                "do_table_structure": True,
                "table_structure_mode": "ACCURATE", # ACCURATE or FAST
                "table_do_cell_matching": True, # Map back to PDF cells
            }
        },
        "metadata": {
            # SerpApi Google Scholar configuration
            "serpapi_api_key": os.getenv("SERPAPI_API_KEY"), # Get from env var
            "serpapi_google_scholar_params": { # Default parameters for Google Scholar searches
                "hl": "en", # Language: English
                "num": 10, # Number of results per page (max 20)
                "as_vis": "0", # Include citations (default)
                "as_ylo": None, # Optional: Start year filter
                "as_yhi": None, # Optional: End year filter
            }
        },
        "extraction": {
            "confidence_threshold": 0.6, # Filtering based on this is currently manual
            "extract_components": [ # Components to attempt extraction for
                "research_context", "theoretical_basis", "research_problem",
                "knowledge_gap", "research_question", "future_direction",
                "potential_application", "scientific_challenge",
                "methodological_challenge", "implementation_challenge",
                "limitation", "methodological_framework",
                "material_tool"
            ],
        },
        "processing": {
            "max_workers": 4, # Controls asyncio semaphore for concurrency
            "fail_fast": False,
            "skip_existing": True # Skip generating output JSON if it exists
        },
        "output": {
            "verbose_output": True # Controls some logging detail
        },
        "strapi": {
            "url": os.getenv("STRAPI_URL", "http://localhost:1337"),
            "token": os.getenv("STRAPI_API_TOKEN"), # Get from env var by default
            "api_base_path": "/api", # Strapi API base path
            "direct_upload": False,
            "upload_batch_size": 20, # Conceptual, currently uploads one by one
            "test_endpoints": True,
            "retry_failed_uploads": False, # Complex dependency retry logic not implemented
            "api_slugs": { # Mapping from internal key to Strapi API ID (plural)
                "scientific_paper": "sciknow-25x1-scientific-papers",
                "research_context": "sciknow-25x1-research-contexts",
                "theoretical_basis": "sciknow-25x1-theoretical-bases",
                "research_problem": "sciknow-25x1-research-problems",
                "knowledge_gap": "sciknow-25x1-knowledge-gaps",
                "research_question": "sciknow-25x1-research-questions",
                "future_direction": "sciknow-25x1-future-directions",
                "potential_application": "sciknow-25x1-potential-applications",
                "scientific_challenge": "sciknow-25x1-scientific-challenges",
                "methodological_challenge": "sciknow-25x1-methodological-challenges",
                "implementation_challenge": "sciknow-25x1-implementation-challenges",
                "limitation": "sciknow-25x1-limitations",
                "methodological_framework": "sciknow-25x1-methodological-frameworks",
                "material_tool": "sciknow-25x1-material-tools",
                # Add slugs for components if used
            }
        }
    }

    # Function to recursively merge dictionaries
    def merge_dicts(base, overlay):
        for k, v in overlay.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                merge_dicts(base[k], v)
            else:
                # Override or add new key, only if value is not None
                # This prevents None values in custom_params from overwriting defaults
                # unless the default was also None.
                if v is not None or base.get(k) is None:
                    base[k] = v


    if params_file:
        logger.info(f"Loading parameters from: {params_file}")
        try:
            with open(params_file, 'r', encoding='utf-8') as f:
                custom_params = yaml.safe_load(f)
                if not isinstance(custom_params, dict):
                    logger.warning(f"Parameter file {params_file} is not a valid dictionary. Using defaults.")
                    return default_params

            # Start with defaults and merge custom params on top
            merged_params = default_params.copy() # Deep copy? Not strictly needed if merge_dicts handles it
            merge_dicts(merged_params, custom_params)
            logger.info("Successfully merged custom parameters.")
            return merged_params

        except FileNotFoundError:
            logger.warning(f"Parameter file {params_file} not found. Using default parameters.")
        except yaml.YAMLError as e:
            logger.warning(f"Error parsing parameter file {params_file}: {e}. Using default parameters.")
        except Exception as e:
            logger.error(f"Unexpected error loading parameters from {params_file}: {e}. Using defaults.")

    else:
         logger.info("No parameter file specified. Using default parameters.")

    # Ensure API keys from environment are loaded if not overridden by file
    if not default_params["llm"]["api_key"]:
        default_params["llm"]["api_key"] = os.getenv("LLM_API_KEY")
    if not default_params["metadata"]["serpapi_api_key"]:
        default_params["metadata"]["serpapi_api_key"] = os.getenv("SERPAPI_API_KEY")
    if not default_params["strapi"]["token"]:
        default_params["strapi"]["token"] = os.getenv("STRAPI_API_TOKEN")

    return default_params