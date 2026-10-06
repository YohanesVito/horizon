> ## Documentation Index
> Fetch the complete documentation index at: https://docs.sectors.app/llms.txt
> Use this file to discover all available pages before exploring further.

# Corporate Actions Calendar

> Corporate actions across every IDX ticker in a date window, grouped by type: the market-wide counterpart of the per-symbol [Corporate Actions](https://docs.sectors.app/api-references/v2/indonesia/company/corporate-actions) endpoint. Row keys match the per-symbol endpoint. `start`/`end` filter (and sort) each type on one key: `dividend`, `upcoming_dividend`, `bonus` and `right_issue` on `ex_date`, `stock_split` on `date` (its ex-date), `warrant` on `trading_period_start`, and `agm` on `agm_date`; ties sort by `symbol`.

<Note>`end` may be in the future, so the window works as a calendar. Default window: today - 30 days to today + 30 days. Wider ranges are clamped to the 90 days ending at `end`.</Note>

<Note>Only the requested `type` keys are present in the response.</Note>

<Info>Costs 1 API credit per requested type. Default (all 7 types) consumes 7 credits.</Info>



## OpenAPI

````yaml GET /v2/corporate-actions/
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
  /v2/corporate-actions/:
    get:
      tags:
        - News & Filings
      summary: Corporate Actions Calendar
      description: >-
        Corporate actions across every IDX ticker in a date window, grouped by
        type: the market-wide counterpart of the per-symbol [Corporate
        Actions](https://docs.sectors.app/api-references/v2/indonesia/company/corporate-actions)
        endpoint. Row keys match the per-symbol endpoint. `start`/`end` filter
        (and sort) each type on one key: `dividend`, `upcoming_dividend`,
        `bonus` and `right_issue` on `ex_date`, `stock_split` on `date` (its
        ex-date), `warrant` on `trading_period_start`, and `agm` on `agm_date`;
        ties sort by `symbol`.


        <Note>`end` may be in the future, so the window works as a calendar.
        Default window: today - 30 days to today + 30 days. Wider ranges are
        clamped to the 90 days ending at `end`.</Note>


        <Note>Only the requested `type` keys are present in the response.</Note>


        <Info>Costs 1 API credit per requested type. Default (all 7 types)
        consumes 7 credits.</Info>
      operationId: corporate_actions_retrieve
      parameters:
        - in: query
          name: start
          schema:
            type: string
          description: 'Start date (YYYY-MM-DD). Default: end - 30 days.'
          examples:
            Example:
              value: '2025-05-01'
          x-max-days: 90
        - in: query
          name: end
          schema:
            type: string
          description: >-
            End date (YYYY-MM-DD); may be in the future. Default: today + 30
            days.
          examples:
            Example:
              value: '2025-05-31'
        - in: query
          name: type
          schema:
            type: array
            items:
              type: string
              enum:
                - agm
                - bonus
                - dividend
                - right_issue
                - stock_split
                - upcoming_dividend
                - warrant
          description: 'Comma-separated action types. Default: all.'
          examples:
            Example:
              value: dividend,stock_split
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CorporateActionsCalendarResponse'
              examples:
                CorporateActionsCalendar:
                  value:
                    start: '2025-07-01'
                    end: '2025-07-31'
                    dividend:
                      - symbol: BBMD.JK
                        ex_date: '2025-07-01'
                        cum_date: '2025-06-30'
                        recording_date: '2025-07-02'
                        payment_date: '2025-07-18'
                        dividend_amount: 34.25
                        dividend_yield: 0.0168784
                    stock_split:
                      - symbol: CUAN.JK
                        date: '2025-07-15'
                        cum_date: '2025-07-14'
                        recording_date: '2025-07-16'
                        split_ratio: 10
                        ratio: '1:10'
                    right_issue:
                      - symbol: WIFI.JK
                        ex_date: '2025-07-02'
                        cum_date: '2025-07-01'
                        recording_date: '2025-07-03'
                        trading_period_start: '2025-07-07'
                        trading_period_end: '2025-07-15'
                        subscription_date: '2025-07-03'
                        price: 2000
                        old_ratio: 4
                        new_ratio: 5
                    agm:
                      - symbol: DRMA.JK
                        agm_date: '2025-07-01'
                        recording_date: '2025-06-05'
                        agm_time: '14:00:00'
                        agm_place: >-
                          Pt Dharma Polimetal Tbk Jl. Angsana Raya Blok A9 No.
                          8, Delta Silicon 1, Cikarang 17550 Kotabekasi Jawa
                          Barat
                  summary: Corporate actions calendar
                  x-example-request:
                    method: GET
                    path: /v2/corporate-actions/
                    url: >-
                      https://api.sectors.app/v2/corporate-actions/?type=dividend%2Cstock_split%2Cright_issue%2Cagm&start=2025-07-01&end=2025-07-31
                    query:
                      type: dividend,stock_split,right_issue,agm
                      start: '2025-07-01'
                      end: '2025-07-31'
          description: >-
            Requested action types, each a list of rows sorted by date then
            symbol.
        '400':
          content:
            application/json:
              schema:
                type: object
                additionalProperties: {}
              examples:
                BadRequest:
                  value:
                    error: BAD_REQUEST
                    message: >-
                      Invalid type(s): foo. Valid types: dividend,
                      upcoming_dividend, stock_split, bonus, right_issue,
                      warrant, agm.
          description: Unknown type, invalid date, or start after end.
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
    CorporateActionsCalendarResponse:
      type: object
      properties:
        start:
          type: string
          format: date
        end:
          type: string
          format: date
        dividend:
          type: array
          items:
            $ref: '#/components/schemas/CorporateActionsDividendRow'
        upcoming_dividend:
          type: array
          items:
            $ref: '#/components/schemas/CorporateActionsUpcomingDividendRow'
        stock_split:
          type: array
          items:
            $ref: '#/components/schemas/CorporateActionsStockSplitRow'
        bonus:
          type: array
          items:
            $ref: '#/components/schemas/CorporateActionsBonusRow'
        right_issue:
          type: array
          items:
            $ref: '#/components/schemas/CorporateActionsRightIssueRow'
        warrant:
          type: array
          items:
            $ref: '#/components/schemas/CorporateActionsWarrantRow'
        agm:
          type: array
          items:
            $ref: '#/components/schemas/CorporateActionsAgmRow'
      required:
        - end
        - start
    CorporateActionsDividendRow:
      type: object
      properties:
        symbol:
          type: string
        ex_date:
          type: string
          format: date
          description: Ex-date.
        cum_date:
          type: string
          format: date
          nullable: true
        recording_date:
          type: string
          format: date
          nullable: true
        payment_date:
          type: string
          format: date
          nullable: true
        dividend_amount:
          type: number
          format: double
          nullable: true
        dividend_yield:
          type: number
          format: double
          nullable: true
      required:
        - cum_date
        - dividend_amount
        - dividend_yield
        - ex_date
        - payment_date
        - recording_date
        - symbol
    CorporateActionsUpcomingDividendRow:
      type: object
      properties:
        symbol:
          type: string
        ex_date:
          type: string
          format: date
          description: Ex-date.
        cum_date:
          type: string
          format: date
          nullable: true
        recording_date:
          type: string
          format: date
          nullable: true
        payment_date:
          type: string
          format: date
          nullable: true
        dividend_amount:
          type: number
          format: double
          nullable: true
      required:
        - cum_date
        - dividend_amount
        - ex_date
        - payment_date
        - recording_date
        - symbol
    CorporateActionsStockSplitRow:
      type: object
      properties:
        symbol:
          type: string
        date:
          type: string
          format: date
          description: Ex-date.
        cum_date:
          type: string
          format: date
          nullable: true
        recording_date:
          type: string
          format: date
          nullable: true
        split_ratio:
          type: number
          format: double
          nullable: true
        ratio:
          type: string
          nullable: true
          description: E.g. `1:2`.
      required:
        - cum_date
        - date
        - ratio
        - recording_date
        - split_ratio
        - symbol
    CorporateActionsBonusRow:
      type: object
      properties:
        symbol:
          type: string
        ex_date:
          type: string
          format: date
          description: Ex-date.
        cum_date:
          type: string
          format: date
          nullable: true
        recording_date:
          type: string
          format: date
          nullable: true
        payment_date:
          type: string
          format: date
          nullable: true
        old_ratio:
          type: number
          format: double
          nullable: true
        new_ratio:
          type: number
          format: double
          nullable: true
      required:
        - cum_date
        - ex_date
        - new_ratio
        - old_ratio
        - payment_date
        - recording_date
        - symbol
    CorporateActionsRightIssueRow:
      type: object
      properties:
        symbol:
          type: string
        ex_date:
          type: string
          format: date
          description: Ex-date.
        cum_date:
          type: string
          format: date
          nullable: true
        recording_date:
          type: string
          format: date
          nullable: true
        trading_period_start:
          type: string
          format: date
          nullable: true
        trading_period_end:
          type: string
          format: date
          nullable: true
        subscription_date:
          type: string
          format: date
          nullable: true
        price:
          type: number
          format: double
          nullable: true
        old_ratio:
          type: number
          format: double
          nullable: true
        new_ratio:
          type: number
          format: double
          nullable: true
      required:
        - cum_date
        - ex_date
        - new_ratio
        - old_ratio
        - price
        - recording_date
        - subscription_date
        - symbol
        - trading_period_end
        - trading_period_start
    CorporateActionsWarrantRow:
      type: object
      properties:
        symbol:
          type: string
        trading_period_start:
          type: string
          format: date
          description: First trading day of the warrant.
        trading_period_end:
          type: string
          format: date
          nullable: true
        ex_per_start:
          type: string
          format: date
          nullable: true
        ex_per_end:
          type: string
          format: date
          nullable: true
        maturity_date:
          type: string
          format: date
          nullable: true
        price:
          type: number
          format: double
          nullable: true
        ratio_warrant:
          type: number
          format: double
          nullable: true
        ratio_shares:
          type: number
          format: double
          nullable: true
      required:
        - ex_per_end
        - ex_per_start
        - maturity_date
        - price
        - ratio_shares
        - ratio_warrant
        - symbol
        - trading_period_end
        - trading_period_start
    CorporateActionsAgmRow:
      type: object
      properties:
        symbol:
          type: string
        agm_date:
          type: string
          format: date
          description: Meeting date.
        recording_date:
          type: string
          format: date
          nullable: true
        agm_time:
          type: string
          format: time
          nullable: true
        agm_place:
          type: string
          nullable: true
      required:
        - agm_date
        - agm_place
        - agm_time
        - recording_date
        - symbol
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: Authorization
      description: Global API Key Authorization

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.