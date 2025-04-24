#!/usr/bin/env python3
# skeo.py - Scientific Knowledge Extraction Ontology Tool (Main Script)
# Orchestrates the extraction process, supporting recursive directory processing.

import os
import sys
import argparse
import logging
import json
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Use direct imports since all modules are expected in the same directory
try:
    from llm_client import LLMClient
    from metadata_fetcher import SerpApiMetadataFetcher
    from pdf_processor import PDFProcessor
    from prompt_manager import PromptManager
    from config_loader import load_params
    from skeo_extractor import SKEOExtractor
    # Import StrapiClient only if needed for pre-checks
    #from strapi_client import StrapiClient
except ImportError as e:
    # Provide a more specific error message if imports fail
    print(f"Error: Could not import necessary modules ({e}).", file=sys.stderr)
    print("Ensure skeo modules (config_loader.py, skeo_extractor.py, etc.) are in the same directory as skeo.py.", file=sys.stderr)
    sys.exit(1)


# Configure logging (basic setup)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("skeo_extraction.log"),
        logging.StreamHandler(sys.stdout) # Ensure logs go to stdout
    ]
)
logger = logging.getLogger('skeo.main')

# --- Helper Function for Safe Filename ---
def create_safe_filename_base(filename: str) -> str:
    """Removes extension and makes the filename safe for filesystem paths."""
    base = os.path.splitext(filename)[0]
    safe_base = re.sub(r'[^\w\-.]+', '_', base)
    return safe_base

async def main():
    """Main asynchronous entry point for SKEO extraction tool."""
    parser = argparse.ArgumentParser(
        description="SKEO - Scientific Knowledge Extraction Ontology Tool",
        epilog="Extracts structured knowledge from scientific papers (found recursively) using LLMs and saves/uploads results, mirroring input directory structure."
    )
    parser.add_argument(
        "--pdf-dir", "-d", required=True, help="Root directory containing PDF files to process (searches recursively)."
    )
    parser.add_argument(
        "--prompt-file", "-p", default="skeo_prompts.yaml",
        help="YAML file containing extraction prompts (default: skeo_prompts.yaml)."
    )
    parser.add_argument(
        "--output-dir", "-o", default="skeo_output",
        help="Root directory to save extraction output JSON files (mirrors input structure, default: skeo_output)."
    )
    parser.add_argument(
        "--params-file", default=None,
        help="Optional YAML file containing parameters (overrides defaults and env vars)."
    )
    # Allow direct Strapi overrides via CLI
    parser.add_argument("--strapi-url", help="Override Strapi API URL from params/env.")
    parser.add_argument("--strapi-token", help="Override Strapi API token from params/env.")
    parser.add_argument("--direct-upload", action='store_true', default=None,
                        help="Enable direct upload to Strapi (overrides params).")
    parser.add_argument("--no-direct-upload", dest='direct_upload', action='store_false',
                        help="Disable direct upload to Strapi (overrides params).")
    parser.add_argument("--skip-existing", action=argparse.BooleanOptionalAction, default=None,
                        help="Override processing.skip_existing param (e.g., --skip-existing / --no-skip-existing).")
    parser.add_argument("--fail-fast", action=argparse.BooleanOptionalAction, default=None,
                        help="Override processing.fail_fast param.")
    parser.add_argument("--max-workers", type=int, default=1,
                        help="Override processing.max_workers param for concurrency limit.")

    args = parser.parse_args()

    # --- Parameter Loading & CLI Overrides ---
    try:
        params = load_params(args.params_file)
    except Exception as e:
        logger.error(f"Failed to load parameters: {e}", exc_info=True)
        sys.exit(1)

    # Apply CLI overrides carefully
    if args.strapi_url:
        params.setdefault('strapi', {})['url'] = args.strapi_url
        logger.info(f"Overriding Strapi URL from CLI: {args.strapi_url}")
    if args.strapi_token:
         params.setdefault('strapi', {})['token'] = args.strapi_token
         logger.info("Overriding Strapi Token from CLI.")
    if args.direct_upload is not None: # Check if flag was used
         params.setdefault('strapi', {})['direct_upload'] = args.direct_upload
         logger.info(f"Overriding direct_upload to {args.direct_upload} from CLI.")
    if args.skip_existing is not None:
         params.setdefault('processing', {})['skip_existing'] = args.skip_existing
         logger.info(f"Overriding skip_existing to {args.skip_existing} from CLI.")
    if args.fail_fast is not None:
         params.setdefault('processing', {})['fail_fast'] = args.fail_fast
         logger.info(f"Overriding fail_fast to {args.fail_fast} from CLI.")
    if args.max_workers is not None:
         params.setdefault('processing', {})['max_workers'] = args.max_workers
         logger.info(f"Overriding max_workers to {args.max_workers} from CLI.")

    # --- Path Validation ---
    input_pdf_dir = Path(args.pdf_dir).resolve() # Use absolute path for consistency
    output_base_dir = Path(args.output_dir).resolve()

    if not input_pdf_dir.is_dir():
        logger.error(f"PDF directory does not exist or is not a directory: {input_pdf_dir}")
        sys.exit(1)
    if not os.path.isfile(args.prompt_file): # Keep os.path for non-Path vars if preferred
        logger.error(f"Prompt file does not exist or is not a file: {args.prompt_file}")
        sys.exit(1)

    # Create base output directory if it doesn't exist
    try:
        output_base_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Could not create base output directory {output_base_dir}: {e}")
        sys.exit(1)

    # --- Find PDFs Recursively & Determine Output Paths ---
    # Stores tuples of (input_pdf_path, output_json_path)
    files_to_process: List[Tuple[Path, Path]] = []
    skip_existing = params.get("processing", {}).get("skip_existing", True)
    skipped_count = 0
    found_count = 0

    logger.info(f"Scanning for PDF files recursively in: {input_pdf_dir}")
    try:
        for root, _, filenames in os.walk(input_pdf_dir):
            current_dir = Path(root)
            for filename in filenames:
                if filename.lower().endswith('.pdf'):
                    found_count += 1
                    pdf_path = current_dir / filename

                    # Calculate relative path from the input base directory
                    relative_pdf_dir = current_dir.relative_to(input_pdf_dir)

                    # Construct the corresponding output subdirectory
                    output_subdir = output_base_dir / relative_pdf_dir

                    # Construct the output JSON filename
                    safe_filename_base = create_safe_filename_base(filename)
                    output_json_filename = f"{safe_filename_base}_extraction.json"
                    output_json_path = output_subdir / output_json_filename

                    # Check if output already exists and should be skipped
                    if skip_existing and output_json_path.exists():
                        logger.debug(f"Skipping already processed file (output exists): {pdf_path.relative_to(input_pdf_dir)}")
                        skipped_count += 1
                        continue

                    # Add the pair to the list of files to process
                    files_to_process.append((pdf_path, output_json_path))
                    logger.debug(f"Planning to process: {pdf_path} -> {output_json_path}")

    except FileNotFoundError:
        # Should not happen due to initial check, but belt-and-suspenders
        logger.error(f"PDF directory not found during scan: {input_pdf_dir}")
        sys.exit(1)
    except Exception as e:
         logger.error(f"Error scanning for PDF files in {input_pdf_dir}: {e}", exc_info=True)
         sys.exit(1)

    if not files_to_process:
        logger.info(f"No new PDF files found to process in {input_pdf_dir} (Found: {found_count}, Skipped existing: {skipped_count}).")
        sys.exit(0) # Exit cleanly if nothing to do

    logger.info(f"Found {found_count} total PDFs. Planning to process {len(files_to_process)} new files (Skipped {skipped_count} existing).")


    # --- Initialize Extractor ---
    # NOTE: The output_dir passed here is the *base* output directory.
    #       The actual saving location within process_pdf will use the specific
    #       output_json_path calculated above and passed during the call.
    try:
         # Pass the loaded and potentially overridden params
         extractor = SKEOExtractor(
             prompt_file=args.prompt_file,
             output_dir=str(output_base_dir), # Pass base dir for potential internal use
             params=params
         )
         # --- !!! IMPORTANT REQUIREMENT !!! ---
         # Ensure that the SKEOExtractor.process_pdf method in skeo_extractor.py
         # has been updated to accept a second argument 'output_json_path: str' (or Path)
         # and uses *that* path for saving the JSON output, including creating
         # necessary subdirectories using os.makedirs(os.path.dirname(output_json_path), exist_ok=True).
         # Example signature:
         # async def process_pdf(self, pdf_path: Union[str, Path], output_json_path: Union[str, Path]) -> Union[Tuple[str, Dict], Tuple[str, Exception]]:
         # --- / IMPORTANT REQUIREMENT --- ---
    except Exception as init_err:
         logger.error(f"Failed to initialize SKEOExtractor: {init_err}", exc_info=True)
         sys.exit(1)


    # --- Pre-check Strapi Connection/Endpoints (if uploading) ---
    # (Strapi logic remains the same)
    strapi_ok = True
    direct_upload_enabled = params.get("strapi", {}).get("direct_upload", False)

    if direct_upload_enabled:
        # Check if the extractor initialized the strapi_client correctly
        if not extractor.strapi_client:
             logger.error("Direct upload enabled but Strapi client failed to initialize (check params/token).")
             strapi_ok = False
        else:
             logger.info("Direct upload enabled. Testing Strapi connection...")
             if not await extractor.strapi_client.test_connection():
                  strapi_ok = False
             elif params.get("strapi", {}).get("test_endpoints", True):
                  logger.info("Testing Strapi endpoints...")
                  endpoint_status = await extractor.strapi_client.test_all_endpoints()
                  # Check if any endpoint failed
                  if any(status["status"] == "error" for status in endpoint_status.values()):
                       strapi_ok = False

        if not strapi_ok and params.get("processing", {}).get("fail_fast", False):
            logger.error("Strapi connection or endpoint check failed and fail_fast is enabled. Exiting.")
            sys.exit(1)
        elif not strapi_ok:
             logger.warning("Strapi connection or endpoint check failed. Direct upload might fail for processed files.")
        else:
             logger.info("Strapi connection and endpoints check successful.")


    # --- Process PDFs Concurrently using asyncio ---
    processing_params = params.get("processing", {})
    fail_fast = processing_params.get("fail_fast", False)
    concurrency_limit = processing_params.get("max_workers", 1)
    semaphore = asyncio.Semaphore(concurrency_limit)
    logger.info(f"Processing PDFs with concurrency limit: {concurrency_limit}")

    async def process_with_semaphore(pdf_path: Path, output_path: Path):
         """Wrapper to run process_pdf with semaphore and pass output path."""
         async with semaphore:
              pdf_display_name = pdf_path.relative_to(input_pdf_dir) # For logging
              logger.debug(f"Acquired semaphore for {pdf_display_name}")
              try:
                   # --- MODIFIED CALL ---
                   # Pass both the input PDF path and the calculated output JSON path
                   # Ensure SKEOExtractor.process_pdf expects these arguments!
                   result = await extractor.process_pdf(pdf_path, output_path)
              except Exception as task_exc:
                   logger.error(f"Caught unexpected exception directly from process_pdf task for {pdf_display_name}: {task_exc}", exc_info=True)
                   # Return the *input* path and the exception
                   result = (str(pdf_path), task_exc)
              logger.debug(f"Released semaphore for {pdf_display_name}")

              # Ensure result is a tuple (path_str, outcome) even on direct exception
              if isinstance(result, tuple) and len(result) == 2:
                   # SKEOExtractor.process_pdf should ideally return (str(pdf_path), outcome)
                   # Ensure the first element is the *original input pdf path* as a string
                   if result[0] != str(pdf_path):
                        logger.warning(f"Path mismatch in process_pdf result for {pdf_display_name}. Expected {pdf_path}, got {result[0]}. Correcting.")
                        result = (str(pdf_path), result[1])
                   return result
              else:
                   # If process_pdf failed unexpectedly or returned wrong format
                   logger.error(f"Unexpected return type '{type(result)}' from process_pdf for {pdf_display_name}. Wrapping in error tuple.")
                   return (str(pdf_path), Exception(f"Unexpected return type from process_pdf: {type(result)}"))


    # Create tasks with both input and output paths
    tasks = [process_with_semaphore(pdf_path, output_path) for pdf_path, output_path in files_to_process]

    # Execute tasks and gather results
    results = await asyncio.gather(*tasks, return_exceptions=True) # Handles internal asyncio errors

    # --- Process Results ---
    success_count = 0
    error_count = 0
    processed_input_paths = [str(paths[0]) for paths in files_to_process] # Get input paths as strings

    for i, result_item in enumerate(results):
         pdf_input_path_str = processed_input_paths[i] # Get corresponding input path string
         pdf_display_name = Path(pdf_input_path_str).relative_to(input_pdf_dir) # For logging

         if isinstance(result_item, Exception):
              # This catches exceptions from asyncio.gather itself or the semaphore wrapper
              error_count += 1
              logger.error(f"System error during processing task for {pdf_display_name}: {result_item}", exc_info=result_item)
              if fail_fast:
                   logger.error("Fail fast enabled. Exiting due to system error.")
                   sys.exit(1)
         elif isinstance(result_item, tuple) and len(result_item) == 2:
              processed_path_str, outcome = result_item
              # Sanity check path matches input string (should match due to wrapper logic)
              if processed_path_str != pdf_input_path_str:
                   logger.warning(f"Path mismatch in results? Input: {pdf_input_path_str}, Output tuple path: {processed_path_str}")
                   # Trust the index for associating with the original file
                   processed_path_str = pdf_input_path_str

              if isinstance(outcome, Exception):
                   # This catches exceptions returned *by* process_pdf or the wrapper
                   error_count += 1
                   # Error should have been logged within process_pdf or its sub-methods/wrapper
                   logger.error(f"Failed to process {pdf_display_name}. See previous logs for details (Exception: {outcome}).")
                   if fail_fast:
                        logger.error(f"Fail fast enabled. Exiting due to processing error for {pdf_display_name}.")
                        sys.exit(1)
              elif isinstance(outcome, dict):
                   # Success case, outcome is the extracted data dict
                   success_count += 1
                   logger.info(f"Successfully processed: {pdf_display_name}")
                   # Specific success details (like output path) should be logged within process_pdf
              else:
                   # Unexpected outcome type from process_pdf
                   error_count += 1
                   logger.error(f"Unexpected outcome type '{type(outcome)}' for {pdf_display_name}")
                   if fail_fast: sys.exit(1)
         else:
              # Unexpected result format from gather
              error_count += 1
              logger.error(f"Unexpected result format from asyncio.gather for {pdf_display_name}: {result_item}")
              if fail_fast: sys.exit(1)


    # --- Final Summary ---
    logger.info("-" * 20)
    logger.info("SKEO Extraction Summary:")
    logger.info(f"  Input directory scanned: {input_pdf_dir}")
    logger.info(f"  Output base directory: {output_base_dir}")
    logger.info(f"  Total PDFs found: {found_count}")
    logger.info(f"  Skipped (output exists): {skipped_count}")
    logger.info(f"  Attempted processing: {len(files_to_process)}")
    logger.info(f"  Successfully processed: {success_count}")
    logger.info(f"  Failed: {error_count}")
    logger.info("-" * 20)

    if error_count > 0:
         logger.warning("Some PDFs failed processing. Check log file 'skeo_extraction.log' for detailed errors.")
         sys.exit(1) # Exit with error code if any PDF failed
    else:
         logger.info("All planned PDFs processed successfully.")
         sys.exit(0) # Exit cleanly


if __name__ == "__main__":
    # Optional: Use uvloop for potentially better asyncio performance
    try:
        import uvloop
        uvloop.install()
        logger.info("Using uvloop for asyncio event loop.")
    except ImportError:
        logger.debug("uvloop not found, using standard asyncio event loop.")
        pass
    except Exception as e:
         logger.warning(f"Failed to install uvloop: {e}")

    # Run the main async function
    asyncio.run(main())