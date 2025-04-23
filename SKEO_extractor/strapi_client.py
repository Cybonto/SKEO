# strapi_client.py - Client for interacting with Strapi API

import os
import asyncio
import aiohttp
import logging
import json
from typing import Dict, List, Any, Optional
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Import load_params to get default slugs if needed (adjust path)
from config_loader import load_params

logger = logging.getLogger('skeo.strapi')

class StrapiClient:
    """Client for interacting with Strapi API"""

    def __init__(self, params: Optional[Dict] = None):
        """
        Initialize Strapi client using parameters or environment variables.

        Args:
            params: Optional parameters dict containing 'strapi' section.
        """
        self.params = params if params else {}
        strapi_params = self.params.get('strapi', {})

        self.strapi_url = strapi_params.get('url', os.getenv("STRAPI_URL", "http://localhost:1337"))
        self.strapi_token = strapi_params.get('token', os.getenv("STRAPI_API_TOKEN"))
        self.strapi_api_base_path = strapi_params.get('api_base_path', '/api')
        self.upload_batch_size = strapi_params.get('upload_batch_size', 20) # Conceptual
        self.retry_failed_uploads = strapi_params.get('retry_failed_uploads', False)

        # Load Strapi API slugs from params or defaults
        self.strapi_slugs = strapi_params.get('api_slugs', {})
        if not self.strapi_slugs:
             logger.warning("Strapi API slugs not found in params['strapi']['api_slugs']. Using default slugs from config_loader.")
             self.strapi_slugs = load_params().get('strapi', {}).get('api_slugs', {})

        self.base_headers = {
            "Content-Type": "application/json"
        }
        if self.strapi_token:
            self.base_headers["Authorization"] = f"Bearer {self.strapi_token}"
        else:
             logger.warning("Strapi API token not found in params or environment variables. Upload/Testing might fail.")

        self.endpoint_status = {} # Store endpoint test results

    async def _get_api_url(self, slug_key: str) -> Optional[str]:
         """Get the full API URL for a given component key or explicit slug."""
         # Check if slug_key is already a slug (contains '-') or a component key
         slug = self.strapi_slugs.get(slug_key, slug_key if '-' in slug_key else None)
         if not slug:
              logger.error(f"Strapi API slug not configured or identifiable for key: {slug_key}")
              return None
         return f"{self.strapi_url.rstrip('/')}{self.strapi_api_base_path.rstrip('/')}/{slug}"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1), retry=retry_if_exception_type(aiohttp.ClientError))
    async def test_connection(self):
        """Test connection to Strapi API by fetching user info."""
        test_url = f"{self.strapi_url.rstrip('/')}{self.strapi_api_base_path.rstrip('/')}/users/me"
        request_timeout = aiohttp.ClientTimeout(total=15)
        logger.info(f"Testing Strapi API connection to {self.strapi_url}...")
        if not self.strapi_token:
             logger.error("Cannot test Strapi connection: API token is missing.")
             return False
        try:
            async with aiohttp.ClientSession(headers=self.base_headers, timeout=request_timeout) as session:
                async with session.get(test_url) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        logger.info(f"Strapi API connection successful (Authenticated as User: {user_data.get('username', 'Unknown')})")
                        return True
                    else:
                        status_text = await response.text()
                        logger.warning(f"Strapi API connection test failed: {response.status} - {status_text[:200]}")
                        response.raise_for_status() # Let retry handle if appropriate
                        return False # Should not be reached
        except aiohttp.ClientError as e:
             logger.warning(f"Strapi API connection test failed (Network/Client Error): {e}")
             raise # Allow retry
        except Exception as e:
            logger.error(f"Unexpected error during Strapi connection test: {e}")
            return False

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1), retry=retry_if_exception_type(aiohttp.ClientError))
    async def test_single_endpoint(self, component_key: str) -> Dict:
         """Test a single Strapi endpoint using the component key."""
         api_url = await self._get_api_url(component_key)
         if not api_url:
              return {"status": "error", "error": "Slug not configured", "url": component_key}

         request_timeout = aiohttp.ClientTimeout(total=10)
         logger.info(f"Testing endpoint: {component_key} ({api_url})")
         try:
              async with aiohttp.ClientSession(headers=self.base_headers, timeout=request_timeout) as session:
                   async with session.get(api_url, params={"pagination[pageSize]": 1}) as response:
                        if response.status == 200:
                             return {"status": "ok", "url": api_url}
                        else:
                             status_text = await response.text()
                             logger.warning(f"Endpoint test failed for {component_key}: {response.status} - {status_text[:200]}")
                             return {"status": "error", "error": f"{response.status} - {status_text[:200]}", "url": api_url}
         except aiohttp.ClientError as e:
              logger.warning(f"Endpoint test failed for {component_key} (Network/Client Error): {e}")
              return {"status": "error", "error": f"Network/Client Error: {e}", "url": api_url}
         except Exception as e:
              logger.error(f"Unexpected error testing endpoint {component_key}: {e}")
              return {"status": "error", "error": f"Unexpected Error: {e}", "url": api_url}

    async def test_all_endpoints(self):
        """Test all API endpoints defined in strapi_slugs concurrently."""
        logger.info("Testing availability of all configured Strapi endpoints...")
        if not self.strapi_slugs:
             logger.warning("No Strapi slugs configured to test.")
             return {}

        tasks = []
        for component_key in self.strapi_slugs.keys():
             tasks.append(self.test_single_endpoint(component_key))

        results = await asyncio.gather(*tasks)

        self.endpoint_status = {}
        successful = 0
        total_endpoints = len(self.strapi_slugs)

        for i, component_key in enumerate(self.strapi_slugs.keys()):
             self.endpoint_status[component_key] = results[i]
             if results[i]["status"] == "ok":
                  successful += 1
             else:
                  logger.warning(f"Endpoint '{component_key}' failed test: {results[i].get('error', 'Unknown reason')}")

        logger.info(f"Strapi endpoint test complete: {successful}/{total_endpoints} endpoints available.")
        return self.endpoint_status


    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(aiohttp.ClientError))
    async def _upload_single_entity(self, strapi_slug: str, entity_payload: Dict) -> Dict:
        """Upload a single entity payload to the specified Strapi slug with retry logic."""
        api_url = await self._get_api_url(strapi_slug) # Use slug directly
        if not api_url:
             # Should not happen if called correctly, but check anyway
             raise ValueError(f"Invalid Strapi slug provided for upload: {strapi_slug}")

        payload = {"data": entity_payload}
        request_timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(headers=self.base_headers, timeout=request_timeout) as session:
            logger.debug(f"POSTing to {api_url} with payload keys: {list(payload['data'].keys())}")
            async with session.post(api_url, json=payload) as response:
                 if response.status in (200, 201): # OK or Created
                     result_data = await response.json()
                     if not result_data or "data" not in result_data or "id" not in result_data["data"]:
                          logger.warning(f"Strapi returned success status ({response.status}) but invalid data structure for {strapi_slug}")
                          return {"status": "warning", "message": "Success status but invalid response structure", "response": result_data}
                     return {"status": "success", "id": result_data["data"]["id"], "response": result_data}
                 else:
                     error_text = await response.text()
                     logger.warning(f"Failed to create entity via {api_url} (HTTP {response.status}): {error_text[:500]}")
                     # Log payload carefully if needed for debugging (mask sensitive data)
                     try:
                         payload_str = json.dumps(payload)
                         logger.debug(f"Failed Payload (first 500 chars): {payload_str[:500]}")
                     except Exception:
                         logger.debug("Could not serialize payload for logging.")
                     response.raise_for_status() # Let retry handle if possible
                     # This part might not be reached if raise_for_status succeeds
                     return {"status": "error", "status_code": response.status, "error": error_text}


    async def upload_data(self, data_by_strapi_slug: Dict[str, List[Dict]]):
        """
        Upload extracted data to Strapi, handling dependencies conceptually.

        Args:
            data_by_strapi_slug: Dict mapping Strapi API slugs (plural)
                               to lists of entity data dicts prepared for upload
                               (relations should contain internal UUIDs).

        Returns:
            Dict with upload results: {total, succeeded, failed, created_ids, errors}
        """
        if not self.strapi_token:
            logger.error("Strapi API token not provided. Cannot upload.")
            return {"status": "error", "error": "Strapi token missing", "total": 0, "succeeded": 0, "failed": 0, "created_ids": {}, "errors": []}

        # Define entity processing order based on Strapi slugs (best guess for dependencies)
        # Order matters: Create items that others depend on first.
        processing_order_keys = [ # Use the internal component keys for ordering logic
            "scientific_paper", "research_context", "theoretical_basis",
            "research_problem", "knowledge_gap", "research_question",
            "scientific_challenge", "potential_application", "material_tool",
            "methodological_framework", "methodological_challenge",
            "implementation_challenge", "limitation", "future_direction"
        ]
        # Convert keys to slugs for processing
        processing_order_slugs = [self.strapi_slugs.get(k) for k in processing_order_keys if self.strapi_slugs.get(k)]
        # Add any slugs present in data but not in the ordered list (append at end)
        for slug in data_by_strapi_slug.keys():
            if slug not in processing_order_slugs:
                 processing_order_slugs.append(slug)

        results = {
            "total": 0, "succeeded": 0, "failed": 0,
            "created_ids": {}, # Maps internal UUID -> Strapi ID
            "errors": []
        }
        processed_internal_ids = set() # Track attempts by internal UUID

        for strapi_slug in processing_order_slugs:
            if strapi_slug not in data_by_strapi_slug:
                continue # Skip if no data for this slug

            entities = data_by_strapi_slug[strapi_slug]
            if not isinstance(entities, list):
                 logger.warning(f"Data for slug '{strapi_slug}' is not a list, skipping.")
                 continue

            logger.info(f"Attempting to upload {len(entities)} entities for slug '{strapi_slug}'")

            for entity_upload_payload in entities:
                if not isinstance(entity_upload_payload, dict):
                     logger.warning(f"Skipping non-dict item found for slug '{strapi_slug}'")
                     continue

                # We need the internal ID to track creation and resolve dependencies
                # The extractor should add this temporarily before calling _prepare_data_for_strapi_upload
                internal_id = entity_upload_payload.pop("internal_id", None)
                if not internal_id:
                     logger.error(f"Entity payload for '{strapi_slug}' is missing 'internal_id' for tracking. Cannot upload reliably. Payload keys: {list(entity_upload_payload.keys())}")
                     results["total"] +=1 # Count as attempt
                     results["failed"] += 1
                     results["errors"].append({
                          "slug": strapi_slug,
                          "error": "Missing internal_id in prepared payload.",
                          "payload_keys": list(entity_upload_payload.keys())
                     })
                     continue # Skip this entity

                if internal_id in processed_internal_ids:
                     logger.debug(f"Skipping already processed internal ID '{internal_id}' for slug '{strapi_slug}'")
                     continue

                results["total"] += 1
                processed_internal_ids.add(internal_id)

                # Resolve relationship IDs within the payload
                resolved_payload = {}
                has_unresolved_deps = False
                for field, value in entity_upload_payload.items():
                    is_single_relation = isinstance(value, str) and len(value) == 32 # Assume 32-char UUIDs
                    is_multi_relation = isinstance(value, list) and value and all(isinstance(item, str) and len(item)==32 for item in value)

                    if is_single_relation:
                         strapi_rel_id = results["created_ids"].get(value)
                         if strapi_rel_id:
                              resolved_payload[field] = strapi_rel_id
                         else:
                              logger.warning(f"Dependency '{field}' (Internal ID: {value}) not resolved for '{strapi_slug}' (Internal ID: {internal_id}). Skipping field in upload.")
                              has_unresolved_deps = True
                    elif is_multi_relation:
                         resolved_ids = []
                         for item_internal_id in value:
                              item_strapi_id = results["created_ids"].get(item_internal_id)
                              if item_strapi_id:
                                   resolved_ids.append(item_strapi_id)
                              else:
                                   logger.warning(f"Dependency item in '{field}' (Internal ID: {item_internal_id}) not resolved for '{strapi_slug}' (Internal ID: {internal_id}). Skipping item.")
                                   has_unresolved_deps = True
                         if resolved_ids:
                              resolved_payload[field] = resolved_ids
                    else:
                         # Copy other fields (primitives, components as dicts/lists)
                         resolved_payload[field] = value

                # Upload the resolved payload
                try:
                    upload_attempt_result = await self._upload_single_entity(strapi_slug, resolved_payload)

                    if upload_attempt_result.get("status") in ["success", "warning"]:
                         results["succeeded"] += 1
                         strapi_id = upload_attempt_result.get("id")
                         if strapi_id:
                              results["created_ids"][internal_id] = strapi_id
                              logger.debug(f"Uploaded {strapi_slug} '{internal_id}' -> Strapi ID {strapi_id}")
                         else:
                              logger.warning(f"Upload for {strapi_slug} '{internal_id}' reported success/warning but no Strapi ID found in response.")
                    else:
                         results["failed"] += 1
                         error_info = {
                              "slug": strapi_slug,
                              "internal_id": internal_id,
                              "payload_sent_keys": list(resolved_payload.keys()), # Log keys only
                              "error": upload_attempt_result.get("error", "Unknown upload error"),
                              "status_code": upload_attempt_result.get("status_code")
                         }
                         results["errors"].append(error_info)

                except Exception as upload_err:
                     results["failed"] += 1
                     error_info = {
                          "slug": strapi_slug,
                          "internal_id": internal_id,
                          "error": f"Upload failed after retries: {str(upload_err)}"
                     }
                     results["errors"].append(error_info)
                     logger.error(f"Upload ultimately failed for {strapi_slug} '{internal_id}': {upload_err}")


        logger.info(f"Strapi Upload Summary: Total={results['total']}, Succeeded={results['succeeded']}, Failed={results['failed']}")
        if results["errors"]:
             logger.warning(f"Encountered {len(results['errors'])} errors during upload. Check logs and results['errors'] for details.")
             # Optionally log error details here
             # for error in results["errors"][:5]: logger.warning(f"  - Error detail: {error}")

        return results