> ## Documentation Index
> Fetch the complete documentation index at: https://docs.sectors.app/llms.txt
> Use this file to discover all available pages before exploring further.

# Corporate Actions

> <Note>IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BBCA`, `BMRI`, `TLKM`.</Note>

Returns all corporate action history for a given IDX-listed company: stock splits, right issues, warrants, bonus shares, AGM events, upcoming dividends, and historical dividends.

<Note>For every company's actions in a date window, see the market-wide [Corporate Actions Calendar](https://docs.sectors.app/api-references/v2/indonesia/news/corporate-actions).</Note>

<Info>Costs 1 API credit.</Info>



## OpenAPI

````yaml GET /v2/company/corporate-actions/{symbol}/
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
  /v2/company/corporate-actions/{symbol}/:
    get:
      tags:
        - Detailed Reports
      summary: Corporate Actions
      description: >-
        <Note>IDX symbol: 4 letters, optionally followed by `.jk`
        (case-insensitive). E.g. `BBCA`, `BMRI`, `TLKM`.</Note>


        Returns all corporate action history for a given IDX-listed company:
        stock splits, right issues, warrants, bonus shares, AGM events, upcoming
        dividends, and historical dividends.


        <Note>For every company's actions in a date window, see the market-wide
        [Corporate Actions
        Calendar](https://docs.sectors.app/api-references/v2/indonesia/news/corporate-actions).</Note>


        <Info>Costs 1 API credit.</Info>
      operationId: company_corporate_actions_retrieve
      parameters:
        - in: path
          name: symbol
          schema:
            type: string
          description: IDX symbol. E.g. `BBCA`, `BMRI`.
          required: true
          examples:
            Example:
              value: BBCA
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CorporateActionsResponse'
              examples:
                BBCACorporateActions:
                  value:
                    symbol: BBCA.JK
                    corporate_actions:
                      agm:
                        - agm_date: '2025-03-12'
                          agm_time: '09:30:00'
                          agm_place: >-
                            Menara Bca, Grand Indonesia, Jl. M. H. Thamrin No.
                            1, Jakarta 10310 Kota Adm. Jakarta Pusat
                          agm_result: null
                      bonus: null
                      warrant: null
                      dividend:
                        - ex_date: '2025-12-03'
                          payment_date: '2025-12-22'
                          dividend_yield: 0.00641717
                          dividend_amount: 55
                      right_issue: null
                      stock_split:
                        - date: '2021-10-13'
                          split_ratio: 5
                      upcoming_dividend: null
                  summary: BBCA Corporate Actions
                  x-example-request:
                    method: GET
                    path: /v2/company/corporate-actions/{symbol}/
                    url: https://api.sectors.app/v2/company/corporate-actions/BBCA/
                    path_params:
                      symbol: BBCA
          description: Corporate actions grouped by type.
        '404':
          content:
            application/json:
              schema:
                type: object
                additionalProperties: {}
              examples:
                NotFound:
                  value:
                    error: No data found for symbol 'XYZA'.
          description: Symbol not found.
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
    CorporateActionsResponse:
      type: object
      properties:
        symbol:
          type: string
          description: IDX ticker symbol (with `.JK` suffix).
        corporate_actions:
          $ref: '#/components/schemas/CorporateActionsByType'
      required:
        - corporate_actions
        - symbol
    CorporateActionsByType:
      type: object
      properties:
        dividend:
          type: array
          items: {}
          description: Historical dividend events.
        upcoming_dividend:
          type: array
          items: {}
          description: Dividends announced but not yet paid.
        stock_split:
          type: array
          items: {}
          description: Stock split events.
        right_issue:
          type: array
          items: {}
          description: Rights issue events.
        warrant:
          type: array
          items: {}
          description: Warrant issuance events.
        bonus:
          type: array
          items: {}
          description: Bonus share events.
        agm:
          type: array
          items: {}
          description: Annual general meeting events.
      required:
        - agm
        - bonus
        - dividend
        - right_issue
        - stock_split
        - upcoming_dividend
        - warrant
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: Authorization
      description: Global API Key Authorization

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.