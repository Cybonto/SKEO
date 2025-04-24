# skeo_extractor.py - Main logic for extracting SKEO components

import os
import asyncio
import json
import uuid
import logging
import aiofiles
import re # Added for filename sanitization
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path # Import Path for better path handling

from pydantic import ValidationError

# Use relative imports for sibling modules
from llm_client import LLMClient
from metadata_fetcher import SerpApiMetadataFetcher
from pdf_processor import PDFProcessor
from prompt_manager import PromptManager
from strapi_client import StrapiClient
from config_loader import load_params
import skeo_models # Import the models module

logger = logging.getLogger('skeo.extractor')

class SKEOExtractor:
    """Main extractor class coordinates PDF processing and component extraction."""

    def __init__(self, prompt_file: str, output_dir: str, params: Optional[Dict] = None):
        self.params = params if params else load_params() # Load defaults if not provided
        # output_dir is now the BASE output directory, individual files determined by caller
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True) # Ensure base dir exists

        # Initialize clients using loaded params
        self.llm_client = LLMClient(self.params)
        # Initialize fetcher - it checks internally if API key exists
        self.metadata_fetcher = SerpApiMetadataFetcher(self.params)
        self.pdf_processor = PDFProcessor(self.llm_client, self.metadata_fetcher, self.params)
        self.prompt_manager = PromptManager(prompt_file, self.params)

        # Extraction settings from params
        extraction_params = self.params.get('extraction', {})
        self.extract_components = extraction_params.get('extract_components', [])
        if not isinstance(self.extract_components, list):
            logger.warning("extract_components in params is not a list, using default.")
            # Load default list if needed
            self.extract_components = load_params().get('extraction', {}).get('extract_components', [])

        # Initialize Strapi client ONLY if direct upload is enabled
        self.strapi_client = None
        strapi_params = self.params.get('strapi', {})
        if strapi_params.get('direct_upload', False):
            # Pass the already loaded params to StrapiClient
            self.strapi_client = StrapiClient(params=self.params)

        # Map internal component keys to Pydantic models from skeo_models module
        self.schema_models = {
            "research_context": skeo_models.ResearchContext,
            "theoretical_basis": skeo_models.TheoreticalBasis,
            "research_problem": skeo_models.ResearchProblem,
            "knowledge_gap": skeo_models.KnowledgeGap,
            "research_question": skeo_models.ResearchQuestion,
            "future_direction": skeo_models.FutureDirection,
            "potential_application": skeo_models.PotentialApplication,
            "scientific_challenge": skeo_models.ScientificChallenge,
            "methodological_challenge": skeo_models.MethodologicalChallenge,
            "implementation_challenge": skeo_models.ImplementationChallenge,
            "limitation": skeo_models.Limitation,
            "methodological_framework": skeo_models.MethodologicalFramework,
            "material_tool": skeo_models.MaterialTool,
            # Add other models if they are extracted as top-level components
        }
        # Validate configured components against available schemas
        for comp in self.extract_components:
            if comp not in self.schema_models:
                logger.warning(f"Component '{comp}' configured for extraction, but no matching Pydantic model found in self.schema_models.")


    def _generate_id(self) -> str:
        """Generate a unique string ID (UUID)."""
        return uuid.uuid4().hex

    # --- MODIFIED process_pdf SIGNATURE ---
    async def process_pdf(self, pdf_path: Union[str, Path], output_json_path: Union[str, Path]) -> Tuple[str, Union[Dict[str, Any], Exception]]:
        """
        Process a single PDF: extract text/metadata, extract components, link, save/upload.

        Args:
            pdf_path: Path to the input PDF file.
            output_json_path: The exact path where the output JSON should be saved.

        Returns:
            Tuple(original_pdf_path_string, result_dict_by_slug or Exception)
        """
        # Ensure paths are Path objects internally
        pdf_path = Path(pdf_path)
        output_json_path = Path(output_json_path)
        pdf_display_name = pdf_path.name # For logging

        logger.info(f"Starting processing for PDF: {pdf_display_name}")
        logger.info(f"Target output path: {output_json_path}")
        paper_uuid = self._generate_id() # Generate ID for this paper early

        try:
            # --- Step 1: Extract Text and Metadata ---
            extracted_text_data = await self.pdf_processor.extract_text_from_pdf(pdf_path)
            if not extracted_text_data or not extracted_text_data.get('metadata'):
                 raise ValueError(f"PDF processing failed to return essential data for {pdf_display_name}.")

            # --- Step 2: Prepare Base Paper Object using ScientificPaper model ---
            paper_metadata = extracted_text_data['metadata']
            paper_data = {
                "title": paper_metadata.get("title", "Title Not Found"),
                "authors": paper_metadata.get("authors", []), # List of Author dicts
                "abstract": extracted_text_data.get('sections', {}).get('abstract', paper_metadata.get('abstract')), # Use section abstract first
                "doi": paper_metadata.get("doi"),
                "publicationDate": paper_metadata.get("publicationDate", paper_metadata.get("year")),
                "journal": paper_metadata.get("journal"),
                "volume": paper_metadata.get("volume"),
                "issue": paper_metadata.get("issue"),
                "pages": paper_metadata.get("pages"),
                "keywords": paper_metadata.get("keywords", []),
                "pdfPath": str(pdf_path), # Store the path processed as string
                "fileUrl": paper_metadata.get("fileUrl", paper_metadata.get("pdfPath")), # Link from metadata search
                "extractionDate": datetime.now().isoformat(),
                "extractionConfidenceScore": 0.0, # Placeholder
                "id": paper_uuid # Internal UUID
            }
            try:
                paper_object = skeo_models.ScientificPaper.model_validate(paper_data)
                paper_dict = paper_object.model_dump(exclude_unset=True, mode='json')
            except ValidationError as ve:
                 logger.error(f"Failed to validate initial paper data for {pdf_display_name}: {ve}")
                 paper_dict = paper_data
            except AttributeError: # Fallback for Pydantic v1
                 try:
                     paper_object = skeo_models.ScientificPaper(**paper_data)
                     paper_dict = paper_object.dict(exclude_unset=True)
                 except ValidationError as ve_v1:
                      logger.error(f"Failed to validate initial paper data (v1) for {pdf_display_name}: {ve_v1}")
                      paper_dict = paper_data

            # --- Step 3: Extract SKEO Components Concurrently ---
            component_tasks = []
            valid_components_to_extract = [
                comp for comp in self.extract_components if comp in self.schema_models
            ]
            for component_key in valid_components_to_extract:
                 task = self._extract_single_component(
                     component_key, extracted_text_data, paper_uuid
                 )
                 component_tasks.append(task)

            component_results = await asyncio.gather(*component_tasks)

            # --- Step 4: Aggregate Results and Calculate Confidence ---
            slug_map = self.params.get('strapi', {}).get('api_slugs', {})
            paper_slug = slug_map.get("scientific_paper", "scientific_paper")

            aggregated_data_by_slug = {paper_slug: [paper_dict]}
            component_confidences = []

            for component_key, result_list in component_results:
                if result_list is not None: # Check if extraction was successful (returned list, maybe empty)
                    strapi_key = slug_map.get(component_key, component_key)
                    aggregated_data_by_slug[strapi_key] = result_list
                    for item in result_list:
                        if isinstance(item, dict):
                            component_confidences.append(item.get("extractionConfidence", 0.0))

            if component_confidences:
                avg_confidence = round(sum(component_confidences) / len(component_confidences), 4)
                # Check if paper_slug exists and has at least one item before accessing
                if paper_slug in aggregated_data_by_slug and aggregated_data_by_slug[paper_slug]:
                    aggregated_data_by_slug[paper_slug][0]["extractionConfidenceScore"] = avg_confidence
                else:
                    logger.warning(f"Could not assign average confidence for {pdf_display_name}: Paper data missing or empty.")


            # --- Step 5: Add Relationships (Simplified) ---
            await self._add_relationships(aggregated_data_by_slug)

            # --- Step 6: Save/Upload Result ---
            # --- MODIFIED CALL to pass output_json_path ---
            await self._save_and_upload_result(aggregated_data_by_slug, pdf_path, output_json_path)

            logger.info(f"Successfully finished processing PDF: {pdf_display_name}")
            # --- Return original path as string ---
            return (str(pdf_path), aggregated_data_by_slug)

        except Exception as e:
            logger.error(f"Failed processing PDF {pdf_display_name}: {str(e)}", exc_info=True)
            # --- Return original path as string ---
            return (str(pdf_path), e) # Return exception for handling in main loop

    # --- _extract_single_component remains the same ---
    async def _extract_single_component(self, component_key: str, extracted_text: Dict[str, Any], paper_id: str) -> Tuple[str, Optional[List[Dict]]]:
        """Extracts data for a single SKEO component. Returns list or None on failure."""
        logger.info(f"Extracting component: {component_key}")
        results_list = []
        try:
            prompt = self.prompt_manager.get_prompt(component_key, extracted_text)
            schema_model = self.schema_models.get(component_key)
            if not schema_model:
                 logger.error(f"No schema model found for component key {component_key}. Cannot extract.")
                 return (component_key, []) # Return empty list, not None, to indicate no data found

            # LLM Client now returns None on definitive failure
            extracted_json = await self.llm_client.extract_json(prompt, schema_model)

            if extracted_json is None:
                 logger.warning(f"LLM extraction failed definitively for {component_key} after retries.")
                 return (component_key, []) # Return empty list, extraction attempted but failed

            # Ensure result is always a list for consistent processing downstream
            if isinstance(extracted_json, dict):
                extracted_json = [extracted_json]
            elif not isinstance(extracted_json, list):
                 logger.warning(f"LLM returned unexpected type {type(extracted_json)} for {component_key}. Expected dict or list. Discarding.")
                 return (component_key, []) # Return empty list

            # Process each extracted item dict
            for item_dict in extracted_json:
                 if isinstance(item_dict, dict):
                     # Add internal ID and link to paper before final validation
                     item_dict["id"] = self._generate_id()
                     item_dict["paper"] = paper_id
                     # Pydantic default should handle confidence, but set default here just in case
                     item_dict.setdefault("extractionConfidence", 0.7)

                     try:
                          # Final validation with added fields (id, paper)
                          # Ensure model includes these Optional fields
                          validated_item = schema_model.model_validate(item_dict)
                          # Use model_dump for Pydantic v2
                          results_list.append(validated_item.model_dump(exclude_unset=True, mode='json'))
                     except ValidationError as ve:
                           logger.warning(f"Schema validation failed for item in {component_key}: {ve}. Item (first 200 chars): {str(item_dict)[:200]}")
                           # Option: append raw item_dict if validation fails? Or skip? Skipping for now.
                     except AttributeError: # Fallback for Pydantic v1
                          try:
                              validated_item = schema_model(**item_dict)
                              results_list.append(validated_item.dict(exclude_unset=True))
                          except ValidationError as ve_v1:
                               logger.warning(f"Schema validation failed (v1) for item in {component_key}: {ve_v1}. Item (first 200 chars): {str(item_dict)[:200]}")
                     except Exception as item_err:
                           logger.warning(f"Error processing item for {component_key}: {item_err}. Item: {str(item_dict)[:200]}")
                 else:
                      logger.warning(f"LLM returned non-dict item in list for {component_key}: {type(item_dict)}")

            logger.info(f"Successfully validated and processed {len(results_list)} items for {component_key}")
            return (component_key, results_list)

        except Exception as e:
            # Catch unexpected errors during the process for this component
            logger.error(f"Unexpected error extracting {component_key}: {str(e)}", exc_info=True)
            # Indicate failure for this component, but don't stop overall process
            return (component_key, None) # Returning None signals an extraction *error* for this component

    # --- extract_component remains the same (potentially deprecated by _extract_single_component) ---
    async def extract_component(self, component_name: str, extracted_text: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        prompt = self.prompt_manager.get_prompt(component_name, extracted_text)
        logger.info(f"Extracting {component_name} using LLM.")
        try:
            extraction_result = await self.llm_client.extract_json(prompt)
            if extraction_result:
                logger.debug(f"{component_name} extraction result: {extraction_result}")
                return extraction_result
            else:
                logger.warning(f"LLM extraction for {component_name} returned no data.")
                return None
        except Exception as e:
            logger.error(f"Error extracting {component_name}: {str(e)}", exc_info=True)
            return None

    # --- extract_all_components remains the same (potentially deprecated by process_pdf loop) ---
    async def extract_all_components(self, extracted_text: Dict[str, Any]) -> Dict[str, Any]:
        extracted_components = {}
        tasks = []
        for component_name in self.extract_components:
            tasks.append(self.extract_component(component_name, extracted_text))
        results = await asyncio.gather(*tasks)
        for component_name, component_result in zip(self.extract_components, results):
            if component_result:
                extracted_components[component_name] = component_result
        return extracted_components

    # --- _add_relationships remains the same ---
    async def _add_relationships(self, extracted_data_by_slug: Dict[str, List[Dict]]) -> None:
        """
        Add relationships between extracted entities based on simplified logic.
        Modifies the extracted_data_by_slug dictionary in place.
        Assumes entities in lists are dicts with an 'id' field (internal UUID).
        """
        logger.debug("Attempting to add simplified relationships between extracted entities...")

        # Helper to get slug safely using component key
        def get_slug(key):
            slug = self.params.get('strapi', {}).get('api_slugs', {}).get(key)
            if not slug: logger.warning(f"Slug for '{key}' not found in config for relationship linking.")
            return slug

        try:
            # Get slugs needed for linking
            problem_slug = get_slug("research_problem")
            gap_slug = get_slug("knowledge_gap")
            question_slug = get_slug("research_question")
            framework_slug = get_slug("methodological_framework")
            sci_challenge_slug = get_slug("scientific_challenge")
            method_challenge_slug = get_slug("methodological_challenge")
            impl_challenge_slug = get_slug("implementation_challenge")
            limitation_slug = get_slug("limitation")
            future_dir_slug = get_slug("future_direction")
            potential_app_slug = get_slug("potential_application")
            material_tool_slug = get_slug("material_tool")


            # Get lists of entities using the slugs, default to empty list
            problems = extracted_data_by_slug.get(problem_slug, [])
            gaps = extracted_data_by_slug.get(gap_slug, [])
            questions = extracted_data_by_slug.get(question_slug, [])
            frameworks = extracted_data_by_slug.get(framework_slug, [])
            sci_challenges = extracted_data_by_slug.get(sci_challenge_slug, [])
            method_challenges = extracted_data_by_slug.get(method_challenge_slug, [])
            impl_challenges = extracted_data_by_slug.get(impl_challenge_slug, [])
            limitations = extracted_data_by_slug.get(limitation_slug, [])
            future_dirs = extracted_data_by_slug.get(future_dir_slug, [])
            potential_apps = extracted_data_by_slug.get(potential_app_slug, [])
            material_tools = extracted_data_by_slug.get(material_tool_slug, [])

            # Get the internal ID of the first found entity of each type (simplified logic)
            first_problem_id = problems[0].get("id") if problems else None
            first_framework_id = frameworks[0].get("id") if frameworks else None
            first_gap_id = gaps[0].get("id") if gaps else None
            first_limitation_id = limitations[0].get("id") if limitations else None
            first_potential_app_id = potential_apps[0].get("id") if potential_apps else None
            first_sci_challenge_id = sci_challenges[0].get("id") if sci_challenges else None
            all_framework_ids = [f.get("id") for f in frameworks if f.get("id")]
            all_material_tool_ids = [mt.get("id") for mt in material_tools if mt.get("id")]


            # --- Apply Links (Check if target ID exists before linking) ---
            if first_problem_id:
                for gap in gaps: gap["relatedProblem"] = first_problem_id
                for q in questions: q["relatedProblem"] = first_problem_id
                for fw in frameworks: fw["researchProblem"] = first_problem_id
                for sc in sci_challenges: sc["relatedProblem"] = first_problem_id

            if first_gap_id:
                for q in questions: q["addressesGap"] = first_gap_id
                for fd in future_dirs: fd["addressesGap"] = first_gap_id

            if first_framework_id:
                for mc in method_challenges: mc["encounteredInFramework"] = first_framework_id
                for ic in impl_challenges: ic["encounteredInFramework"] = first_framework_id
                for lim in limitations: lim["limitedFramework"] = first_framework_id
                # Link Materials/Tools used in the first framework (example)
                for mt in material_tools:
                     if "usedInFrameworks" not in mt: mt["usedInFrameworks"] = []
                     # Avoid duplicates if run multiple times (though shouldn't happen in normal flow)
                     if first_framework_id not in mt["usedInFrameworks"]:
                         mt["usedInFrameworks"].append(first_framework_id)

            if first_limitation_id:
                 for mc in method_challenges: mc["resultsInLimitation"] = first_limitation_id
                 for fd in future_dirs: fd["arisesFromLimitation"] = first_limitation_id

            if first_potential_app_id:
                 for ic in impl_challenges: ic["relatedApplication"] = first_potential_app_id
                 for fd in future_dirs: fd["extendsPotentialApplication"] = first_potential_app_id

            if first_sci_challenge_id:
                 for mc in method_challenges: mc["relatedScientificChallenge"] = first_sci_challenge_id

            # Link Potential Applications to all frameworks (example of multi-link)
            if all_framework_ids:
                for pa in potential_apps:
                     pa["buildOnMethodologicalFrameworks"] = all_framework_ids

            logger.debug("Finished adding simplified relationships.")

        except Exception as e:
            logger.error(f"Error adding relationships: {e}", exc_info=True)


    # --- MODIFIED _save_and_upload_result SIGNATURE and LOGIC ---
    async def _save_and_upload_result(self, result_data_by_slug: Dict[str, List[Dict]], pdf_path: Union[str, Path], output_json_path: Union[str, Path]) -> None:
        """
        Save extraction result locally to the specified path and upload to Strapi if configured.

        Args:
            result_data_by_slug: The extracted data keyed by Strapi slugs.
            pdf_path: The original path of the PDF (used for logging).
            output_json_path: The exact path where the JSON file should be saved.
        """
        # Ensure paths are Path objects
        pdf_path = Path(pdf_path)
        output_path = Path(output_json_path)
        pdf_display_name = pdf_path.name # For logging

        try:
            # Prepare data for Strapi upload format (removes internal 'id', formats relations)
            data_to_process = self._prepare_data_for_strapi_upload(result_data_by_slug)

            # --- Create Output Directory ---
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured output directory exists: {output_path.parent}")
            except OSError as e:
                 logger.error(f"Failed to create output directory {output_path.parent} for {pdf_display_name}: {e}")
                 raise # Re-raise directory creation error

            # Save locally using aiofiles
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as afp:
                await afp.write(json.dumps(data_to_process, indent=2, ensure_ascii=False))
            logger.info(f"Saved extraction result locally to {output_path}") # Use the exact output path

            # Upload to Strapi if client is initialized
            if self.strapi_client:
                logger.info(f"Attempting direct upload to Strapi for {pdf_display_name}...")
                try:
                    upload_summary = await self.strapi_client.upload_data(data_to_process)
                    # StrapiClient should log its own summary
                except Exception as e:
                    logger.error(f"Strapi upload failed for {pdf_display_name}: {str(e)}", exc_info=True)

        except Exception as e:
            logger.error(f"Failed to save or upload extraction result for {pdf_display_name}: {str(e)}", exc_info=True)


    # --- _prepare_data_for_strapi_upload remains the same ---
    def _prepare_data_for_strapi_upload(self, result_data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Formats the final extracted data (keyed by Strapi slug) for Strapi upload.
        - Removes the internal 'id' field.
        - Ensures relationship fields contain only the target internal UUIDs.
        - Adds a temporary 'internal_id' field for the StrapiClient to map Strapi IDs.
        - Handles nested components recursively.
        """
        prepared_upload_data = {}
        for strapi_slug, entity_list in result_data.items():
            prepared_list = []
            if isinstance(entity_list, list):
                for entity in entity_list:
                    if isinstance(entity, dict):
                         # Process entity recursively to format relations and add internal_id
                         formatted_entity = self._format_entity_for_upload(entity)
                         prepared_list.append(formatted_entity)
                    else:
                         logger.warning(f"Skipping non-dict item in list for slug '{strapi_slug}'")

            prepared_upload_data[strapi_slug] = prepared_list
        return prepared_upload_data

    # --- _format_entity_for_upload remains the same ---
    def _format_entity_for_upload(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively formats a single entity and its nested components for Strapi upload.
        Adds 'internal_id' and removes 'id'. Formats relation fields.
        """
        formatted_payload = {}
        internal_id = entity_data.get("id") # Get the internal UUID

        if internal_id:
            formatted_payload["internal_id"] = internal_id # Add for mapping by StrapiClient

        # Define relationship fields based on SKEO schema knowledge
        # These fields should contain UUIDs (or lists of UUIDs) referring to other *top-level* entities
        single_relation_fields = {
            "paper", "relatedProblem", "addressesGap", "relatedApplication",
            "relatedScientificChallenge", "encounteredInFramework",
            "limitedFramework", "resultsInLimitation", "researchProblem",
             "arisesFromLimitation", "extendsPotentialApplication", # From FutureDirection
        }
        multi_relation_fields = {
            "materialsAndTools", "buildOnMethodologicalFrameworks", "usedInFrameworks",
            "usedInExecutions" # From MaterialTool (adjust based on actual usage)
        }
        # Fields containing lists of *component* objects (not simple relations)
        component_list_fields = {
             "authors", "fundingSources", "institutions", # In ResearchContext, Paper
             "underlyingTheories", "guidingModels", # In TheoreticalBasis
             "relatedVariables", # In ResearchQuestion
             "variables", "procedures", # In MethodologicalFramework
             "validationTypes", # In ValidationVerification (list of strings, not relations)
             "steps", # In Procedure
        }
        # Fields containing single *component* objects
        single_component_fields = {
            "studyDesign", "populationAndSampling", "dataCollection", "dataAnalysis",
            "resultsRepresentation", "validationAndVerification", "ethicalConsiderations",
            "reproducibilityAndSharing" # In MethodologicalFramework
        }


        for field_name, field_value in entity_data.items():
            # Skip the original internal 'id' field
            if field_name == "id":
                 continue

            if field_name in single_relation_fields:
                # Keep only the string UUID for single relations
                if isinstance(field_value, str) and len(field_value) == 32:
                    formatted_payload[field_name] = field_value
            elif field_name in multi_relation_fields:
                 # Keep only the list of string UUIDs for multi-relations
                 if isinstance(field_value, list):
                      ids = [item for item in field_value if isinstance(item, str) and len(item) == 32]
                      if ids: formatted_payload[field_name] = ids
            elif field_name in component_list_fields:
                 # Recursively format components within lists
                 if isinstance(field_value, list):
                      formatted_payload[field_name] = [
                          self._format_entity_for_upload(item) if isinstance(item, dict) else item
                          for item in field_value
                          if item is not None # Filter out potential None values in lists
                      ]
            elif field_name in single_component_fields:
                 # Recursively format single nested component
                 if isinstance(field_value, dict):
                      formatted_payload[field_name] = self._format_entity_for_upload(field_value)
            else:
                # Copy other primitive fields or lists of primitives directly
                formatted_payload[field_name] = field_value

        return formatted_payload