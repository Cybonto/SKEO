# metadata_fetcher.py - Fetches paper metadata using external APIs (SerpApi)

import os
import re
import asyncio
import aiohttp
import logging
import ssl
import certifi # Import certifi
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError # Import RetryError
import json # Added for JSONDecodeError handling

logger = logging.getLogger('skeo.metadata')

class SerpApiMetadataFetcher:
    """Fetch paper metadata using the SerpApi Google Scholar endpoint."""

    BASE_URL = "https://serpapi.com/search"

    def __init__(self, params: Optional[Dict] = None):
        """
        Initialize the fetcher with SerpApi configuration.

        Args:
            params: Optional parameters dict containing 'metadata' section.
        """
        metadata_params = params.get('metadata', {}) if params else {}
        self.api_key = metadata_params.get('serpapi_api_key', os.getenv("SERPAPI_API_KEY"))
        self.default_scholar_params = metadata_params.get('serpapi_google_scholar_params', {})

        self.enabled = bool(self.api_key)

        if not self.enabled:
            logger.warning("SerpApi metadata lookup disabled: SERPAPI_API_KEY not provided in params or environment variables.")
        else:
            # Create SSL context using certifi
            try:
                self.ssl_context = ssl.create_default_context(cafile=certifi.where())
                logger.info("SerpApi metadata fetcher initialized with SSL context using certifi.")
            except Exception as e:
                 logger.error(f"Failed to create SSL context using certifi: {e}. SSL verification might still fail.", exc_info=True)
                 self.ssl_context = None # Fallback to default SSL handling


    # Keep tenacity retry for transient network issues, but add specific error handling below
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(aiohttp.ClientError))
    async def _make_serpapi_request(self, url: str, timeout: aiohttp.ClientTimeout) -> Optional[Dict]:
        """Internal method to make the cancellable request with SSL context."""
        # Create connector inside the async function to avoid potential loop issues
        # Pass the SSL context created during initialization
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            logger.debug(f"Making GET request to: {url}")
            async with session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.warning(f"SerpApi request failed (HTTP {response.status}): {error_text[:500]}")
                    # Raise for status to trigger tenacity retry for server/client errors
                    response.raise_for_status()
                    return None # Should not be reached if raise_for_status works

                # Successfully received response
                try:
                    data = await response.json()
                    return data
                except json.JSONDecodeError as json_err:
                     logger.error(f"Failed to decode JSON response from SerpApi: {json_err}")
                     # Don't retry JSON errors, return None
                     return None

    async def search_scholar_metadata(self, title: str, first_author: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Search for paper metadata using SerpApi's Google Scholar engine.
        Handles network/SSL errors gracefully.

        Args:
            title: Paper title.
            first_author: First author's name, if available.

        Returns:
            Dict: Processed paper metadata if found, None otherwise. Maps to ScientificPaper fields where possible.
        """
        if not self.enabled:
            return None
        # Ensure title is usable
        if not title or not isinstance(title, str) or len(title.strip()) == 0:
             logger.warning("Skipping metadata search: Invalid or empty title provided.")
             return None

        search_query = f'"{title.strip()}"' # Exact title match, stripped
        if first_author and isinstance(first_author, str) and len(first_author.strip()) > 0:
            search_query += f' author:"{first_author.strip()}"'

        api_params = {
            "api_key": self.api_key,
            "engine": "google_scholar",
            "q": search_query,
            **self.default_scholar_params # Include defaults like hl, num, as_ylo etc.
        }

        # Remove None values from params
        api_params = {k: v for k, v in api_params.items() if v is not None}

        url = f"{self.BASE_URL}?{urlencode(api_params)}"
        request_timeout = aiohttp.ClientTimeout(total=30) # Timeout for SerpApi call

        logger.info(f"Querying SerpApi Google Scholar for: {search_query}")

        data = None
        try:
            # Call the internal request method which uses tenacity for retries
            data = await self._make_serpapi_request(url, request_timeout)

        # --- Graceful Error Handling ---
        except RetryError as e:
            # This catches errors if tenacity retries failed (e.g., persistent connection issues)
            logger.warning(f"SerpApi request failed after multiple retries: {e}. Proceeding without online metadata.")
            return None
        except aiohttp.ClientConnectorCertificateError as ssl_err:
            # Specific handling for the SSL certificate verification error
            logger.error(f"SerpApi SSL Certificate Verification Failed: {ssl_err}. Check your system's CA certificates or install/update 'certifi'. Proceeding without online metadata.")
            return None
        except aiohttp.ClientConnectionError as conn_err:
            # Handle other connection errors (e.g., DNS resolution failed, connection refused)
            logger.warning(f"SerpApi Connection Error: {conn_err}. Proceeding without online metadata.")
            return None
        except asyncio.TimeoutError:
            logger.warning("SerpApi request timed out. Proceeding without online metadata.")
            return None
        except Exception as e:
            # Catch any other unexpected errors during the request
            logger.error(f"Unexpected error during SerpApi request: {str(e)}", exc_info=True)
            return None
        # --- End Graceful Error Handling ---

        # --- Process Successful Response ---
        if data is None:
             # This case covers JSONDecodeError handled in _make_serpapi_request
             logger.warning("Received no valid data from SerpApi. Proceeding without online metadata.")
             return None

        # Check for errors reported by SerpApi itself in the JSON response
        if "error" in data:
             logger.warning(f"SerpApi returned an error message: {data['error']}. Proceeding without online metadata.")
             return None

        # Process organic results
        if "organic_results" not in data or not data["organic_results"]:
            logger.info(f"No Google Scholar organic results found via SerpApi for: '{title}'")
            return None

        # Process the first result (best guess)
        result = data["organic_results"][0]
        logger.info(f"Found potential metadata via SerpApi for: '{title}'")
        return self._parse_serpapi_result(result)
        # --- End Process Successful Response ---


    def _parse_serpapi_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses a single organic result from SerpApi Google Scholar response
        and maps it to the ScientificPaper schema fields where possible.
        """
        # --- (Parsing logic remains the same as before) ---
        metadata = {
            "title": result.get("title", ""),
            "authors": [],
            "publication_info": result.get("publication_info", {}),
            "journal": "",
            "publicationDate": "",
            "year": "",
            "doi": "",
            "abstract": result.get("snippet"), # Snippet often contains part of abstract
            "keywords": [], # Keywords not typically in basic results
            "fileUrl": result.get("link"), # Link to the paper's page on Scholar/publisher
            "pdfPath": None, # We don't get the direct PDF path usually
            "volume": "",
            "issue": "",
            "pages": "",
            # Add other fields if available in SerpApi response structure
            "cited_by_count": result.get("cited_by", {}).get("total"),
            "related_articles_link": result.get("related_pages_link"),
            "versions_link": result.get("versions", {}).get("link"),
            "serpapi_result_id": result.get("result_id") # Store SerpApi's internal ID
        }

        # Parse authors from publication_info summary string (heuristic)
        pub_summary = metadata["publication_info"].get("summary", "")
        if pub_summary:
            parts = pub_summary.split(" - ")
            if len(parts) > 0:
                 potential_authors_str = parts[0]
                 # Basic check to avoid misinterpreting journal as authors
                 if "," in potential_authors_str and not any(kw in potential_authors_str.lower() for kw in ["journal", "conf", "proc"]):
                      authors = [a.strip() for a in potential_authors_str.split(",")]
                      metadata["authors"] = [{"name": name} for name in authors if name]

            # Try to extract Journal, Year from parts
            year_match = re.search(r'\b(19|20)\d{2}\b', pub_summary)
            if year_match:
                metadata["year"] = year_match.group(0)
                metadata["publicationDate"] = metadata["year"]

            # Simple journal extraction (may need refinement)
            potential_journal_str = None
            if len(parts) > 1:
                potential_journal_str = parts[1] # Often the second part
            elif len(parts) == 1 and not metadata["authors"]: # If only one part and it wasn't authors
                 potential_journal_str = parts[0]

            if potential_journal_str and not re.fullmatch(r'\b(19|20)\d{2}\b', potential_journal_str.strip()):
                metadata["journal"] = potential_journal_str.strip()


        # Extract DOI if available in inline links
        inline_links = result.get("inline_links", {})
        # DOI isn't typically here, but checking just in case structure changes
        # if "doi_link" in inline_links and "link" in inline_links["doi_link"]:
        #      doi_match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', inline_links["doi_link"]["link"], re.IGNORECASE)
        #      if doi_match: metadata["doi"] = doi_match.group(1)

        # Look for direct PDF links if provided (e.g., resources)
        resources = result.get("resources", [])
        for resource in resources:
            if resource.get("file_format", "").lower() == "pdf":
                metadata["pdfPath"] = resource.get("link") # Assign first PDF link found
                break # Take the first PDF link

        # Try to extract DOI from standard link (less reliable fallback)
        if metadata["fileUrl"] and not metadata["doi"]:
            doi_match = re.search(r'(10\.\d{4,9}/[-._;()/:A-Z0-9]+)', metadata["fileUrl"], re.IGNORECASE)
            if doi_match:
                metadata["doi"] = doi_match.group(1).strip().rstrip('.')


        # Clean up empty strings and remove raw publication_info
        metadata = {k: v for k, v in metadata.items() if v or isinstance(v, (int, bool))}
        metadata.pop("publication_info", None)

        return metadata