"""Small allowlisted Sectors MCP client for sourced news context."""
import json
import httpx

URL = 'https://sectors-mcp.supertype.ai/mcp'


class NewsClient:
    def __init__(self, client, key):
        self.client = client
        self.headers = {'Authorization': f'Bearer {key.strip()}', 'Accept': 'application/json, text/event-stream'}
        self.sequence = 0

    async def request(self, method, params=None, notification=False):
        self.sequence += 1
        body = {'jsonrpc': '2.0', 'method': method}
        if not notification:
            body['id'] = self.sequence
        if params is not None:
            body['params'] = params
        response = await self.client.post(URL, headers=self.headers, json=body)
        response.raise_for_status()
        if response.headers.get('mcp-session-id'):
            self.headers['Mcp-Session-Id'] = response.headers['mcp-session-id']
        if notification:
            return None
        if 'text/event-stream' in response.headers.get('content-type', ''):
            messages = []
            for block in response.text.replace('\r\n', '\n').split('\n\n'):
                data = '\n'.join(line[5:].lstrip() for line in block.splitlines() if line.startswith('data:'))
                if data:
                    messages.append(json.loads(data))
            result = next((m for m in messages if m.get('id') == body['id']), None)
        else:
            result = response.json()
        if not isinstance(result, dict) or result.get('id') != body['id'] or 'error' in result:
            raise ValueError('Invalid MCP response.')
        return result['result']

    async def initialize(self):
        result = await self.request('initialize', {'protocolVersion': '2025-03-26', 'capabilities': {},
                                    'clientInfo': {'name': 'horizon-insights', 'version': '1'}})
        self.headers['MCP-Protocol-Version'] = result['protocolVersion']
        await self.request('notifications/initialized', notification=True)

    async def news(self, symbol, start, end):
        result = await self.request('tools/call', {'name': 'fetch-news', 'arguments': {
            'symbols': symbol, 'extension': 'idx', 'start': start, 'end': end, 'limit': 3, 'offset': 0}})
        if result.get('isError'):
            raise ValueError('Sectors news unavailable.')
        structured = result.get('structuredContent')
        if structured is None:
            texts = [item['text'] for item in result.get('content', []) if item.get('type') == 'text']
            structured = json.loads('\n'.join(texts))
        if not isinstance(structured, dict):
            raise ValueError('Invalid news response.')
        # MCP tools may wrap the official response in a data field.
        if 'results' not in structured and isinstance(structured.get('data'), dict):
            structured = structured['data']
        return structured['results']
