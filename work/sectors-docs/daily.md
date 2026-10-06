> ## Documentation Index
> Fetch the complete documentation index at: https://docs.sectors.app/llms.txt
> Use this file to discover all available pages before exploring further.

# Daily Transaction Data

> Returns daily close price, volume, and market cap for a given IDX symbol over a date range of up to 90 days.

<Note>IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BBCA`, `GOTO`, `TLKM`.</Note>

<Note>Date range: defaults to last 30 days. Max window 90 days; wider ranges are clamped to the most recent 90 days ending at `end`. Future `end` dates return 400.</Note>

<Info>Costs 1 API credit.</Info>



## OpenAPI

````yaml GET /v2/daily/{symbol}/
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
  /v2/daily/{symbol}/:
    get:
      tags:
        - Transaction Data
      summary: Daily Transaction Data
      description: >-
        Returns daily close price, volume, and market cap for a given IDX symbol
        over a date range of up to 90 days.


        <Note>IDX symbol: 4 letters, optionally followed by `.jk`
        (case-insensitive). E.g. `BBCA`, `GOTO`, `TLKM`.</Note>


        <Note>Date range: defaults to last 30 days. Max window 90 days; wider
        ranges are clamped to the most recent 90 days ending at `end`. Future
        `end` dates return 400.</Note>


        <Info>Costs 1 API credit.</Info>
      operationId: daily_retrieve
      parameters:
        - in: path
          name: symbol
          schema:
            type: string
          description: IDX symbol. E.g. `BBCA`, `GOTO`, `TLKM`.
          required: true
          examples:
            Example:
              value: BBCA
        - in: query
          name: start
          schema:
            type: string
          description: >-
            Start date in `YYYY-MM-DD` format. Defaults to 30 days before `end`.
            Wider ranges are clamped to the most recent 90 days.
          examples:
            Example:
              value: '2025-05-01'
          x-max-days: 90
        - in: query
          name: end
          schema:
            type: string
          description: >-
            End date in `YYYY-MM-DD` format. Defaults to today. Future dates
            return 400.
          examples:
            Example:
              value: '2025-05-14'
      responses:
        '200':
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/DailyDataItem'
              examples:
                DailyData:
                  value:
                    - symbol: BBCA.JK
                      date: '2025-05-02'
                      close: 8975
                      open: 9000
                      high: 9000
                      low: 8850
                      volume: 92219000
                      market_cap: 1095329638012500
                  summary: Daily data
                  x-example-request:
                    method: GET
                    path: /v2/daily/{symbol}/
                    url: >-
                      https://api.sectors.app/v2/daily/BBCA/?start=2025-05-02&end=2025-05-02
                    path_params:
                      symbol: BBCA
                    query:
                      start: '2025-05-02'
                      end: '2025-05-02'
          description: Array of daily transaction records.
        '400':
          content:
            application/json:
              schema:
                type: object
                additionalProperties: {}
              examples:
                InvalidFormat:
                  value:
                    error: Use a valid date format of YYYY-MM-DD.
                  summary: Invalid format
          description: Invalid request (bad date format).
        '404':
          content:
            application/json:
              schema:
                type: object
                additionalProperties: {}
              examples:
                NotFound:
                  value:
                    error: Given stock symbol 'ZZZZ' does not exist.
          description: >-
            Symbol not found — the ticker does not exist in the daily dataset.
            (A valid ticker with no rows in the requested window returns 200
            with an empty list.)
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
    DailyDataItem:
      type: object
      properties:
        symbol:
          type: string
          description: Ticker symbol.
        date:
          type: string
          format: date
          description: Trading date.
        close:
          type: integer
          description: Closing price in IDR.
        open:
          type: integer
          nullable: true
          description: Opening price in IDR.
        high:
          type: integer
          nullable: true
          description: Intraday high in IDR.
        low:
          type: integer
          nullable: true
          description: Intraday low in IDR.
        volume:
          type: integer
          description: Trading volume (shares).
        market_cap:
          type: integer
          description: Market cap in IDR.
      required:
        - close
        - date
        - high
        - low
        - market_cap
        - open
        - symbol
        - volume
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: Authorization
      description: Global API Key Authorization

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.