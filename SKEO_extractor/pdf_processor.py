# pdf_processor.py - Processes PDF files for text and metadata extraction

import os
import re
import logging
import asyncio
import pymupdf as fitz  # PyMuPDF
from typing import Dict, List, Any, Optional, Tuple # Added Tuple
import sys

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
        doc = None  # PyMuPDF doc object
        first_page_markdown_for_validation = None # Store markdown from title extraction run
        title_for_search = None
        try:
            # --- Open the PDF Document with PyMuPDF (still needed for fallback/metadata) ---
            try:
                doc = fitz.open(pdf_path)
            except Exception as fitz_err:
                logger.error(f"Error opening PDF with PyMuPDF for {pdf_path}: {fitz_err}")
                return None

            # --- Basic Metadata Extraction (PyMuPDF for initial info) ---
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

            # --- Attempt Title Extraction ---

            # 1. Try extracting with Docling Header Method first (as it also gives markdown for validation)
            #    We run this even if PyMuPDF metadata exists, to get the markdown text for validation.
            docling_title_candidate = None
            if DOCLING_AVAILABLE:
                # This now returns (title_candidate, first_page_markdown) or (None, None)
                docling_title_candidate, first_page_markdown_for_validation = await self._extract_title_with_docling(pdf_path)
                if docling_title_candidate:
                    logger.info(f"Docling extracted title candidate: {docling_title_candidate}")
                    # Validate using the markdown text *from the same Docling run*
                    if await self._is_title_in_text(title=docling_title_candidate, markdown_text=first_page_markdown_for_validation):
                        title_for_search = docling_title_candidate
                        logger.info(f"Title confirmed from Docling header: {title_for_search}")
                    else:
                        logger.warning("Title extracted from Docling header NOT found in its generated markdown text. Discarding Docling title.")
                else:
                    logger.info("No title header extracted using Docling.")

            # 2. If Docling didn't find a valid title, try PyMuPDF metadata
            if not title_for_search and basic_metadata["title"]:
                extracted_title_meta = basic_metadata["title"].strip()
                logger.info(f"Trying title from PyMuPDF metadata: {extracted_title_meta}")
                # Validate using Docling's markdown if available, otherwise fallback to PyMuPDF text
                if await self._is_title_in_text(title=extracted_title_meta, doc=doc, markdown_text=first_page_markdown_for_validation):
                    title_for_search = extracted_title_meta
                    logger.info(f"Title confirmed from PyMuPDF metadata: {title_for_search}")
                else:
                    logger.warning("Title from PyMuPDF metadata not found in document text (checked Docling markdown first, then PyMuPDF). Discarding metadata title.")
            elif not title_for_search:
                 logger.info("No title found in PyMuPDF metadata or Docling failed/discarded.")


            # 3. If title still not found, try guessing from filename (validate against PyMuPDF text as fallback)
            if not title_for_search:
                filename_title = os.path.splitext(os.path.basename(pdf_path))[0].replace('_', ' ')
                logger.info(f"Trying title guessed from filename: {filename_title}")
                # Use PyMuPDF doc for validation as the last resort if Docling failed
                if await self._is_title_in_text(title=filename_title, doc=doc):
                    title_for_search = filename_title
                    logger.info(f"Title confirmed from filename guess: {title_for_search}")
                else:
                    logger.warning("Title guessed from filename not found in PyMuPDF document text. Discarding.")

            # --- Final Title Check ---
            if not title_for_search:
                logger.error("Title could not be reliably extracted and validated from any method.")
                title_for_search = None  # Explicitly set to None


            # --- Use extracted title and author for further processing ---
            basic_metadata["title"] = title_for_search # Store the final title

            # --- Metadata Search (SerpApi) ---
            online_metadata = None
            # Only search if we found a title
            if self.search_metadata and title_for_search and self.metadata_fetcher:
                online_metadata = await self.metadata_fetcher.search_scholar_metadata(
                    title_for_search,
                    first_author_for_search
                )

            # --- Consolidate Metadata ---
            if title_for_search:
                # Prioritize online metadata, fallback to basic metadata (which now holds the validated title)
                final_metadata = {
                    "title": (online_metadata or {}).get("title") or basic_metadata["title"],
                    "authors": (online_metadata or {}).get("authors", []),
                    "doi": (online_metadata or {}).get("doi") or basic_metadata["doi"],
                    "journal": (online_metadata or {}).get("journal", ""),
                    "publicationDate": (online_metadata or {}).get("publicationDate") or (online_metadata or {}).get("year"),
                    "year": (online_metadata or {}).get("year", ""),
                    "volume": (online_metadata or {}).get("volume", ""),
                    "issue": (online_metadata or {}).get("issue", ""),
                    "pages": (online_metadata or {}).get("pages", ""),
                    "keywords": (online_metadata or {}).get("keywords", []),
                    "abstract": (online_metadata or {}).get("abstract", ""),
                    "fileUrl": (online_metadata or {}).get("fileUrl", ""),
                    "pdfPath": (online_metadata or {}).get("pdfPath")
                }
            else:
                # Use "manual input needed" values if title couldn't be found/validated
                final_metadata = {
                    "title": "Manual input needed",
                    "authors": [], "doi": "", "journal": "", "publicationDate": "", "year": "",
                    "volume": "", "issue": "", "pages": "", "keywords": [], "abstract": "",
                    "fileUrl": "", "pdfPath": ""
                }

            # Fill missing fields from basic_metadata if needed
            if not final_metadata["authors"] and basic_metadata["authors_str"]:
                final_metadata["authors"] = [{"name": name} for name in cleaned_authors]
            if not final_metadata["keywords"] and basic_metadata["keywords_str"]:
                final_metadata["keywords"] = [kw.strip() for kw in re.split(r'[;,]', basic_metadata["keywords_str"]) if kw.strip()]

            # --- Text & Section Extraction ---
            extraction_result = None
            if self.extract_method == "docling":
                extraction_result = await self._extract_with_docling(pdf_path, final_metadata)
            # Ensure we always have a PyMuPDF doc object for the pymupdf method
            elif doc:
                extraction_result = await self._extract_with_pymupdf(doc, final_metadata)
            else:
                # This case should theoretically not be reached due to earlier checks
                logger.error(f"Cannot extract with PyMuPDF as document object is missing for {pdf_path}")
                return None


            if extraction_result is None:
                logger.error(f"Text extraction failed for {pdf_path} using method '{self.extract_method}'")
                return None

            # --- Final Metadata Refinement from extracted text ---
            # Use the text extracted by the chosen method (Docling markdown or PyMuPDF plain text)
            final_metadata = await self._refine_metadata_from_text(
                extraction_result["metadata"], extraction_result["full_text"]
            )
            extraction_result["metadata"] = final_metadata  # Update metadata

            # --- Logging Final Checks ---
            if not final_metadata.get("doi"):
                logger.info(f"DOI could not be finalized for {pdf_path}")
            if not final_metadata.get("year"):
                logger.info(f"Year could not be finalized for {pdf_path}")
            # Check the finalized title
            if not final_metadata.get("title") or final_metadata.get("title") == "Manual input needed":
                logger.error(f"Title could not be finalized for {pdf_path}")

            return extraction_result

        except Exception as e:
            logger.error(f"General error processing PDF {pdf_path}: {str(e)}", exc_info=True)
            return None
        finally:
            if doc:
                try:
                    doc.close()
                except Exception as close_err:
                    logger.warning(f"Error closing PDF {pdf_path}: {close_err}")

    # --- MODIFIED SIGNATURE AND LOGIC ---
    async def _is_title_in_text(self, title: str, doc: Optional[fitz.Document] = None, markdown_text: Optional[str] = None) -> bool:
        """
        Check if the extracted title appears in the document text.
        Prioritizes checking against provided markdown_text (from Docling).
        Falls back to checking PyMuPDF document (doc) if markdown_text is None.
        """
        if not title:
            return False

        title_lower = title.strip().lower()
        if not title_lower:
            return False

        # --- Priority 1: Check Docling Markdown Text ---
        if markdown_text:
            try:
                # Simple substring check on the markdown
                if title_lower in markdown_text.lower():
                    logger.info(f"Validated title '{title}' found in Docling markdown.")
                    return True
                else:
                    logger.warning(f"Title candidate '{title}' NOT found in Docling markdown.")
                    return False # If markdown provided, don't fallback to PyMuPDF here
            except Exception as e:
                logger.warning(f"Error checking title in markdown text: {e}")
                # Fall through to PyMuPDF check if markdown check failed? Or return False?
                # Let's return False to be strict: if markdown was provided, validation relies on it.
                return False

        # --- Priority 2: Check PyMuPDF Document Text (Fallback) ---
        elif doc:
            logger.debug(f"Validating title '{title}' using PyMuPDF document text (markdown not provided).")
            try:
                # Check first page first
                page = doc.load_page(0)
                page_text = page.get_text("text", flags=fitz.TEXT_INHIBIT_SPACES) # Try inhibiting spaces
                if title_lower in page_text.lower():
                    logger.info(f"Validated title '{title}' found in PyMuPDF first page text.")
                    return True

                # Check full document text if not on first page
                full_text = ""
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    # Consider flags like TEXT_INHIBIT_SPACES for potentially better matching
                    full_text += page.get_text("text", flags=fitz.TEXT_INHIBIT_SPACES)
                    # Optimization: check incrementally?
                    # if len(full_text) > 5000 and title_lower in full_text.lower(): break # Check periodically

                if title_lower in full_text.lower():
                    logger.info(f"Validated title '{title}' found in PyMuPDF full document text.")
                    return True
                else:
                    logger.warning(f"Title candidate '{title}' NOT found in PyMuPDF document text.")
                    return False
            except Exception as e:
                logger.warning(f"Error checking title in PyMuPDF text: {e}")
                return False
        else:
            # Cannot validate if neither markdown nor doc is provided
            logger.error(f"Cannot validate title '{title}': No markdown text or PyMuPDF document provided.")
            return False

    # --- MODIFIED LOGIC AND RETURN VALUE ---
    async def _extract_title_with_docling(self, pdf_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Attempt to extract title from the highest-level markdown header on the first page using Docling.
        Finds the minimum header level present (e.g., # vs ##) and returns the first header at that level.

        Returns:
            Tuple: (title_candidate, first_page_markdown) or (None, None)
        """
        if not DOCLING_AVAILABLE:
            logger.warning("Docling is not available. Cannot extract title using Docling.")
            return None, None
        try:
            # Configure Docling pipeline options for minimal conversion of first page
            pipeline_opts = PdfPipelineOptions(
                max_num_pages=1,
                enable_remote_services=self.docling_options_config.get("enable_remote_services", False), # Use config here too
                do_code_enrichment=False, do_formula_enrichment=False,
                do_picture_classification=False, do_picture_description=False,
                generate_picture_images=False, do_table_structure=False,
            )
            converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts)})

            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, lambda: converter.convert(pdf_path))

            if result and result.document:
                markdown_text = result.document.export_to_markdown()
                if not markdown_text:
                    logger.warning("Docling conversion yielded empty markdown text.")
                    return None, None

                lines = markdown_text.splitlines()
                min_header_level = float('inf') # Start with infinity
                first_title_at_min_level = None

                # First pass: Find the minimum header level present
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped.startswith('#'):
                        match = re.match(r'^(#+)\s*(.*)', line_stripped)
                        if match:
                            heading_text = match.group(2).strip()
                            if heading_text: # Ignore empty headings
                                header_level = len(match.group(1))
                                min_header_level = min(min_header_level, header_level)

                # Second pass: Find the *first* header matching the minimum level
                if min_header_level != float('inf'): # Check if any header was found
                    for line in lines:
                        line_stripped = line.strip()
                        if line_stripped.startswith('#'):
                             match = re.match(r'^(#+)\s*(.*)', line_stripped)
                             if match:
                                 header_level = len(match.group(1))
                                 heading_text = match.group(2).strip()
                                 if header_level == min_header_level and heading_text:
                                     first_title_at_min_level = heading_text
                                     logger.info(f"Found potential title header (Level {min_header_level}): '{first_title_at_min_level}'")
                                     break # Stop after finding the first one at the min level

                if first_title_at_min_level:
                    return first_title_at_min_level, markdown_text
                else:
                    logger.warning("No suitable markdown headings found by Docling on the first page.")
                    return None, markdown_text # Return markdown even if no title found
            else:
                logger.warning("Docling conversion did not yield a result or document.")
                return None, None
        except Exception as e:
            # Log the specific error from Docling conversion
            logger.error(f"Error during Docling title extraction/conversion: {e}", exc_info=True)
            return None, None

    async def _extract_with_docling(self, pdf_path: str, initial_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract text using Docling's DocumentConverter."""
        if not DOCLING_AVAILABLE:
            return None
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

            # Prepare kwargs for the convert call
            convert_kwargs = {}
            if isinstance(max_pages, int): convert_kwargs['max_num_pages'] = max_pages
            elif max_pages is not None: logger.warning(f"Ignoring invalid docling_options.max_num_pages: {max_pages}")
            if isinstance(max_size, int): convert_kwargs['max_file_size'] = max_size
            elif max_size is not None: logger.warning(f"Ignoring invalid docling_options.max_file_size: {max_size}")

            logger.debug(f"Calling Docling convert with kwargs: {convert_kwargs}")

            # Run conversion in executor thread
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, lambda: converter.convert(pdf_path, **convert_kwargs)
            )

            if not result or not result.document:
                logger.error(f"Docling conversion failed for {pdf_path}")
                return None

            markdown_text = result.document.export_to_markdown()
            if not markdown_text:
                 logger.error(f"Docling conversion resulted in empty markdown for {pdf_path}")
                 # Fallback to plain text extraction? Or return failure?
                 # Let's try plain text as a fallback if markdown is empty
                 markdown_text = result.document.export_to_text()
                 if not markdown_text:
                     logger.error(f"Docling conversion also resulted in empty plain text for {pdf_path}")
                     return None # Return failure if both are empty
                 logger.warning(f"Using plain text extraction from Docling for {pdf_path} as markdown was empty.")


            language = await self._detect_language(markdown_text)
            # --- Section Parsing ---
            # Use markdown if available, otherwise attempt parsing on plain text (less reliable)
            sections = await self._parse_sections_from_markdown(markdown_text)

            # Pre-fill abstract if not found via metadata search
            if not metadata.get("abstract") and sections.get("abstract"):
                metadata["abstract"] = sections["abstract"][:1000] # Limit length

            # Infer missing sections with LLM if needed
            if not all(sections.get(s) for s in ["introduction", "methodology", "results", "discussion"]):
                logger.info("Attempting LLM section inference based on Docling output.")
                # Pass markdown_text which might be markdown or plain text fallback
                await self._infer_sections_with_llm(markdown_text, sections)

            # Ensure required sections exist, possibly populated from 'misc'
            required_sections = ["abstract", "introduction", "methodology", "results", "discussion", "conclusion", "references"]
            misc_content = sections.get('misc', '') # Get misc content once
            for section in required_sections:
                if not sections.get(section):
                    # If a required section is empty, try filling it from misc content
                    # Simple approach: assign all misc content to the first missing required section?
                    # Or maybe better to just leave them empty if not found/inferred? Let's leave empty.
                    sections[section] = "" # Ensure key exists
            sections.pop('misc', None) # Remove misc key after potential use or if unused


            return {
                "metadata": metadata,
                "full_text": markdown_text[:self.max_text_length],
                "sections": sections,
                "language": language
            }

        except Exception as e:
            logger.error(f"Error during Docling processing for {pdf_path}: {str(e)}", exc_info=True)
            return None

    async def _extract_with_pymupdf(self, doc: fitz.Document, initial_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract text using PyMuPDF (simpler layout analysis)."""
        logger.info(f"Extracting text using PyMuPDF for {doc.name}")
        metadata = initial_metadata.copy()
        full_text = ""
        sections = {
            "abstract": metadata.get("abstract", ""),
            "introduction": "", "methodology": "", "results": "",
            "discussion": "", "conclusion": "", "references": ""
        }
        try:
            for page_num, page in enumerate(doc):
                try:
                    full_text += page.get_text("text") + "\n"
                except Exception as page_err:
                    logger.warning(f"Error extracting text from page {page_num+1} of {doc.name}: {page_err}")
                    full_text += "[Content Extraction Error]\n"

            if not full_text:
                logger.error(f"PyMuPDF extracted no text from {doc.name}")
                return None

            language = await self._detect_language(full_text)

            logger.info("Attempting LLM section inference based on PyMuPDF full text.")
            await self._infer_sections_with_llm(full_text, sections)

            # Ensure required sections exist
            required_sections = ["abstract", "introduction", "methodology", "results", "discussion", "conclusion", "references"]
            for section in required_sections:
                 sections.setdefault(section, "") # Ensure key exists, default empty

            # Populate abstract if still missing
            if not sections["abstract"] and metadata.get("abstract"):
                sections["abstract"] = metadata["abstract"]

            return {
                "metadata": metadata,
                "full_text": full_text[:self.max_text_length],
                "sections": sections,
                "language": language
            }
        except Exception as e:
            logger.error(f"Error during PyMuPDF processing for {doc.name}: {str(e)}", exc_info=True)
            return None

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
        text_snippet = text[:min(len(text), 5000)]

        # Refine DOI
        if not metadata.get("doi"):
            doi_match = re.search(r'\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b', text_snippet, re.IGNORECASE)
            if doi_match:
                metadata["doi"] = doi_match.group(1).strip().rstrip('.')
                logger.info(f"Refined DOI from text: {metadata['doi']}")

        # Refine Year
        if not metadata.get("year"):
            year_context_match = re.search(r'(?:published|received|accepted|©|copyright|\()\s*((?:19|20)\d{2})\b', text_snippet, re.IGNORECASE)
            year_standalone_match = re.search(r'\b((?:19|20)\d{2})\b', text_snippet[:1000]) # Shorter snippet for standalone
            if year_context_match:
                metadata["year"] = year_context_match.group(1)
                logger.info(f"Refined Year from text context: {metadata['year']}")
            elif year_standalone_match:
                metadata["year"] = year_standalone_match.group(1)
                logger.info(f"Refined Year (standalone) from text: {metadata['year']}")

        # Refine Pub Info (Journal, Volume, etc.) - Less reliable regex
        if not metadata.get("journal") or not metadata.get("volume"):
            pub_match = re.search(
                r'([A-Za-z\s&]{5,})' r'(?:[,\.]|\s+)' r'(?:Vol\.?|Volume)?\s*(\d+)'
                r'(?:(?:,\s*|\s+)\(?No\.?|Issue\)?\s*(\d+|\w+))?' r'(?:(?:,\s*|\s+)\(?(?:(?:pp|pages)\.?\s*)?([\d\-–]+)\)?)?'
                r'(?:(?:,\s*|\s+)\(?((?:19|20)\d{2})\)?)?', text_snippet, re.IGNORECASE | re.MULTILINE)
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
        misc_content = []

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
        key_map = { "related_work": "methodology", "acknowledgements": "conclusion", "appendix": "references" }

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
                    if current_section_name: sections[current_section_name] = "\n".join(current_content).strip()
                    else: misc_content.extend(current_content) # Content before first known header
                    current_section_name = standard_key
                    current_content = [] # Reset content for new section
                else: # Unmatched header, treat as content
                    if current_section_name: current_content.append(line)
                    else: misc_content.append(line)
            else: # Not a header line
                if current_section_name: current_content.append(line)
                else: misc_content.append(line)

        # Save the last section
        if current_section_name: sections[current_section_name] = "\n".join(current_content).strip()
        else: misc_content.extend(current_content) # All content was misc

        # Store misc content if any
        if misc_content: sections["misc"] = "\n".join(misc_content).strip()

        logger.info(f"Sections identified via Markdown headers: {list(s for s in sections if s != 'misc')}")
        return sections

    async def _infer_sections_with_llm(self, text: str, sections: Dict[str, str]) -> None:
        """Use LLM to infer missing sections or improve section detection."""
        target_sections = ["abstract", "introduction", "methodology", "results", "discussion", "conclusion"]
        # Infer if section is missing OR has very little content (e.g., < 100 chars)
        sections_to_infer = [s for s in target_sections if len(sections.get(s, '')) < 100]

        if not sections_to_infer or not text:
            logger.debug("Skipping LLM section inference (no sections need inference or no text).")
            return

        logger.info(f"Attempting LLM inference for sections: {sections_to_infer}")
        try:
            text_limit = 50000
            if len(text) > text_limit:
                text_snippet = text[:text_limit // 2] + "\n...\n" + text[-text_limit // 2:]
            else: text_snippet = text

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
                        # Update if LLM found substantially more content or section was empty/short
                        if len(llm_content) > len(sections.get(normalized_name, '')) + 50:
                            sections[normalized_name] = llm_content.strip()
                            logger.info(f"Section '{normalized_name}' updated/populated by LLM.")
            else:
                logger.warning(f"LLM section inference did not return a valid dictionary. Response: {llm_extracted_sections}")

        except Exception as e:
            logger.warning(f"Error using LLM for section inference: {str(e)}", exc_info=True)