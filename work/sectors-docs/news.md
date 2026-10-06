> ## Documentation Index
> Fetch the complete documentation index at: https://docs.sectors.app/llms.txt
> Use this file to discover all available pages before exploring further.

# News Articles

> Returns paginated news articles from either the IDX (Indonesian Stock Exchange) or mining news sources. Use the `extension` parameter to choose the data source — each extension has its own set of valid filter parameters.

<Warning>Mixing IDX and mining parameters will return a 400 error. E.g. passing `sector` with `extension=mining` is invalid.</Warning>

<Accordion title="IDX Extension Parameters (extension=idx)">
- **sector**: Comma-separated sector slugs (kebab-case). Get values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint.
- **sub_sector**: Comma-separated subsector slugs (kebab-case). E.g. `banks`, `insurance`, `retailing`. Get valid values from the [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors) endpoint.
- **tags**: Comma-separated tag slugs. Get values from the [News Tags](https://docs.sectors.app/api-references/v2/indonesia/helper-list/tags) endpoint.
- **symbols**: Comma-separated IDX symbols. E.g. `BBCA,BBRI,BMRI`.
- **keyword**: Case-insensitive substring match on article title.
</Accordion>

<Accordion title="Mining Extension Parameters (extension=mining)">
- **keyword**: Case-insensitive substring match on article title.
- **commodity_type**: Filter by commodity. E.g. `Coal`, `Nickel`, `Gold`.
</Accordion>

<Note>Date filters: both `start` and `end` are independent and optional — omit either side to leave that bound unconstrained. Future `end` dates return 400.</Note>

<Info>Costs 1 API credit.</Info>



## OpenAPI

````yaml GET /v2/news/
openapi: 3.0.3
info:
  title: Sectors API
  version: 2.0.0
  x-tagGroups:
    - name: Indonesia (IDX)
      x-sidebar-icon: building-columns
      tags:
        - Company Screener
        - Helper Lists
        - Detailed Reports
        - Transaction Data
        - Rankings
        - IPO & Performance
        - News & Filings
        - Brokers
    - name: Singapore (SGX)
      x-sidebar-icon: building
      tags:
        - SGX - Company Screener
        - SGX - Helper Lists
        - SGX - Detailed Reports
        - SGX - Transaction Data
        - SGX - Rankings
        - SGX - News & Filings
    - name: Malaysia (KLSE)
      x-sidebar-icon: landmark
      tags:
        - KLSE
    - name: Mining (Extension)
      x-sidebar-icon: gem
      tags:
        - Companies
        - Commodities & Trade
        - Production & Sites
        - Contracts & Licenses
  description: >-
    Financial data API for IDX, SGX, and KLSE listed companies, including mining
    sector data.


    ## Billing & Credits


    Credits/quota are consumed as a function of the HTTP response status, so the
    same status always bills the same way:


    | Response | Consumes credits? |

    |---|---|

    | **2xx** (success) | Yes — the endpoint's stated cost (most cost 1;
    multi-section reports, multi-classification rankings, and some feeds cost
    more, as noted on each endpoint). |

    | **404** (addressed resource not found) | Yes — 1 credit. Your request was
    well-formed and we ran the lookup, but the specific resource you addressed
    doesn't exist (e.g. an unknown `symbol`/`slug`). You are billed for the
    lookup, not the result. |

    | **400** (bad request) | No — free. Malformed input (missing/invalid
    parameters, unknown sections, bad date formats, invalid slugs) is rejected
    before any lookup runs. |

    | **401 / 403** (auth) | No — free. |

    | **429** (rate limit / quota exhausted) | No — free. |

    | **5xx** (server error) | No — free. A failure on our side is never billed.
    |


    ### Empty results


    **List and filter endpoints return `200` with an empty result when nothing
    matches** — an empty collection is a valid answer, not an error. For
    example, a screener/ranking whose filters match no companies returns `200`
    with empty arrays (and a `message` explaining why), and a date-range feed
    with no rows in the window returns `200` with an empty list. These still
    consume credits (the query ran). A `404` is reserved for when the **specific
    resource you addressed** (a `symbol`, `slug`, `index_code`, etc.) does not
    exist at all.


    **One exception:** the Company Screener endpoints charge **1 credit on a
    `400`** *only* when using the natural-language `?q=` parameter and the
    failure occurs after the query has been sent to the language model (e.g. an
    untranslatable query). This recovers the model cost already incurred. A
    `400` from a structured (`where` / `order_by`) query, or any validation
    failure before the model runs, is free. A successful `?q=` screen costs 3
    credits; a successful structured screen costs 1.
servers:
  - url: https://api.sectors.app
    description: Production Server
security:
  - ApiKeyAuth: []
tags:
  - name: Company Screener
    description: >-
      Filter and screen IDX-listed companies with SQL-like or natural language
      queries
    x-sidebar-icon: bolt
  - name: Detailed Reports
    description: >-
      Company reports, revenue segments, quarterly financials, and subsector
      reports
    x-sidebar-icon: file-contract
  - name: Transaction Data
    description: Daily transaction data, IDX market summary, and index data
    x-sidebar-icon: money-bill-transfer
  - name: Rankings
    description: Most traded stocks and top company movers
    x-sidebar-icon: ranking-star
  - name: IPO & Performance
    description: IPO listing performance for IDX companies
    x-sidebar-icon: chart-line
  - name: News & Filings
    description: News articles, company filings, and stock suspensions
    x-sidebar-icon: newspaper
  - name: Brokers
    description: >-
      IDX broker activity: per-broker daily trades, top buyers/sellers by
      symbol, top accumulations/distributions by broker, foreign vs domestic
      flow, and the curated broker registry
    x-sidebar-icon: user-tie
  - name: Helper Lists
    description: >-
      Reference lists: industries, subsectors, revenue segments, quarterly
      dates, tags, and the investors / conglomerates directory
    x-sidebar-icon: list-check
  - name: SGX - Company Screener
    description: >-
      Filter and screen SGX-listed companies with SQL-like or natural language
      queries
    x-sidebar-icon: bolt
  - name: SGX - Detailed Reports
    description: Singapore Stock Exchange full company reports
    x-sidebar-icon: file-contract
  - name: SGX - Transaction Data
    description: SGX daily price/volume, short-sell activity, and share buybacks
    x-sidebar-icon: money-bill-transfer
  - name: SGX - Rankings
    description: Top SGX companies by classification
    x-sidebar-icon: ranking-star
  - name: SGX - News & Filings
    description: SGX news articles and insider filings
    x-sidebar-icon: newspaper
  - name: SGX - Helper Lists
    description: 'SGX reference lists: sectors, company directory, news tag vocabulary'
    x-sidebar-icon: list-check
  - name: KLSE
    description: Malaysia Stock Exchange — companies, sectors, and rankings
    x-sidebar-icon: landmark
  - name: Companies
    description: Mining company search, detail, financials, ownership, and performance
    x-sidebar-icon: industry
  - name: Commodities & Trade
    description: >-
      Commodity prices, export destinations, global commodity data, and sales
      destinations
    x-sidebar-icon: truck
  - name: Production & Sites
    description: >-
      Total commodity production, national resources and reserves, and mining
      sites
    x-sidebar-icon: hammer
  - name: Contracts & Licenses
    description: Mining contracts, licenses, and auction data
    x-sidebar-icon: file-signature
paths:
  /v2/news/:
    get:
      tags:
        - News & Filings
      summary: News Articles
      description: >-
        Returns paginated news articles from either the IDX (Indonesian Stock
        Exchange) or mining news sources. Use the `extension` parameter to
        choose the data source — each extension has its own set of valid filter
        parameters.


        <Warning>Mixing IDX and mining parameters will return a 400 error. E.g.
        passing `sector` with `extension=mining` is invalid.</Warning>


        <Accordion title="IDX Extension Parameters (extension=idx)">

        - **sector**: Comma-separated sector slugs (kebab-case). Get values from
        the
        [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors)
        endpoint.

        - **sub_sector**: Comma-separated subsector slugs (kebab-case). E.g.
        `banks`, `insurance`, `retailing`. Get valid values from the
        [Subsectors](https://docs.sectors.app/api-references/v2/indonesia/helper-list/subsectors)
        endpoint.

        - **tags**: Comma-separated tag slugs. Get values from the [News
        Tags](https://docs.sectors.app/api-references/v2/indonesia/helper-list/tags)
        endpoint.

        - **symbols**: Comma-separated IDX symbols. E.g. `BBCA,BBRI,BMRI`.

        - **keyword**: Case-insensitive substring match on article title.

        </Accordion>


        <Accordion title="Mining Extension Parameters (extension=mining)">

        - **keyword**: Case-insensitive substring match on article title.

        - **commodity_type**: Filter by commodity. E.g. `Coal`, `Nickel`,
        `Gold`.

        </Accordion>


        <Note>Date filters: both `start` and `end` are independent and optional
        — omit either side to leave that bound unconstrained. Future `end` dates
        return 400.</Note>


        <Info>Costs 1 API credit.</Info>
      operationId: news_retrieve
      parameters:
        - in: query
          name: sector
          schema:
            type: string
          description: '**IDX only.** Comma-separated sector slugs (kebab-case).'
          examples:
            Example:
              value: financials
        - in: query
          name: sub_sector
          schema:
            type: string
          description: '**IDX only.** Comma-separated subsector slugs (kebab-case).'
          examples:
            Example:
              value: banks
        - in: query
          name: commodity_type
          schema:
            type: string
            enum:
              - Bauxite
              - Coal
              - Copper
              - Gold
              - Iron
              - Nickel
              - Non-Metallic Mineral
              - Sand, Stone, Gravel
              - Tin
          description: '**Mining only.** Filter by commodity type. E.g. `Coal`, `Nickel`.'
          examples:
            Example:
              value: Coal
        - in: query
          name: start
          schema:
            type: string
          description: >-
            Start date in `YYYY-MM-DD` format. Optional; if omitted, no lower
            bound is applied. Filters on `timestamp`.
          examples:
            Example:
              value: '2025-05-01'
        - in: query
          name: end
          schema:
            type: string
          description: >-
            End date in `YYYY-MM-DD` format. Optional; if omitted, no upper
            bound is applied. Future dates return 400.
          examples:
            Example:
              value: '2025-05-14'
        - in: query
          name: limit
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 30
          description: Items per page. Max 30.
          examples:
            Example:
              value: 20
        - in: query
          name: offset
          schema:
            type: integer
            default: 0
            minimum: 0
          description: Items to skip for pagination.
          examples:
            Example:
              value: 0
        - in: query
          name: tags
          schema:
            type: string
          description: >-
            **IDX only.** Comma-separated tag slugs. Get valid values from the
            [News
            Tags](https://docs.sectors.app/api-references/v2/indonesia/helper-list/tags)
            endpoint.
          examples:
            Example:
              value: Bullish
        - in: query
          name: extension
          schema:
            type: string
            enum:
              - idx
              - mining
            default: idx
          description: Data source. Default `idx`.
          examples:
            Example:
              value: idx
        - in: query
          name: keyword
          schema:
            type: string
          description: >-
            Case-insensitive substring match on article title. Works for both
            IDX and mining.
          examples:
            Example:
              value: dividend
        - in: query
          name: symbols
          schema:
            type: string
          description: '**IDX only.** Comma-separated IDX symbols. E.g. `BBCA,BBRI`.'
          examples:
            Example:
              value: BBCA,BBRI
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NewsArticleList'
              examples:
                IDXNewsResponse:
                  value:
                    results:
                      - title: >-
                          OJK says Henry Surya's false statements delayed the
                          investigation into PT Asuransi Jiwa Prolife Indonesia
                          fraud case
                        body: >-
                          The Financial Services Authority (OJK) said Henry
                          Surya's lies prolonged the probe of a fraud at PT
                          Asuransi Jiwa Prolife Indonesia. Surya is the sole
                          suspect for embezzling roughly Rp 500 billion of
                          customer funds, of which Rp 300 billion was used
                          personally. OJK investigators have seized 485 pieces
                          of evidence worth Rp 113.97 billion, including three
                          shops, a house in Medan and cash. Surya, already
                          serving an 18‑year prison term for another case, will
                          face trial for this fraud after his conditional
                          release.
                        source: >-
                          https://money.kompas.com/read/2026/07/09/180504926/ojk-sebut-kebohongan-henry-surya-buat-pengusutan-kasus-indosurya-makan-waktu
                        thumbnail: >-
                          https://asset.kompas.com/crops/qceDuDkratLeHCXO28fC2iGFTys=/0x0:0x0/230x152/data/photo/2026/07/09/6a4f38026d694.jpg
                        timestamp: '2026-07-09T18:05:00'
                        sector: financials
                        sub_sector:
                          - insurance
                        tags:
                          - Violation
                          - Risk & Compliance
                          - Politics & Regulation
                          - Bearish
                        symbols: []
                        dimension:
                          future: 0
                          dividend: 0
                          ownership: 0
                          technical: 0
                          valuation: 0
                          financials: 0
                          management: 0
                          sustainability: 0
                    pagination:
                      total_count: 8665
                      showing: 1
                      limit: 2
                      offset: 0
                      has_next: true
                      has_previous: false
                      next_offset: 2
                      previous_offset: null
                  summary: IDX news response
                  x-example-request:
                    method: GET
                    path: /v2/news/
                    url: https://api.sectors.app/v2/news/?limit=2
                    query:
                      limit: 2
          description: Paginated list of news articles.
        '400':
          content:
            application/json:
              schema:
                type: object
                additionalProperties: {}
              examples:
                WrongExtensionParams:
                  value:
                    error: >-
                      Parameter(s) [sector] are not valid for extension=mining.
                      Valid params: ['commodity_type', 'end', 'keyword',
                      'limit', 'offset', 'start'].
                  summary: Wrong extension params
                InvalidDateFormat:
                  value:
                    error: >-
                      Use a valid date format of YYYY-MM-DD for 'start' and
                      'end'.
                  summary: Invalid date format
          description: Invalid parameters.
        '429':
          content:
            application/json:
              schema:
                type: object
                additionalProperties: {}
              examples:
                RateLimit:
                  value:
                    error: RATE_LIMIT_EXCEEDED
                    message: Rate limit exceeded. Consider upgrading.
          description: Rate limit exceeded.
components:
  schemas:
    NewsArticleList:
      type: object
      properties:
        results:
          type: array
          items:
            $ref: '#/components/schemas/NewsArticleListItem'
        pagination:
          $ref: '#/components/schemas/NewsArticleListPagination'
      required:
        - pagination
        - results
    NewsArticleListItem:
      type: object
      properties:
        title:
          type: string
          description: Article headline.
        body:
          type: string
          description: Article body text (IDX only).
        source:
          type: string
          description: Source URL.
        timestamp:
          type: string
          description: Article publication timestamp.
        sector:
          type: string
          description: Sector slug (IDX only).
        sub_sector:
          type: array
          items:
            type: string
          description: Subsector slugs (IDX only).
        tags:
          type: array
          items:
            type: string
          description: Tag slugs (IDX only).
        symbols:
          type: array
          items:
            type: string
          description: Related IDX symbols (IDX only).
        thumbnail:
          type: string
          nullable: true
          description: Thumbnail image URL (IDX only).
        dimension:
          nullable: true
          description: News dimension scores as a structured object (IDX only).
        commodity_type:
          type: array
          items:
            type: string
          description: Commodity types (mining only).
      required:
        - source
        - timestamp
        - title
    NewsArticleListPagination:
      type: object
      properties:
        total_count:
          type: integer
          description: Total number of matching results.
        showing:
          type: integer
          description: Number of results in this page.
        limit:
          type: integer
          description: Maximum results per page.
        offset:
          type: integer
          description: Number of results skipped.
        has_next:
          type: boolean
          description: Whether a next page exists.
        has_previous:
          type: boolean
          description: Whether a previous page exists.
        next_offset:
          type: integer
          nullable: true
          description: Offset for the next page, or null.
        previous_offset:
          type: integer
          nullable: true
          description: Offset for the previous page, or null.
      required:
        - has_next
        - has_previous
        - limit
        - next_offset
        - offset
        - previous_offset
        - showing
        - total_count
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: Authorization
      description: Global API Key Authorization

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.