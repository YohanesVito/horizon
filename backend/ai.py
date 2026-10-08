"""Server-only OpenAI structured output helper; no requests happen on import."""
import json
import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import dotenv_values
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'gpt-6-luna'
RESPONSES_URL = 'https://api.openai.com/v1/responses'


class AIError(RuntimeError):
    """Safe error for callers; never includes keys, prompts or provider bodies."""


def _api_key() -> str:
    # Read only AI_KEY; do not import database configuration or mutate os.environ.
    value = os.getenv('AI_KEY')
    if value is None:
        for filename in ('.env.local', '.env'):
            value = dotenv_values(ROOT / filename).get('AI_KEY')
            if value is not None:
                break
    if not value or not value.strip():
        raise AIError('Set AI_KEY in the server environment, .env.local or .env.')
    return value.strip()


async def generate_structured(
    prompt: str,
    schema: dict[str, Any],
    *,
    instructions: str | None = None,
    max_output_tokens: int = 4096,
) -> dict[str, Any]:
    """Return a validated JSON object using GPT-6 Luna.

    Supply an OpenAI-compatible strict JSON schema (all object fields required,
    additionalProperties=false). Refusals, incomplete output and API failures
    raise AIError. Invalid caller inputs raise ValueError before any request.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError('prompt must be a non-empty string.')
    if not isinstance(schema, dict) or schema.get('type') != 'object':
        raise ValueError('schema must describe a JSON object.')
    try:
        Draft202012Validator.check_schema(schema)
        json.dumps(schema, allow_nan=False)
    except (SchemaError, TypeError, ValueError):
        raise ValueError('schema must be a valid JSON Schema.') from None
    if type(max_output_tokens) is not int or max_output_tokens < 1:
        raise ValueError('max_output_tokens must be a positive integer.')
    if instructions is not None and not isinstance(instructions, str):
        raise ValueError('instructions must be a string.')

    payload = {
        'model': MODEL,
        'input': prompt,
        'store': False,
        'max_output_tokens': max_output_tokens,
        'text': {'format': {
            'type': 'json_schema', 'name': 'result',
            'schema': schema, 'strict': True,
        }},
    }
    if instructions is not None:
        payload['instructions'] = instructions
    key = _api_key()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                RESPONSES_URL, json=payload,
                headers={'Authorization': f'Bearer {key}'},
            )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise AIError(f'OpenAI request failed (HTTP {exc.response.status_code}).') from None
    except httpx.RequestError:
        raise AIError('OpenAI request failed or timed out.') from None

    try:
        body = response.json()
        if body.get('status') != 'completed':
            raise AIError('OpenAI response did not complete; no result returned.')
        texts = []
        for item in body['output']:
            if item.get('type') != 'message':
                continue
            for part in item['content']:
                if part.get('type') == 'refusal':
                    raise AIError('OpenAI refused the request.')
                if part.get('type') == 'output_text':
                    texts.append(part['text'])
        if not texts:
            raise AIError('OpenAI returned no structured output.')
        result = json.loads(''.join(texts))
        Draft202012Validator(schema).validate(result)
        return result
    except (ValueError, KeyError, TypeError, AttributeError, ValidationError):
        raise AIError('OpenAI returned invalid structured output.') from None
