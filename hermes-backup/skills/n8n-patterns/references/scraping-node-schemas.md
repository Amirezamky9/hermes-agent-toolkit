# MCP-Verified Node Schemas: Scraping & Research

> Ground truth from `mcp_n8n_mcp_get_node_types` during session 2026-07-09.
> For builder sessions constructing scrape workflows — skip re-fetching.

## HTTP Request (n8n-nodes-base.httpRequest) v4.3

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `method` | GET/POST/PUT/etc | GET | — |
| `url` | string (expr) | — | REQUIRED |
| `authentication` | none / predefinedCredentialType / genericCredentialType | none | — |
| `genericAuthType` | httpBasicAuth / httpBearerAuth / httpDigestAuth / httpHeaderAuth / httpQueryAuth / httpCustomAuth / oAuth1Api / oAuth2Api | — | Only if auth=genericCredentialType |
| `sendQuery` | bool | false | Enable query params |
| `specifyQuery` | keypair / json | keypair | — |
| `queryParameters` | [{name, value}] | — | NEVER put static credentials here |
| `sendHeaders` | bool | false | — |
| `headerParameters` | [{name, value}] | — | NEVER put static auth here |
| `sendBody` | bool | false | — |
| `contentType` | json / form-urlencoded / multipart-form-data / binaryData / raw | json | — |

### Pagination (options.pagination)

| Field | Type | Default |
|-------|------|---------|
| `paginationMode` | off / updateAParameterInEachRequest / responseContainsNextURL | updateAParameterInEachRequest |
| `nextURL` | expr | — | For responseContainsNextURL mode |
| `parameters` | [{type: qs/body/headers, name, value}] | — | For updateAParameterInEachRequest |
| `paginationCompleteWhen` | responseIsEmpty / receiveSpecificStatusCodes / other | responseIsEmpty |
| `requestInterval` | number (ms) | 0 |
| `maxRequests` | number | 100 |

### Batching (options.batching)

| Field | Type | Default |
|-------|------|---------|
| `batchSize` | number | 50 |
| `batchInterval` | number (ms) | 1000 |

### Response Options

| Field | Type | Default |
|-------|------|---------|
| `fullResponse` | bool | false |
| `neverError` | bool | false |
| `responseFormat` | autodetect / file / json / text | autodetect |
| `timeout` | number (ms) | 10000 |

## HTML (n8n-nodes-base.html) v1.2 — extractHtmlContent

| Field | Type | Default |
|-------|------|---------|
| `operation` | generateHtmlTemplate / extractHtmlContent / convertToHtmlTable | — |
| `sourceData` | binary / json | json |
| `extractionValues[].key` | string | — | Output key |
| `extractionValues[].cssSelector` | string | — | CSS selector |
| `extractionValues[].returnValue` | text / html / attribute / value | text |
| `extractionValues[].attribute` | string | — | Only if returnValue=attribute |
| `extractionValues[].returnArray` | bool | false |
| options.trimValues | bool | true |
| options.cleanUpText | bool | true |

## RSS Feed Read (n8n-nodes-base.rssFeedRead) v1.2

| Field | Type | Default |
|-------|------|---------|
| `url` | string (expr) | REQUIRED |
| options.customFields | string (comma-separated) | — |
| options.ignoreSSL | bool | false |

## Code (n8n-nodes-base.code) v2

| Field | Type | Default |
|-------|------|---------|
| `mode` | runOnceForAllItems / runOnceForEachItem | — |
| `language` | javaScript / pythonNative | javaScript |
| `jsCode` / `pythonCode` | string | — |

🚫 **Sandbox has NO network access.** fetch(), axios, XMLHttpRequest, requests, urllib all FAIL.

## Split In Batches (n8n-nodes-base.splitInBatches) v2

| Field | Type | Default |
|-------|------|---------|
| `batchSize` | number | 10 |
| options.reset | bool | false |

Output 0 = Done. Output 1 = Continue (loop back).

## Information Extractor (@n8n/n8n-nodes-langchain.informationExtractor) v1.2

Requires subnode `model` (LanguageModel).

| Field | Type | Default |
|-------|------|---------|
| `text` | string (expr) | — | The text to extract from |
| `schemaType` | fromAttributes / fromJson / manual | fromAttributes |
| `attributes[].name` | string | — |
| `attributes[].type` | string / number / boolean / date | string |
| `attributes[].description` | string | — | Helps LLM |
| `attributes[].required` | bool | false |
| options.batching.batchSize | number | 5 |
| options.batching.delayBetweenBatches | number (ms) | 0 |

## Error Trigger (n8n-nodes-base.errorTrigger) v1

No params. Just a trigger node. Wires to a separate error-handling workflow.

## RSS Feed Trigger (n8n-nodes-base.rssFeedReadTrigger) v1

No special params — standard trigger. Fires on RSS feed update.

## Apify MCP (@n8n/mcp-registry.apify) v1.1

For AI Agent tool wiring. No discriminators. Use `tool({ type: '@n8n/mcp-registry.apify' })` in SDK.

## Webpage Content Extractor (n8n-nodes-webpage-content-extractor.webpageContentExtractor) v1

No params — feed it a URL via upstream node. Extracts main content (Reader-mode style).

## Perplexity (n8n-nodes-base.perplexity) v2

| Resource | Operation | Notes |
|----------|-----------|-------|
| search | search | Raw web search results |
| chat | complete | Sonar models + built-in search |
| agent | createResponse | Agent API with 3rd-party models |
| embedding | createEmbedding / createContextualized | Vector embeddings |

## Extract from File (n8n-nodes-base.extractFromFile) v1.1

| Operation | Parses |
|-----------|--------|
| csv | CSV |
| html | HTML table |
| pdf | PDF content + metadata |
| xml | XML |
| fromJson | JSON |
| text | plain text |
| ics | calendar |
| ods/xls/xlsx | spreadsheets |
| rtf | rich text |
| binaryToPropery | base64 |

## icons

- 🚫 = feature not available / forbidden
- ⚠️ = watch out
- ✅ = supported
