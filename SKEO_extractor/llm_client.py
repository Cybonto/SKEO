# llm_client.py - Client for interacting with LLM APIs

import os
import json
import re
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional, Union
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from pydantic import ValidationError

logger = logging.getLogger('skeo.llm')

class LLMClient:
    """Client for interacting with LLM via HTTP API (using aiohttp)"""

    def __init__(self, params: Optional[Dict] = None):
        """
        Initialize LLM client using environment variables or params

        Args:
            params: Optional parameters dict overriding environment variables
        """
        llm_params = params.get('llm', {}) if params else {}

        self.api_base = llm_params.get('api_endpoint', os.getenv("LLM_API_ENDPOINT", "https://api.openai.com"))
        self.api_key = llm_params.get('api_key', os.getenv("LLM_API_KEY"))
        self.model = llm_params.get('model', os.getenv("LLM_MODEL_NAME", "gpt-4-1106-preview"))
        self.api_base_path = llm_params.get('api_base_path', "/v1")
        self.chat_endpoint = llm_params.get('chat_endpoint', "/chat/completions")
        self.health_endpoint = llm_params.get('health_endpoint') # Often None/unused

        if not self.api_base:
            raise ValueError("LLM_API_ENDPOINT environment variable or llm.api_endpoint param is required")

        self.base_headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            self.base_headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            logger.warning("LLM API Key not configured. Requests might fail.")

        # Extract LLM settings
        self.max_tokens = llm_params.get('max_tokens', 4000)
        self.temperature = llm_params.get('temperature', 0.2)
        self.retry_attempts = llm_params.get('retry_attempts', 3)
        self.timeout_seconds = llm_params.get('timeout_seconds', 120)
        self.validation_mode = llm_params.get('validation_mode', "strict") # strict or lenient

        # Run connection check asynchronously if needed (or just log config)
        logger.info(f"LLM Client configured: endpoint={self.api_base}, model={self.model}")
        # Consider adding an async check method to be called externally if needed:
        # asyncio.run(self._check_connection()) # Avoid running async in __init__

    async def _check_connection(self):
        """Verify LLM API connection with a test prompt (optional, call externally)"""
        logger.info("Verifying LLM API connection...")
        try:
            test_response = await self.generate_response(
                "Respond precisely with 'LLM connection successful' if you can process this message.",
                max_tokens=10, temperature=0.0
            )
            if "LLM connection successful" in test_response:
                logger.info("LLM API connection verified successfully via test prompt.")
                return True
            else:
                logger.warning(f"LLM API test prompt received unexpected response: '{test_response}'")
                return False
        except Exception as e:
            logger.error(f"Could not verify LLM API connection: {str(e)}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(aiohttp.ClientError))
    async def generate_response(self, prompt: str, max_tokens: Optional[int] = None, temperature: Optional[float] = None) -> str:
        """Generate a response from the LLM using aiohttp with retries."""
        max_tokens = max_tokens if max_tokens is not None else self.max_tokens
        temperature = temperature if temperature is not None else self.temperature

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        # Handle potential variations in API base/path structure
        api_base = self.api_base.rstrip('/')
        api_path = self.api_base_path.strip('/')
        chat_path = self.chat_endpoint.lstrip('/')
        url = f"{api_base}/{api_path}/{chat_path}" if api_path else f"{api_base}/{chat_path}"

        request_timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)

        try:
            async with aiohttp.ClientSession(headers=self.base_headers, timeout=request_timeout) as session:
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()
                    response_data = await response.json()
                    if not response_data.get("choices") or not response_data["choices"][0].get("message"):
                         raise ValueError("Invalid response structure from LLM API")
                    return response_data["choices"][0]["message"]["content"]
        except aiohttp.ClientResponseError as e:
            logger.error(f"LLM API Error (HTTP {e.status}): {e.message} for URL {url}")
            try:
                error_body = await e.response.text()
                logger.error(f"LLM Error Body: {error_body[:500]}") # Log beginning of error body
            except Exception:
                 pass # Ignore errors reading the body
            raise
        except asyncio.TimeoutError:
            logger.error(f"LLM API request timed out after {self.timeout_seconds} seconds for URL {url}.")
            raise
        except aiohttp.ClientConnectionError as e:
            logger.error(f"LLM API connection error to {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling LLM API at {url}: {str(e)}", exc_info=True)
            raise

    async def extract_json(self, prompt: str, schema_model=None) -> Optional[Union[Dict, List[Dict]]]:
        """
        Extract structured JSON data using the LLM, with schema validation and retries.

        Args:
            prompt (str): The prompt instructing JSON extraction
            schema_model: Optional Pydantic model for validation

        Returns:
            Optional[Union[Dict, List[Dict]]]: The extracted and validated JSON data, or None if extraction fails definitively.
        """
        current_prompt = prompt
        last_error = None

        for attempt in range(self.retry_attempts):
            logger.info(f"Attempting LLM JSON extraction (Attempt {attempt+1}/{self.retry_attempts})")
            try:
                # Add schema/format instructions on each attempt
                json_prompt = f"{current_prompt}\n\nImportant: Respond ONLY with valid, parseable JSON. Do not include any introductory text, explanations, apologies, or markdown formatting like ```json ... ``` around the JSON object/array."

                if schema_model and self.validation_mode == "strict":
                    try:
                        # Use model_json_schema() for Pydantic v2+
                        schema_info = json.dumps(schema_model.model_json_schema())
                        json_prompt += f"\n\nThe JSON response MUST conform strictly to this Pydantic JSON schema: {schema_info}"
                    except AttributeError: # Fallback for older Pydantic or potential issues
                         logger.warning(f"Using schema_json() fallback for model {schema_model.__name__}")
                         try:
                              schema_info = schema_model.schema_json()
                              json_prompt += f"\n\nThe JSON response MUST conform strictly to this Pydantic schema: {schema_info}"
                         except Exception as schema_err:
                              logger.warning(f"Could not generate JSON schema for model {schema_model.__name__}: {schema_err}")
                    except Exception as schema_err:
                        logger.warning(f"Could not generate JSON schema for model {schema_model.__name__}: {schema_err}")

                response_str = await self.generate_response(json_prompt, temperature=0.1)
                logger.debug(f"LLM JSON attempt {attempt+1} raw response: {response_str[:500]}...")

                json_data = None
                # Attempt to parse JSON directly first
                try:
                    # Strip potential markdown backticks and 'json' language identifier
                    clean_response = re.sub(r'^```(?:json)?\s*|\s*```$', '', response_str.strip(), flags=re.DOTALL)
                    json_data = json.loads(clean_response)
                except json.JSONDecodeError as e:
                    logger.warning(f"Direct JSON parse failed (attempt {attempt+1}): {e}. Raw response: {response_str[:200]}")
                    last_error = f"Invalid JSON: {e}"
                    current_prompt += f"\n\nYour previous response was not valid JSON. Please provide only the raw JSON object/array. Error: {e}"
                    continue # Go to next retry attempt

                # Validate against schema if provided
                if schema_model:
                    try:
                        if isinstance(json_data, list):
                            # Use model_validate for Pydantic v2+
                            validated_data = [schema_model.model_validate(item) for item in json_data]
                            logger.info(f"Successfully extracted and validated list of {len(validated_data)} {schema_model.__name__} items.")
                            return [item.model_dump(exclude_unset=True) for item in validated_data]
                        elif isinstance(json_data, dict):
                             validated_data = schema_model.model_validate(json_data)
                             logger.info(f"Successfully extracted and validated {schema_model.__name__}.")
                             return validated_data.model_dump(exclude_unset=True)
                        else:
                            raise ValidationError(f"Expected JSON object or list, got {type(json_data)}", model=schema_model)

                    except ValidationError as ve:
                        last_error = f"Schema validation failed: {str(ve)}"
                        logger.warning(f"Schema validation error (attempt {attempt+1}/{self.retry_attempts}): {str(ve)}")
                        if self.validation_mode == "strict":
                            current_prompt += f"\n\nYour previous response had validation errors against the schema: {str(ve)}\nPlease fix them and ensure conformance to the required schema."
                            continue # Go to next retry attempt
                        else: # Lenient mode
                            logger.warning(f"Schema validation errors ignored in lenient mode.")
                            return json_data # Return raw data despite errors
                    except AttributeError: # Handle Pydantic v1 fallback if needed
                         logger.warning("Attempting Pydantic v1 validation fallback (parse_obj).")
                         try:
                              if isinstance(json_data, list):
                                   validated_data = [schema_model.parse_obj(item) for item in json_data]
                                   logger.info(f"Successfully extracted and validated list of {len(validated_data)} {schema_model.__name__} items (v1).")
                                   return [item.dict(exclude_unset=True) for item in validated_data]
                              elif isinstance(json_data, dict):
                                   validated_data = schema_model.parse_obj(json_data)
                                   logger.info(f"Successfully extracted and validated {schema_model.__name__} (v1).")
                                   return validated_data.dict(exclude_unset=True)
                         except ValidationError as ve_v1:
                              last_error = f"Schema validation failed (v1 fallback): {str(ve_v1)}"
                              logger.warning(f"Schema validation error (v1 fallback, attempt {attempt+1}): {str(ve_v1)}")
                              if self.validation_mode == "strict":
                                   current_prompt += f"\n\nYour previous response had validation errors against the schema (v1): {str(ve_v1)}\nPlease fix them."
                                   continue
                              else:
                                   return json_data # Lenient mode


                else:
                    # No schema provided, return parsed JSON
                    logger.info("Successfully extracted JSON (no schema validation requested).")
                    return json_data

            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as e:
                last_error = f"API/Response Error: {str(e)}"
                logger.warning(f"Error during JSON extraction attempt {attempt+1}: {str(e)}")
                if attempt == self.retry_attempts - 1:
                    logger.error(f"Failed to extract JSON after {self.retry_attempts} attempts. Last error: {last_error}")
                    return None # Indicate definitive failure
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                last_error = f"Unexpected Error: {str(e)}"
                logger.error(f"Unexpected error during JSON extraction attempt {attempt+1}: {str(e)}", exc_info=True)
                if attempt == self.retry_attempts - 1:
                     logger.error(f"Failed to extract JSON after {self.retry_attempts} attempts due to unexpected error. Last error: {last_error}")
                     return None # Indicate definitive failure
                await asyncio.sleep(2 ** attempt)

        # If loop finishes without returning/raising
        logger.error(f"Failed to extract JSON after {self.retry_attempts} attempts. Last error: {last_error}")
        return None # Indicate definitive failure