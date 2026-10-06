> ## Documentation Index
> Fetch the complete documentation index at: https://docs.sectors.app/llms.txt
> Use this file to discover all available pages before exploring further.

# Company Report

> Returns a comprehensive company report organized into distinct sections. By default all sections are included. Use `sections` to request only the data you need and reduce response size.

<Note>IDX symbol: 4 letters, optionally followed by `.jk` (case-insensitive). E.g. `BREN`, `BBCA`, `TLKM`.</Note>

<Accordion title="Available sections">
- **overview**: Company identity, market cap, price history, ESG score, tags, indices, affiliates
- **valuation**: Close price, forward PE, intrinsic value, historical valuation (PB, PE, PS, PCF, PEG by year)
- **future**: Analyst forecasts, EPS growth estimates
- **peers**: Peer comparison within the same subsector
- **financials**: Historical annual financials (revenue, earnings, assets, equity, margins)
- **dividend**: Dividend history, yield, payout ratio
- **management**: Key executives and their shareholdings
- **ownership**: Major shareholders and ownership structure
</Accordion>

<Info>Costs 1 API credit per requested section. Default behavior (all 8 sections) consumes 8 credits.</Info>



## OpenAPI

````yaml GET /v2/company/report/{symbol}/
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
  /v2/company/report/{symbol}/:
    get:
      tags:
        - Detailed Reports
      summary: Company Report
      description: >-
        Returns a comprehensive company report organized into distinct sections.
        By default all sections are included. Use `sections` to request only the
        data you need and reduce response size.


        <Note>IDX symbol: 4 letters, optionally followed by `.jk`
        (case-insensitive). E.g. `BREN`, `BBCA`, `TLKM`.</Note>


        <Accordion title="Available sections">

        - **overview**: Company identity, market cap, price history, ESG score,
        tags, indices, affiliates

        - **valuation**: Close price, forward PE, intrinsic value, historical
        valuation (PB, PE, PS, PCF, PEG by year)

        - **future**: Analyst forecasts, EPS growth estimates

        - **peers**: Peer comparison within the same subsector

        - **financials**: Historical annual financials (revenue, earnings,
        assets, equity, margins)

        - **dividend**: Dividend history, yield, payout ratio

        - **management**: Key executives and their shareholdings

        - **ownership**: Major shareholders and ownership structure

        </Accordion>


        <Info>Costs 1 API credit per requested section. Default behavior (all 8
        sections) consumes 8 credits.</Info>
      operationId: company_report_retrieve_2
      parameters:
        - in: path
          name: symbol
          schema:
            type: string
          description: IDX symbol symbol. E.g. `BREN`, `BBCA`.
          required: true
          examples:
            Example:
              value: BREN
        - in: query
          name: sections
          schema:
            type: array
            items:
              type: string
              enum:
                - dividend
                - financials
                - future
                - management
                - overview
                - ownership
                - peers
                - valuation
          description: Comma-separated list of sections to include. Default to all.
          examples:
            Example:
              value: overview
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                description: Only requested `sections` are present.
                properties:
                  symbol:
                    type: string
                  company_name:
                    type: string
                  overview:
                    type: object
                    description: >-
                      Listing board, industry, sector, market cap, price, ESG,
                      tags.
                  valuation:
                    type: object
                    description: >-
                      PE/PB/PS, intrinsic value, forecasts, historical
                      valuation.
                  future:
                    type: object
                    description: Analyst value/growth forecasts and rating breakdown.
                  financials:
                    type: object
                    description: EPS, historical financials & ratios, YoY growth.
                  dividend:
                    type: object
                    description: Historical/upcoming dividends, yield, payout ratio.
                  management:
                    type: object
                    description: Key executives and their shareholdings.
                  ownership:
                    type: object
                    description: Major shareholders, transactions, whale investors.
                  peers:
                    type: array
                    items:
                      type: object
                    description: Peer companies.
              examples:
                CompanyReport:
                  value:
                    symbol: BBCA.JK
                    company_name: PT Bank Central Asia Tbk.
                    overview:
                      listing_board: Main
                      industry: Banks
                      sub_industry: Banks
                      sector: Financials
                      sub_sector: Banks
                      market_cap: 753611199412500
                      market_cap_rank: 1
                      address: "Menara BCA, Grand Indonesia\r\nJalan MH Thamrin No. 1\r\nJakarta 10310"
                      employee_num: 27937
                      employee_num_rank: 15
                      listing_date: '2000-05-31'
                      website: www.bca.co.id
                      phone: 021-23588000
                      email: investor_relations@bca.co.id
                      last_close_price: 6175
                      latest_close_date: '2026-07-08'
                      daily_close_change: -0.0198412698412698
                      all_time_price:
                        ytd_low:
                          '2026-06-09': 4820
                        52_w_low:
                          '2026-06-09': 4820
                        90_d_low:
                          '2026-06-09': 4820
                        ytd_high:
                          '2026-01-06': 8175
                        52_w_high:
                          '2025-08-13': 8975
                        90_d_high:
                          '2026-04-14': 6800
                        all_time_low:
                          '2004-06-08': 175
                        all_time_high:
                          '2024-09-23': 10950
                      esg_score: 21.44
                      tags:
                        - dividend-yield-ttm-above-5-percent
                        - esg-under-25
                        - top-90d-transaction-value
                        - top-90d-transaction-volume
                      indices:
                        - IDXESGL
                        - ECONOMIC30
                        - IDXG30
                        - IDX30
                        - LQ45
                        - FTSE
                        - SRIKEHATI
                        - KOMPAS100
                        - IDXHIDIV20
                        - IDXQ30
                      affiliates:
                        - Djarum
                        - Hartono
                    valuation:
                      last_close_price: 6175
                      latest_close_date: '2026-07-08'
                      daily_close_change: -0.0198412698412698
                      forward_pe: 12.7984576757419
                      intrinsic_value: 13694
                      historical_valuation:
                        - pb: 4.71766971488811
                          pe: 25.6154045827394
                          ps: 11.9285086042203
                          pcf: 30.8908493442671
                          peg: 0.8642744448236932
                          year: 2022
                          pb_peer_avg: 0.975919472508022
                          pe_peer_avg: 15.1292552726864
                          ps_peer_avg: 4.41860675563346
                          enterprise_to_ebitda: null
                          enterprise_to_revenue: null
                    future:
                      company_value_forecasts:
                        - eps_estimate: 518.5
                          estimate_year: 2026
                          revenue_estimate: 126170000000000
                      company_growth_forecasts:
                        - base_year: 2025
                          eps_growth: 0.099789989937308
                          estimate_year: 2026
                          revenue_growth: 0.12645423259397
                      analyst_rating_breakdown:
                        buy: 1
                        hold: 1
                        sell: 0
                        n_analyst: 23
                        strong_buy: 21
                        updated_on: '2026-05-07 18:03:41'
                        strong_sell: 0
                    financials:
                      eps: 471.4536454633092
                      historical_eps:
                        '2025':
                          eps: 471.4536454633092
                          eps_growth: 0.0493
                      historical_financials:
                        - tax: 6854404000000
                          ebit: null
                          year: 2018
                          ebitda: null
                          revenue: 63028090000000
                          earnings: 25855154000000
                          net_debt: 9375812000000
                          net_loan: null
                          cash_only: null
                          provision: null
                          credit_rwa: null
                          gross_loan: null
                          market_rwa: null
                          total_debt: 9375812000000
                          cash_inflow: null
                          cash_outflow: null
                          fixed_assets: null
                          gross_profit: null
                          time_deposit: null
                          total_assets: 824787944000000
                          total_equity: 151753427000000
                          net_cash_flow: null
                          operating_pnl: 32512504000000
                          total_capital: null
                          total_deposit: null
                          free_cash_flow: 22115523000000
                          long_term_debt: null
                          premium_income: null
                          prepaid_assets: null
                          cost_of_revenue: null
                          current_account: null
                          interest_income: null
                          non_loan_assets: null
                          operational_rwa: null
                          premium_expense: null
                          savings_account: null
                          short_term_debt: null
                          interest_expense: null
                          end_cash_position: null
                          operating_expense: null
                          retained_earnings: null
                          total_liabilities: 673034517000000
                          core_capital_tier1: null
                          industry_breakdown: null
                          net_premium_income: null
                          outstanding_shares: 123275000000
                          allowance_for_loans: null
                          current_liabilities: null
                          earnings_before_tax: 32706064000000
                          financing_cash_flow: null
                          investing_cash_flow: null
                          net_interest_income: null
                          non_interest_income: null
                          operating_cash_flow: 24462746000000
                          cash_and_equivalents: null
                          non_loan_earning_assets: null
                          high_quality_liquid_asset: null
                          total_risk_weighted_asset: null
                          non_loan_non_earning_assets: null
                          supplementary_capital_tier2: null
                          non_operating_income_or_loss: null
                          total_cash_and_due_from_banks: 65239752000000
                          interest_expense_non_operating: null
                          non_interest_bearing_liabilities: null
                          realized_capital_goods_investment: null
                          other_interest_bearing_liabilities: null
                      historical_financial_ratio:
                        - year: '2018'
                          capital:
                            capital_adequacy_ratio: null
                          leverage:
                            debt_to_asset_ratio: 0.011367542491624975
                            debt_to_equity_ratio: 4.43505316687181
                          liquidity:
                            casa_ratio: null
                            leverage_ratio: null
                            loan_to_deposit_ratio: null
                            liquidity_coverage_ratio: null
                            operating_cash_flow_margin: 0.38812450131362064
                          efficiency:
                            total_asset_turnover: 0.07641732697295585
                          profitability:
                            roa: 0.03134763812697049
                            roe: 0.17037607987594244
                            efficiency_ratio: 0.03134763812697049
                            net_profit_margin: 0.4102163654332536
                            net_interest_margin: null
                            cost_to_income_ratio: null
                            operating_profit_margin: 0.5158414922616249
                      yoy_quarter_earnings_growth: 0.0387073681660018
                      yoy_quarter_revenue_growth: 0.0110150546891309
                    dividend:
                      historical_dividends:
                        '2026':
                          breakdown:
                            - date: '2026-06-17'
                              total: 20
                              yield: 0.00323886639676113
                          total_yield: 0.0487449392712551
                          total_dividend: 301
                      upcoming_dividends: null
                      yield_ttm: 0.0576518218623482
                      dividend_yield_avg:
                        period: 5
                        avg_yield: 0.0283050359692425
                      dividend_ttm: 356
                      payout_ratio: 0.748637602001087
                      cash_payout_ratio: 0.687782037617804
                      last_ex_dividend_date: '2026-06-17'
                    management:
                      key_executives:
                        - name: Gregory Hendra Lembong
                          position: President Director
                      executives_shareholdings:
                        - name: Armand Wahyudi Hartono
                          position: Vice President Director
                          share_amount: 4256065
                          share_percentage: 0.00003
                    ownership:
                      major_shareholders:
                        - name: PT Dwimuria Investama Andalan
                          share_value: 418232441250000
                          share_amount: 67729950000
                          share_percentage: '0.54942'
                      top_transactions:
                        date: '2026-04-30'
                        top_buyers:
                          - name: Fidelity Institutional Asset Management
                            changeAmount: 186742480
                        top_sellers:
                          - name: Fidelity Management & Research Company LLC
                            changeAmount: -833622654
                      institutional_transaction_flow:
                        - date: '2026-04-30'
                          net_transaction: -4575387238
                      whale_investors:
                        - Anthoni Salim
                      conglomerates_group:
                        - Djarum Group
                    peers:
                      - peers_data:
                          companies:
                            - year: 2025
                              group:
                                - self
                              pb_mrq: 2.96707963218973
                              pe_ttm: 13.2251882418153
                              symbol: BBCA.JK
                              market_cap: 768866486850000
                              net_income: 57537287000000
                              company_name: PT Bank Central Asia Tbk.
                              employee_num: 27937
                              total_assets: 1586830000000000
                              total_equity: 281687555000000
                              pretax_income: 71260876000000
                              total_revenue: 112006326000000
                              point_summaries:
                                - name: value
                                  point: 10.5
                                  maxpoint: 18
                              yearly_mcap_chg: -0.275862068965517
                              operating_expense: 36734403000000
                              revenue_breakdown: null
                              total_liabilities: 1305140000000000
                              int_income_breakdown:
                                - class: Loans & Deposits
                                  amount: 67446394000000
                                  category: Loans
                              operating_expense_breakdown:
                                - class: Salaries & Benefits
                                  amount: 17780770000000
                                  category: Personnel expenses
                          group_name:
                            sector: Financials
                            industry: Banks
                            sub_sector: Banks
                            sub_industry: Banks
                  summary: Company report
                  x-example-request:
                    method: GET
                    path: /v2/company/report/{symbol}/
                    url: https://api.sectors.app/v2/company/report/BBCA/
                    path_params:
                      symbol: BBCA
          description: Comprehensive company report with requested sections.
        '400':
          content:
            application/json:
              schema:
                type: object
                additionalProperties: {}
              examples:
                InvalidSymbol:
                  value:
                    error: Please provide a valid stock symbol.
                  summary: Invalid symbol
          description: Invalid request (missing symbol or unknown section).
        '404':
          content:
            application/json:
              schema:
                type: object
                additionalProperties: {}
              examples:
                NotFound:
                  value:
                    error: Given stock symbol does not exist.
          description: Symbol not found — well-formed but absent from IDX data.
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
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: Authorization
      description: Global API Key Authorization

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.