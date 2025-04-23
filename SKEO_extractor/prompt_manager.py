# prompt_manager.py - Manages prompts for SKEO component extraction

import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger('skeo.prompts')

class PromptManager:
    """Manage prompts for different components of the SKEO ontology"""

    def __init__(self, prompt_file: str, params: Optional[Dict] = None):
        """
        Initialize with prompts from YAML file.

        Args:
            prompt_file (str): Path to YAML file containing prompts.
            params: Optional parameters dict containing potential overrides under 'prompts' key.
        """
        self.params = params if params else {}
        self.prompts = {}
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)

            if not isinstance(self.prompts, dict):
                raise ValueError("Prompt file content must be a YAML dictionary.")

            # Validate required prompts (optional, based on config)
            extraction_params = self.params.get('extraction', {})
            required_components = extraction_params.get('extract_components', [])
            missing_prompts = [comp for comp in required_components if comp not in self.prompts]
            if missing_prompts:
                logger.warning(f"Missing prompts in {prompt_file} for configured components: {', '.join(missing_prompts)}")

             # Apply custom prompt overrides from params['prompts']
            if 'prompts' in self.params and isinstance(self.params['prompts'], dict):
                for component, prompt_override in self.params['prompts'].items():
                     if component in self.prompts and isinstance(prompt_override, str):
                          self.prompts[component] = prompt_override
                          logger.info(f"Using custom prompt override for '{component}' from parameters.")
                     elif isinstance(prompt_override, str):
                          self.prompts[component] = prompt_override # Allow adding new prompts via params
                          logger.info(f"Added new prompt for '{component}' from parameters.")
                     else:
                          logger.warning(f"Ignoring invalid prompt override for '{component}' in parameters (must be a string).")

            logger.info(f"Loaded {len(self.prompts)} prompts initially from {prompt_file}.")

        except FileNotFoundError:
             logger.error(f"Prompt file not found: {prompt_file}")
             raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML prompt file {prompt_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading prompts from {prompt_file}: {str(e)}")
            raise

    def get_prompt(self, component_name: str, extracted_text: Dict[str, Any]) -> str:
        """
        Get the prompt for a specific component, formatted with relevant extracted text.

        Args:
            component_name: Name of the SKEO component (e.g., "research_problem").
            extracted_text: Dict containing 'metadata' and 'sections' from PDFProcessor.

        Returns:
            Formatted prompt string ready for the LLM.
        """
        if component_name not in self.prompts:
            logger.error(f"No prompt template defined for component: {component_name}. Using generic instruction.")
            return f"Extract information relevant to {component_name} from the provided text. Respond in JSON format."

        prompt_template = self.prompts[component_name]

        # Select relevant text sections based on component
        title = extracted_text.get('metadata', {}).get('title', 'N/A')
        abstract = extracted_text.get('sections', {}).get('abstract', '')
        introduction = extracted_text.get('sections', {}).get('introduction', '')
        methodology = extracted_text.get('sections', {}).get('methodology', '')
        results = extracted_text.get('sections', {}).get('results', '')
        discussion = extracted_text.get('sections', {}).get('discussion', '')
        conclusion = extracted_text.get('sections', {}).get('conclusion', '')
        # full_text = extracted_text.get('full_text', '') # Use sparingly

        # Limit section lengths to avoid excessive prompt size
        max_section_len = 10000 # Max chars per section included in prompt context

        text_context = f"Title: {title}\n\n"

        # --- Component-Specific Text Selection Heuristics ---
        if component_name in ["research_context", "theoretical_basis", "research_problem", "scientific_challenge"]:
            text_context += f"Abstract:\n{abstract[:max_section_len]}\n\nIntroduction:\n{introduction[:max_section_len]}\n\nConclusion:\n{conclusion[:max_section_len]}"
        elif component_name in ["knowledge_gap", "research_question"]:
             text_context += f"Abstract:\n{abstract[:max_section_len]}\n\nIntroduction:\n{introduction[:max_section_len]}\n\nDiscussion:\n{discussion[:max_section_len]}\n\nConclusion:\n{conclusion[:max_section_len]}"
        elif component_name in ["future_direction", "potential_application"]:
             text_context += f"Abstract:\n{abstract[:max_section_len]}\n\nResults:\n{results[:max_section_len]}\n\nDiscussion:\n{discussion[:max_section_len]}\n\nConclusion:\n{conclusion[:max_section_len]}"
        elif component_name in ["methodological_challenge", "implementation_challenge", "limitation"]:
             text_context += f"Abstract:\n{abstract[:max_section_len]}\n\nMethodology:\n{methodology[:max_section_len]}\n\nResults:\n{results[:max_section_len]}\n\nDiscussion:\n{discussion[:max_section_len]}"
        elif component_name == "methodological_framework":
             text_context += f"Abstract:\n{abstract[:max_section_len]}\n\nIntroduction:\n{introduction[:max_section_len]}\n\nMethodology:\n{methodology[:max_section_len]}\n\nResults:\n{results[:max_section_len]}" # Include results for context
        elif component_name == "material_tool":
             text_context += f"Methodology:\n{methodology[:max_section_len]}\n\nResults:\n{results[:max_section_len]}" # Often detailed in methods/results
        else:
            logger.warning(f"Using default text sections (Abstract, Intro, Conclusion) for unrecognized component: {component_name}")
            text_context += f"Abstract:\n{abstract[:max_section_len]}\n\nIntroduction:\n{introduction[:max_section_len]}\n\nConclusion:\n{conclusion[:max_section_len]}"

        # Ensure context is not excessively long overall
        max_total_context = 30000
        if len(text_context) > max_total_context:
            logger.warning(f"Truncating text context for {component_name} prompt.")
            text_context = text_context[:max_total_context] + "\n... [Context Truncated]"


        # Format the prompt using .format() - ensure template uses {text}
        try:
            # Basic sanitization to avoid breaking format syntax
            sanitized_context = text_context.replace('{', '{{').replace('}', '}}')
            # Ensure the template actually has a {text} placeholder
            if '{text}' not in prompt_template:
                 logger.warning(f"Prompt template for '{component_name}' does not contain '{{text}}' placeholder. Appending context.")
                 formatted_prompt = prompt_template + "\n\nPaper Context:\n" + sanitized_context
            else:
                 formatted_prompt = prompt_template.format(text=sanitized_context)
            return formatted_prompt
        except KeyError as e:
             logger.error(f"Prompt template for '{component_name}' is missing a required format key: {e}. Template: '{prompt_template[:100]}...'")
             return f"Extract {component_name} information from the text: {text_context}\nRespond in JSON." # Fallback
        except Exception as e:
            logger.error(f"Error formatting prompt for '{component_name}': {e}")
            return f"Extract {component_name} information from the text: {text_context}\nRespond in JSON." # Fallback