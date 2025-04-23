# pdf_processor.py - Processes PDF files for text and metadata extraction

import os
import re
import logging
import asyncio
import fitz  # PyMuPDF
from typing import Dict, List, Any, Optional

# Use conditional import for Docling to avoid hard dependency if not used
try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
    DOCLING_AVAILABLE = True
except ImportError:
    DocumentConverter = None
    PdfFormatOption = None
    InputFormat = None
    PdfPipelineOptions = None
    TableFormerMode = None
    DOCLING_AVAILABLE = False

# Use conditional import for language detection
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    detect = None
    LangDetectException = None
    LANGDETECT_AVAILABLE = False

# Import necessary components (adjust path based on your structure)
try:
    from llm_client import LLMClient
    from metadata_fetcher import SerpApiMetadataFetcher
except ImportError as e:
     print(f"ERROR in pdf_processor.py: Could not import sibling modules ({e}). Ensure all .py files are in the same directory and the script is run from that directory.", file=sys.stderr)
     raise

logger = logging.getLogger('skeo.pdf')

class PDFProcessor:
    """Process PDF files to extract text and metadata"""

    def __init__(self, llm_client: LLMClient, metadata_fetcher: Optional[SerpApiMetadataFetcher] = None, params: Optional[Dict] = None):
        """
        Initialize PDF processor

        Args:
            llm_client: LLM client for text processing.
            metadata_fetcher: SerpApi metadata fetcher for paper metadata.
            params: Parameters dict containing 'pdf' and 'metadata' sections.
        """
        self.llm_client = llm_client
        self.metadata_fetcher = metadata_fetcher
        self.params = params if params else {}

        pdf_params = self.params.get('pdf', {})
        self.extract_method = pdf_params.get("extract_method", "docling" if DOCLING_AVAILABLE else "pymupdf")
        self.search_metadata = pdf_params.get("search_metadata", bool(self.metadata_fetcher and self.metadata_fetcher.enabled))
        self.max_text_length = pdf_params.get("max_text_length", 150000)
        self.language_detection = pdf_params.get("language_detection", True) and LANGDETECT_AVAILABLE
        self.docling_options_config = pdf_params.get("docling_options", {})

        if self.extract_method == "docling" and not DOCLING_AVAILABLE:
            logger.warning("Docling extract method configured but Docling library not found. Falling back to PyMuPDF.")
            self.extract_method = "pymupdf"
        if self.language_detection and not LANGDETECT_AVAILABLE:
            logger.warning("Language detection enabled but langdetect library not found. Disabling detection.")
            self.language_detection = False

        logger.info(f"PDFProcessor initialized with extraction method: {self.extract_method}")


    async def extract_text_from_pdf(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured text and metadata from a PDF file.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            Dict containing 'metadata', 'full_text', 'sections', 'language', or None if extraction fails.
        """
        logger.info(f"Processing PDF: {pdf_path}")
        doc = None # PyMuPDF doc object
        try:
            # --- Basic Metadata Extraction (PyMuPDF for initial info) ---
            try:
                 doc = fitz.open(pdf_path)
                 pdf_metadata_raw = doc.metadata or {}
                 basic_metadata = {
                    "title": pdf_metadata_raw.get("title", ""),
                    "authors_str": pdf_metadata_raw.get("author", ""),
                    "subject": pdf_metadata_raw.get("subject", ""),
                    "keywords_str": pdf_metadata_raw.get("keywords", ""),
                    "doi": ""
                 }
                 cleaned_authors = [a.strip() for a in basic_metadata["authors_str"].split(',') if a.strip()]
                 first_author_for_search = cleaned_authors[0] if cleaned_authors else None
                 title_for_search = basic_metadata["title"]

                 # If PyMuPDF title is empty, try to guess from filename
                 if not title_for_search:
                      title_for_search = os.path.splitext(os.path.basename(pdf_path))[0].replace('_', ' ')
                      logger.info(f"Using filename as initial title guess: {title_for_search}")


            except Exception as fitz_err:
                 logger.error(f"Error opening PDF or reading basic metadata with PyMuPDF for {pdf_path}: {fitz_err}")
                 # If we can't even open the PDF, we can't proceed
                 return None

            # --- Online Metadata Fetching (SerpApi) ---
            online_metadata = None
            if self.search_metadata and title_for_search and self.metadata_fetcher:
                online_metadata = await self.metadata_fetcher.search_scholar_metadata(
                    title_for_search,
                    first_author_for_search
                )

            # --- Consolidate Metadata ---
            # Prioritize online metadata, fallback to PDF metadata.
            final_metadata = {
                "title": (online_metadata or {}).get("title") or basic_metadata["title"] or title_for_search, # Use guess if still empty
                "authors": (online_metadata or {}).get("authors", []), # Assumes fetcher returns list of dicts
                "doi": (online_metadata or {}).get("doi") or basic_metadata["doi"],
                "journal": (online_metadata or {}).get("journal", ""),
                "publicationDate": (online_metadata or {}).get("publicationDate") or (online_metadata or {}).get("year"),
                "year": (online_metadata or {}).get("year", ""),
                "volume": (online_metadata or {}).get("volume", ""),
                "issue": (online_metadata or {}).get("issue", ""),
                "pages": (online_metadata or {}).get("pages", ""),
                "keywords": (online_metadata or {}).get("keywords", []),
                "abstract": (online_metadata or {}).get("abstract", ""), # Pre-fill abstract if found
                "fileUrl": (online_metadata or {}).get("fileUrl", ""), # Link from SerpApi
                "pdfPath": (online_metadata or {}).get("pdfPath") # Direct PDF link from SerpApi resource if found
            }

            # If authors weren't found online, parse from PDF metadata string
            if not final_metadata["authors"] and basic_metadata["authors_str"]:
                 final_metadata["authors"] = [{"name": name} for name in cleaned_authors]

            # Parse keywords from PDF metadata string if not found online
            if not final_metadata["keywords"] and basic_metadata["keywords_str"]:
                final_metadata["keywords"] = [kw.strip() for kw in re.split(r'[;,]', basic_metadata["keywords_str"]) if kw.strip()]

            # Try to extract year from publication date if not found online/parsed
            if not final_metadata["year"] and final_metadata["publicationDate"]:
                 year_match = re.search(r'\b(19|20)\d{2}\b', str(final_metadata["publicationDate"]))
                 if year_match:
                     final_metadata["year"] = year_match.group(0)


            # --- Text & Section Extraction ---
            extraction_result = None
            if self.extract_method == "docling":
                extraction_result = await self._extract_with_docling(pdf_path, final_metadata)
            else: # Default or "pymupdf"
                # Pass the already opened fitz document
                extraction_result = await self._extract_with_pymupdf(doc, final_metadata)

            # If extraction failed, return None
            if extraction_result is None:
                return None

            # --- Final Metadata Refinement from extracted text ---
            final_metadata = await self._refine_metadata_from_text(
                extraction_result["metadata"], extraction_result["full_text"]
            )
            extraction_result["metadata"] = final_metadata # Update metadata in the result dict

            # --- Logging Final Checks ---
            if not final_metadata.get("doi"): logger.info(f"DOI could not be finalized for {pdf_path}")
            if not final_metadata.get("year"): logger.info(f"Year could not be finalized for {pdf_path}")
            if not final_metadata.get("title"): logger.error(f"Title could not be finalized for {pdf_path}")

            return extraction_result

        except Exception as e:
            logger.error(f"General error processing PDF {pdf_path}: {str(e)}", exc_info=True)
            return None # Indicate failure
        finally:
            if doc:
                try: doc.close()
                except Exception as close_err: logger.warning(f"Error closing PDF {pdf_path}: {close_err}")

    async def _extract_with_docling(self, pdf_path: str, initial_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract text using Docling's DocumentConverter."""
        if not DOCLING_AVAILABLE: return None
        logger.info(f"Extracting text using Docling for {pdf_path}")
        metadata = initial_metadata.copy()
        try:
            # Configure Docling pipeline options from params
            pipeline_opts = PdfPipelineOptions(
                artifacts_path=self.docling_options_config.get("artifacts_path"),
                enable_remote_services=self.docling_options_config.get("enable_remote_services", False),
                do_code_enrichment=self.docling_options_config.get("do_code_enrichment", False),
                do_formula_enrichment=self.docling_options_config.get("do_formula_enrichment", False),
                do_picture_classification=self.docling_options_config.get("do_picture_classification", False),
                do_picture_description=self.docling_options_config.get("do_picture_description", False),
                generate_picture_images=self.docling_options_config.get("generate_picture_images", False),
                images_scale=self.docling_options_config.get("images_scale", 2),
                do_table_structure=self.docling_options_config.get("do_table_structure", True),
            )
            # Set TableFormer mode
            tf_mode_str = self.docling_options_config.get("table_structure_mode", "ACCURATE").upper()
            pipeline_opts.table_structure_options.mode = TableFormerMode.FAST if tf_mode_str == "FAST" else TableFormerMode.ACCURATE
            pipeline_opts.table_structure_options.do_cell_matching = self.docling_options_config.get("table_do_cell_matching", True)


            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts)
                }
            )

            # Get limits from config
            max_pages = self.docling_options_config.get("max_num_pages")
            max_size = self.docling_options_config.get("max_file_size")

            # Prepare kwargs for the convert call, only including limits if they are integers
            convert_kwargs = {}
            if isinstance(max_pages, int):
                convert_kwargs['max_num_pages'] = max_pages
            elif max_pages is not None:
                 logger.warning(f"Invalid value '{max_pages}' for docling_options.max_num_pages in config, expected integer. Ignoring limit.")

            if isinstance(max_size, int):
                convert_kwargs['max_file_size'] = max_size
            elif max_size is not None:
                 logger.warning(f"Invalid value '{max_size}' for docling_options.max_file_size in config, expected integer. Ignoring limit.")

            logger.debug(f"Calling Docling convert with kwargs: {convert_kwargs}")

            # Convert the document
            # Run conversion in a separate thread managed by asyncio to avoid blocking
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, # Use default executor
                lambda: converter.convert(pdf_path, **convert_kwargs)
            )

            if not result or not result.document:
                 logger.error(f"Docling conversion failed for {pdf_path}")
                 return None

            # Export to Markdown for section parsing
            markdown_text = result.document.export_to_markdown()
            # Or export to plain text: full_text = result.document.export_to_text()

            language = await self._detect_language(markdown_text)
            sections = await self._parse_sections_from_markdown(markdown_text)

            # Pre-fill abstract if not found via metadata search
            if not metadata.get("abstract") and sections.get("abstract"):
                 metadata["abstract"] = sections["abstract"][:1000] # Limit length

            # Infer missing sections with LLM if needed
            if not all(sections.get(s) for s in ["introduction", "methodology", "results", "discussion"]):
                 logger.info("Attempting LLM section inference based on Docling Markdown.")
                 await self._infer_sections_with_llm(markdown_text, sections)

            # Ensure required sections exist
            required_sections = ["abstract", "introduction", "methodology", "results", "discussion", "conclusion", "references"]
            for section in required_sections: sections.setdefault(section, "")

            return {
                "metadata": metadata, # Metadata refined later from text
                "full_text": markdown_text[:self.max_text_length],
                "sections": sections,
                "language": language
            }

        except Exception as e:
            logger.error(f"Error during Docling processing for {pdf_path}: {str(e)}", exc_info=True)
            return None # Indicate failure

    async def _extract_with_pymupdf(self, doc: fitz.Document, initial_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract text using PyMuPDF (simpler layout analysis)."""
        logger.info(f"Extracting text using PyMuPDF for {doc.name}")
        metadata = initial_metadata.copy()
        full_text = ""
        sections = {
            "abstract": metadata.get("abstract", ""), # Use pre-filled if available
            "introduction": "", "methodology": "", "results": "",
            "discussion": "", "conclusion": "", "references": ""
        }
        try:
            for page_num, page in enumerate(doc):
                try:
                    full_text += page.get_text("text") + "\n" # Basic text extraction
                except Exception as page_err:
                     logger.warning(f"Error extracting text from page {page_num+1} of {doc.name}: {page_err}")
                     full_text += "[Content Extraction Error]\n"

            if not full_text:
                logger.error(f"PyMuPDF extracted no text from {doc.name}")
                return None

            language = await self._detect_language(full_text)

            # Attempt LLM section inference as PyMuPDF gives unstructured text
            logger.info("Attempting LLM section inference based on PyMuPDF full text.")
            await self._infer_sections_with_llm(full_text, sections)

            # Ensure required sections exist
            for section in sections.keys(): sections.setdefault(section, "")

            # Ensure abstract is populated if possible
            if not sections["abstract"] and metadata.get("abstract"):
                 sections["abstract"] = metadata["abstract"]


            return {
                "metadata": metadata, # Metadata refined later from text
                "full_text": full_text[:self.max_text_length],
                "sections": sections,
                "language": language
            }
        except Exception as e:
             logger.error(f"Error during PyMuPDF processing for {doc.name}: {str(e)}", exc_info=True)
             return None # Indicate failure

    async def _detect_language(self, text: str) -> Optional[str]:
        """Detect language from text snippet."""
        if not self.language_detection or not text: return None
        try:
            snippet = text[:min(len(text), 2000)]
            language = detect(snippet)
            logger.info(f"Detected language: {language}")
            return language
        except LangDetectException:
            logger.warning("Language detection failed for document.")
            return None
        except Exception as e:
             logger.warning(f"Error during language detection: {e}")
             return None

    async def _refine_metadata_from_text(self, metadata: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Try to extract missing metadata fields from the text."""
        if not text: return metadata

        text_snippet = text[:min(len(text), 5000)] # Check beginning of text

        # Extract DOI if missing
        if not metadata.get("doi"):
            doi_match = re.search(r'\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b', text_snippet, re.IGNORECASE)
            if doi_match:
                metadata["doi"] = doi_match.group(1).strip().rstrip('.')
                logger.info(f"Refined DOI from text: {metadata['doi']}")

        # Extract Year if missing
        if not metadata.get("year"):
             year_context_match = re.search(r'(?:published|received|accepted|©|\copyright|\()\s*((?:19|20)\d{2})\b', text_snippet, re.IGNORECASE)
             if year_context_match:
                  metadata["year"] = year_context_match.group(1)
                  logger.info(f"Refined Year from text context: {metadata['year']}")
             else: # Fallback: Find standalone year near top
                year_match = re.search(r'\b((?:19|20)\d{2})\b', text_snippet[:1000])
                if year_match:
                    metadata["year"] = year_match.group(1)
                    logger.info(f"Refined Year (standalone) from text: {metadata['year']}")

        # Extract Journal/Volume/Issue/Pages if potentially missing (simple regex)
        # This is less reliable and can be improved with LLM extraction if needed.
        if not metadata.get("journal") or not metadata.get("volume"):
            pub_match = re.search(
                r'([A-Za-z\s&]{5,})' # Journal Name (at least 5 chars)
                r'(?:[,\.]|\s+)' # Separator
                r'(?:Vol\.?|Volume)?\s*(\d+)' # Volume (required for this match)
                r'(?:(?:,\s*|\s+)\(?No\.?|Issue\)?\s*(\d+|\w+))?' # Optional Issue
                r'(?:(?:,\s*|\s+)\(?(?:(?:pp|pages)\.?\s*)?([\d\-–]+)\)?)?' # Optional Pages
                r'(?:(?:,\s*|\s+)\(?((?:19|20)\d{2})\)?)?' # Optional Year
                , text_snippet, re.IGNORECASE | re.MULTILINE)

            if pub_match:
                if not metadata.get("journal"): metadata["journal"] = pub_match.group(1).strip()
                if not metadata.get("volume"): metadata["volume"] = pub_match.group(2).strip()
                if pub_match.group(3) and not metadata.get("issue"): metadata["issue"] = pub_match.group(3).strip()
                if pub_match.group(4) and not metadata.get("pages"): metadata["pages"] = pub_match.group(4).strip()
                if pub_match.group(5) and not metadata.get("year"): metadata["year"] = pub_match.group(5).strip()
                logger.info(f"Attempted refinement of Pub Info from text: J='{metadata.get('journal')}', V='{metadata.get('volume')}'...")

        # Update publication date if only year is present
        if metadata.get("year") and not metadata.get("publicationDate"):
             metadata["publicationDate"] = metadata["year"]

        return metadata

    async def _parse_sections_from_markdown(self, markdown_text: str) -> Dict[str, str]:
        """Parse standard sections from markdown text based on headers."""
        sections = {}
        current_section_name = None
        current_content = []

        # Patterns adjusted for common variations
        section_patterns = {
            "abstract": r'^#+\s*(?:abstract|summary)\s*$',
            "introduction": r'^#+\s*(?:\d{1,2}(?:\.\d{1,2})*\.?\s*)?(?:introduction|background)\s*$',
            "related_work": r'^#+\s*(?:\d{1,2}(?:\.\d{1,2})*\.?\s*)?(?:related\s+work|literature\s+review)\s*$',
            "methodology": r'^#+\s*(?:\d{1,2}(?:\.\d{1,2})*\.?\s*)?(?:method(?:s|ology)?|materials\s+(?:and\s+)?methods|experimental(?:\s+design|\s+setup)?|proposed\s+method|approach|study\s+design)\s*$',
            "results": r'^#+\s*(?:\d{1,2}(?:\.\d{1,2})*\.?\s*)?(?:results|findings|evaluation|experiments(?:\s+and\s+results)?)\s*$',
            "discussion": r'^#+\s*(?:\d{1,2}(?:\.\d{1,2})*\.?\s*)?(?:discussion)\s*$',
            "conclusion": r'^#+\s*(?:\d{1,2}(?:\.\d{1,2})*\.?\s*)?(?:conclusion(?:s)?|summary(?: and Future Work)?)\s*$',
            "references": r'^#+\s*(?:references|bibliography|literature\s+cited)\s*$',
            "acknowledgements": r'^#+\s*(?:acknowledgements?|acknowledgments?)\s*$',
            "appendix": r'^#+\s*(?:appendix|appendices|supplementary\s+(?:material|information))\s*$',
        }
        # Map found keys to standard keys
        key_map = {
            "related_work": "methodology", # Often part of methodology/intro context
            "acknowledgements": "conclusion", # Context often near conclusion
            "appendix": "references" # Context often after references
        }

        lines = markdown_text.splitlines()
        for line in lines:
            matched_section_key = None
            line_stripped = line.strip()

            if line_stripped.startswith('#'):
                for section_key, pattern in section_patterns.items():
                    if re.match(pattern, line_stripped, re.IGNORECASE):
                        matched_section_key = section_key
                        break

            if matched_section_key:
                standard_key = key_map.get(matched_section_key, matched_section_key)
                # Save previous section's content under its standard key
                if current_section_name:
                    sections[current_section_name] = "\n".join(current_content).strip()

                # Start new section (using standard key)
                current_section_name = standard_key
                current_content = []
            elif current_section_name:
                current_content.append(line)

        # Save the last section
        if current_section_name:
            sections[current_section_name] = "\n".join(current_content).strip()

        logger.info(f"Sections identified via Markdown headers: {list(sections.keys())}")
        return sections

    async def _infer_sections_with_llm(self, text: str, sections: Dict[str, str]) -> None:
        """Use LLM to infer missing sections or improve section detection."""
        target_sections = ["abstract", "introduction", "methodology", "results", "discussion", "conclusion"]
        sections_to_infer = [s for s in target_sections if len(sections.get(s, '')) < 100]

        if not sections_to_infer or not text:
            logger.debug("Skipping LLM section inference (no missing sections or no text).")
            return

        logger.info(f"Attempting LLM inference for sections: {sections_to_infer}")
        try:
            # Limit text sent to LLM
            text_limit = 25000 # Adjust token limit as needed
            if len(text) > text_limit:
                 text_snippet = text[:text_limit // 2] + "\n...\n" + text[-text_limit // 2:]
            else:
                 text_snippet = text

            section_prompt = f"""
Analyze the following scientific paper text and extract the content for ONLY the following sections: {', '.join(sections_to_infer)}.
If a section listed above is clearly not present in the text, provide an empty string "" for its value.
Focus on capturing the core content for each requested section accurately and completely.

Paper Text (potentially truncated):
{text_snippet}

Respond ONLY with a valid JSON object where the keys are the section names ({', '.join(sections_to_infer)}) and the values are the extracted text strings for each section.
Example for missing 'results': {{"introduction": "...", "results": ""}}
"""
            llm_extracted_sections = await self.llm_client.extract_json(section_prompt)

            if isinstance(llm_extracted_sections, dict):
                for section_name, llm_content in llm_extracted_sections.items():
                    normalized_name = section_name.lower().strip()
                    if normalized_name in sections_to_infer and isinstance(llm_content, str):
                        # Update if LLM found substantially more content or if section was empty
                        if len(llm_content) > len(sections.get(normalized_name, '')) + 50:
                            sections[normalized_name] = llm_content.strip()
                            logger.info(f"Section '{normalized_name}' updated/populated by LLM.")

        except Exception as e:
            logger.warning(f"Error using LLM for section inference: {str(e)}")