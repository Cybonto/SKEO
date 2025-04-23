#!/usr/bin/env python3
# skeo.py - Scientific Knowledge Extraction Ontology Tool (Main Script)
# Orchestrates the extraction process.

import os
import sys
import argparse
import logging
import json
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use direct imports since all modules are expected in the same directory
# try:
from config_loader import load_params
from skeo_extractor import SKEOExtractor
# Import StrapiClient only if needed for pre-checks
from strapi_client import StrapiClient
# except ImportError as e:
#     # Provide a more specific error message if imports fail
#     print(f"Error: Could not import necessary modules ({e}).", file=sys.stderr)
#     print("Ensure skeo modules (config_loader.py, skeo_extractor.py, etc.) are in the same directory as skeo.py.", file=sys.stderr)
#     sys.exit(1)


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

async def main():
    """Main asynchronous entry point for SKEO extraction tool."""
    parser = argparse.ArgumentParser(
        description="SKEO - Scientific Knowledge Extraction Ontology Tool",
        epilog="Extracts structured knowledge from scientific papers using LLMs and saves/uploads results."
    )
    parser.add_argument(
        "--pdf-dir", "-d", required=True, help="Directory containing PDF files to process."
    )
    parser.add_argument(
        "--prompt-file", "-p", default="skeo_prompts.yaml",
        help="YAML file containing extraction prompts (default: skeo_prompts.yaml)."
    )
    parser.add_argument(
        "--output-dir", "-o", default="skeo_output",
        help="Directory to save extraction output JSON files (default: skeo_output)."
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
    parser.add_argument("--max-workers", type=int, default=None,
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
    if not os.path.isdir(args.pdf_dir):
        logger.error(f"PDF directory does not exist or is not a directory: {args.pdf_dir}")
        sys.exit(1)
    if not os.path.isfile(args.prompt_file):
        logger.error(f"Prompt file does not exist or is not a file: {args.prompt_file}")
        sys.exit(1)

    # --- Find PDFs ---
    pdf_files_to_process = []
    output_dir = args.output_dir
    skip_existing = params.get("processing", {}).get("skip_existing", True)

    try:
        for filename in os.listdir(args.pdf_dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(args.pdf_dir, filename)
                if os.path.isfile(pdf_path):
                    # Check if output already exists and should be skipped
                    if skip_existing:
                        pdf_filename_base = os.path.splitext(filename)[0]
                        safe_filename_base = re.sub(r'[^\w\-.]+', '_', pdf_filename_base)
                        output_file = os.path.join(output_dir, f"{safe_filename_base}_extraction.json")
                        if os.path.exists(output_file):
                            logger.info(f"Skipping already processed file (output exists): {filename}")
                            continue
                    pdf_files_to_process.append(pdf_path)
    except FileNotFoundError:
        logger.error(f"PDF directory not found during listing: {args.pdf_dir}")
        sys.exit(1)
    except Exception as e:
         logger.error(f"Error listing PDF files in {args.pdf_dir}: {e}", exc_info=True)
         sys.exit(1)


    if not pdf_files_to_process:
        logger.info(f"No new PDF files found to process in {args.pdf_dir} (or all skipped).")
        sys.exit(0) # Exit cleanly if nothing to do

    logger.info(f"Found {len(pdf_files_to_process)} PDF files to process.")

    # Create output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"Could not create output directory {output_dir}: {e}")
        sys.exit(1)


    # --- Initialize Extractor ---
    try:
         # Pass the loaded and potentially overridden params
         extractor = SKEOExtractor(
             prompt_file=args.prompt_file,
             output_dir=output_dir,
             params=params
         )
    except Exception as init_err:
         logger.error(f"Failed to initialize SKEOExtractor: {init_err}", exc_info=True)
         sys.exit(1)


    # --- Pre-check Strapi Connection/Endpoints (if uploading) ---
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
    concurrency_limit = processing_params.get("max_workers", 4)
    semaphore = asyncio.Semaphore(concurrency_limit)
    logger.info(f"Processing PDFs with concurrency limit: {concurrency_limit}")

    async def process_with_semaphore(pdf_path):
         # This wrapper ensures each call to process_pdf respects the semaphore limit
         async with semaphore:
              logger.debug(f"Acquired semaphore for {os.path.basename(pdf_path)}")
              try:
                   result = await extractor.process_pdf(pdf_path)
              except Exception as task_exc:
                   logger.error(f"Caught unexpected exception directly from process_pdf task for {os.path.basename(pdf_path)}: {task_exc}", exc_info=True)
                   result = (pdf_path, task_exc) # Ensure result is a tuple even on direct exception
              logger.debug(f"Released semaphore for {os.path.basename(pdf_path)}")
              return result

    tasks = [process_with_semaphore(pdf_path) for pdf_path in pdf_files_to_process]

    # Execute tasks and gather results
    # return_exceptions=True ensures gather doesn't stop on the first exception
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # --- Process Results ---
    success_count = 0
    error_count = 0
    for i, result_item in enumerate(results):
         pdf_input_path = pdf_files_to_process[i] # Get corresponding input path

         if isinstance(result_item, Exception):
              # This catches exceptions from asyncio.gather itself or the wrapper
              error_count += 1
              logger.error(f"System error during processing task for {os.path.basename(pdf_input_path)}: {result_item}", exc_info=result_item)
              if fail_fast:
                   logger.error("Fail fast enabled. Exiting due to system error.")
                   # Optionally cancel remaining tasks:
                   # for task in tasks: task.cancel()
                   sys.exit(1)
         elif isinstance(result_item, tuple) and len(result_item) == 2:
              processed_path, outcome = result_item
              # Sanity check path matches input (should always match here)
              if processed_path != pdf_input_path:
                   logger.warning(f"Path mismatch in results? Input: {pdf_input_path}, Output: {processed_path}")

              if isinstance(outcome, Exception):
                   # This catches exceptions returned *by* process_pdf
                   error_count += 1
                   # Error should have been logged within process_pdf or its sub-methods
                   logger.error(f"Failed to process {os.path.basename(processed_path)}. See previous logs for details.")
                   if fail_fast:
                        logger.error(f"Fail fast enabled. Exiting due to processing error for {os.path.basename(processed_path)}.")
                        sys.exit(1)
              elif isinstance(outcome, dict):
                   # Success case, outcome is the extracted data dict
                   success_count += 1
                   # Success logged within process_pdf
              else:
                   # Unexpected outcome type from process_pdf
                   error_count += 1
                   logger.error(f"Unexpected outcome type '{type(outcome)}' for {os.path.basename(processed_path)}")
                   if fail_fast: sys.exit(1)
         else:
              # Unexpected result format from gather
              error_count += 1
              logger.error(f"Unexpected result format from asyncio.gather for {os.path.basename(pdf_input_path)}: {result_item}")
              if fail_fast: sys.exit(1)


    # --- Final Summary ---
    logger.info("-" * 20)
    logger.info("SKEO Extraction Summary:")
    logger.info(f"  Total PDFs attempted: {len(pdf_files_to_process)}")
    logger.info(f"  Successfully processed: {success_count}")
    logger.info(f"  Failed: {error_count}")
    logger.info("-" * 20)

    if error_count > 0:
         logger.warning("Some PDFs failed processing. Check log file 'skeo_extraction.log' for detailed errors.")
         sys.exit(1) # Exit with error code if any PDF failed
    else:
         logger.info("All PDFs processed successfully.")
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