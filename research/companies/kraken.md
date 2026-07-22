# Kraken (Payward, Inc.)

Draft dossier for Santiago's review. Not a final claim of fact beyond what is cited below.

Verified identity: this is Kraken the cryptocurrency exchange (legal entity Payward, Inc.),
not Kraken Technologies / "Kraken" the Octopus Energy platform (engineering.kraken.tech), which
is an unrelated UK company that also publishes an engineering blog under the "Kraken" name. All
sources below are from kraken.com, blog.kraken.com, or press coverage of the crypto exchange.

## 1. Snapshot

Kraken is a global cryptocurrency exchange (spot, futures, margin trading, staking, plus stock
and tokenized-asset trading) founded in 2011, serving 13M+ users worldwide (kraken.com/about).
Parent entity Payward, Inc. was raising new capital at a $20B valuation in late 2025 (backed by
Citadel Securities, Jane Street, DRW), though a secondary sale in April 2026 implied a lower
$13.3B mark; Payward employs roughly 3,000 people and is preparing for an IPO, expected pushed to
2027 (CoinDesk, May 2026; Bloomberg via CoinDesk). Remote-first, hires in 70+ countries
(blog.kraken.com). The México posting for this role has no on-site location tied to it, consistent
with Kraken's remote-first model.

## 2. Core narrative

Kraken is a 14+ year old crypto exchange (old by industry standards, not a startup) mid-transition
from "crypto native" to full-spectrum financial infrastructure: it holds a Federal Reserve master
account via its Wyoming bank charter (first crypto-native firm to do so), has filed for an OCC
national trust bank charter, and has spent 2025-2026 acquiring adjacent businesses (NinjaTrader
futures platform for $1.5B, Bitnomial derivatives exchange for $550M, Reap Technologies stablecoin
payments for $600M) while pushing toward an IPO (CoinDesk, coindesk.com/business/2026/02/18 and
2026/05/14). The Consumer team specifically (this role's team) is tasked with mass-market
onboarding: "onboard the next 100 million people to the benefits of crypto" through a simple web
and mobile product, distinct from the more advanced Kraken Pro trading app (job postings for
Consumer roles, e.g. cryptojobs.com/job/senior-software-engineer-frontend-consumer-8749). That
mass-market, performance-and-accessibility-at-scale mandate, on a company that is simultaneously
legacy-stable (14 years, regulated, bank charter) and still moving fast on M&A and IPO prep, is
the distinctive story here.

## 3. Mission & product

- Stated mission: "accelerate the adoption of crypto globally, so everyone can achieve financial
  freedom and inclusion" (kraken.com/careers).
- Products: spot and margin crypto trading, futures (via NinjaTrader acquisition), staking,
  Kraken+ premium subscription, and equities/tokenized stock trading (xStocks) (kraken.com/about).
- Revenue model: trading commissions and fees across these products (kraken.com/about).
- Regulatory build-out: Fed master account through its Wyoming SPDI bank charter (April 2026),
  OCC national trust bank charter application (CoinDesk, 2026/05/14).
- Recent M&A to broaden the product surface: NinjaTrader ($1.5B, retail futures), Bitnomial
  ($550M, derivatives exchange), Reap Technologies ($600M, stablecoin payments), Magna (token
  management, February 2026) (coindesk.com/business/2026/02/18; financefeeds.com;
  cryptobriefing.com).

## 4. Culture & voice

- Present-day public voice (kraken.com/careers) emphasizes: "globally remote company driven by
  independent thinkers who challenge the norm," mission-driven work, and a "borderless community."
- Remote-first is structural, not a perk: "Krakenites can build their careers from virtually
  anywhere... seniority is earned through impact, not proximity to a headquarters," with
  Krakenites in 70+ countries speaking 50+ languages (blog.kraken.com/news/industry-news/
  remote-is-how-kraken-operates; krakens-workforce-forever-remote-first).
- Benefits noted publicly: stock grants on most roles, flexible PTO, wellness stipend/fitness
  coaching, remote workspace setup bonus, and an option to receive part of pay in crypto
  (kraken.com/careers).
- Reputational watch-out (older, but material to "know before you apply"): in 2022, co-founder
  and then-CEO Jesse Powell circulated an internal 31-page "culture document" asserting
  libertarian values and rejecting mandated DEI language/pronoun policies, and offered a
  severance package ("Jet Ski program") to employees who disagreed and wanted to leave; this drew
  significant press (thedailybeast.com; fortune.com/crypto/2022/09/21). Powell stepped down as
  CEO in 2022/2023 and is now board chair; Dave Ripley and Arjun Sethi are co-CEOs as of 2026
  (kraken.com/press/releases/kraken-announces-leadership-succession-plan; cryptoslate.com/people/
  dave-ripley). Worth knowing the history exists, even though current public-facing culture
  material (2026) does not repeat that framing.

## 5. Recent news (last ~12 months, each dated)

- March 3, 2025: SEC agreed to dismiss (with prejudice) its unregistered-exchange lawsuit against
  Kraken, part of a broader 2025 regulatory softening toward crypto firms (also affecting
  Coinbase, MetaMask, OpenSea, Gemini, Robinhood) (finance.yahoo.com; banklesstimes.com). Note:
  this followed an earlier, separate 2023 settlement where Kraken paid $30M and shut down its
  U.S. staking product (insurancejournal.com backdrop cited in same coverage).
- November 2025: Payward filed a confidential S-1 with the SEC for an IPO, then paused the
  process in March 2026 as crypto valuations fell (coindesk.com/business/2026/05/14).
- Late 2025: Payward raised $800M at a $20B valuation, backed by Citadel Securities, Jane Street,
  DRW Venture Capital (unchainedcrypto.com; finance.yahoo.com).
- February 18, 2026: Kraken/Payward acquired token-management firm Magna ahead of its IPO push
  (coindesk.com/business/2026/02/18).
- April 2026: Kraken's Wyoming-chartered bank secured a Federal Reserve master account, becoming
  the first crypto-native firm with direct Fedwire settlement access; a Deutsche Borse secondary
  share purchase around the same time implied a $13.3B valuation, down about a third from the
  $20B peak six months prior (coindesk.com/business/2026/05/08).
- May 2026: Payward cut about 150 jobs (roughly 5% of its ~3,000 staff) as part of an
  "optimization" push ahead of the IPO; co-CEO Arjun Sethi said at Consensus Miami Kraken is
  "about 80% ready" to go public, with Bloomberg reporting a 2027 listing is now more likely than
  2026 (coindesk.com/business/2026/05/14; financefeeds.com).
- Also filed for an OCC national trust bank charter around the same period (coindesk.com/
  business/2026/05/14).

## 6. Engineering & AI direction

- Frontend stack: primary customer web app uses server-rendered Django templates with HTMX and
  vanilla JS for some interactive features, plus many React (TypeScript) single-page apps spread
  across the product (himalayas.app/companies/kraken/tech-stack, sourced from Kraken's own stated
  stack). Backend: Python/Django, Django Rest Framework and GraphQL, heavy AWS usage, HashiCorp
  tooling (Packer, Consul, Terraform) for continuous deployment (same source).
- Mobile: three production apps built in React Native, with custom native modules in Swift
  (iOS) and Kotlin (Android) and a Rust backend layer; the team is moving toward Expo modules over
  some community packages for maintainability and performance (blog.kraken.com/product/
  engineering/how-kraken-fixed-performance-issues-via-incremental-adoption-of-the-react-native-
  new-architecture).
- Performance engineering is a real, demonstrated practice, not just a job-posting buzzword:
  Kraken's data-intensive Pro app (charts constantly updating over WebSockets) shipped a
  React Native New Architecture migration that measured 1.3x faster full-app rendering, 2.5x
  faster home screen, and 5.3x faster trading-flow screen, with the largest gains on low-end
  Android devices (same blog post). Testing stack includes Maestro Cloud (E2E), React Testing
  Library (component), and Sentry/Mixpanel for real-world monitoring, with staged Play Store
  rollouts (same source).
- Consumer team's job postings (senior and staff frontend/mobile roles) call for React,
  TypeScript, and (at staff level) React/Next.js/React Native across web and mobile, with explicit
  emphasis on mentoring, code-quality standards, and driving engineering excellence across teams
  (cryptojobs.com/job/senior-software-engineer-frontend-consumer-8749;
  ziprecruiter.co.uk/jobs/505371634).
- No verified public claims found (in this pass) about a specific generative-AI product bet;
  flagging as unverified rather than guessing. The 150-person cut in May 2026 was reported in press
  as partly an "AI efficiency drive" (financefeeds.com headline), but that is a press
  characterization of the layoff, not a confirmed engineering roadmap detail, so treat it as
  directional color, not a hard fact about Kraken's AI stack.

## 7. Why-fit angles for Santiago

Strongest hook to lead with: Santiago has shipped consumer-facing React apps at real scale
(Eugenia.ai: 20+ buildings, 10,000+ users with 75% resident adoption; Nextia: 50,000+ users across
iOS/Swift, Android/Java, and React web) and has hands-on experience with the exact technical
texture of Kraken's Consumer/Pro problem: real-time, WebSocket-driven, chart-heavy UIs under
performance pressure (Plutus: TradingView-style multi-pane charting on lightweight-charts, a
WebSocket quote feed with single-use auth tickets and exponential-backoff reconnect, an SSE
client with cancellation). That is a close, honest match to a team whose own engineering blog is
about squeezing multi-x rendering gains out of a chart-and-WebSocket-heavy app on low-end devices.

Other resonant threads:
- Mass-market, non-technical-user onboarding (Kraken Consumer's "next 100 million people," Eugenia's
  HOA/resident non-technical user base) is a real parallel in product philosophy, not just tech.
- Fully remote-first, Mexico-based hiring removes the location friction that caps many roles;
  Kraken's own material explicitly frames seniority as impact-based, not proximity-based, which
  fits a founder used to owning outcomes without a manager in the room.

Honest concerns / watch-outs:
- Santiago's resume emphasizes AI/LLM and founder/0-to-1 breadth; this role is a pure frontend
  craft role (performance, accessibility, mentoring) with no AI angle evident in the JD or in
  Kraken's public engineering material for this team. Lead with frontend depth, not the AI
  narrative, for this specific application.
- Crypto/fintech has real regulatory volatility (SEC case only dropped in 2025 after a 2023 fine)
  and valuation volatility (reported $20B to $13.3B in six months); worth having a considered,
  non-defensive answer ready if asked about comfort with crypto/regulatory risk.
- The 2022 Jesse Powell culture-document episode is dated but discoverable; Santiago should know
  it exists (and that leadership and public messaging have since changed) rather than be
  surprised by it if it surfaces in an interview.
- No confirmed data on team size, on-call expectations, or interview process for this specific req
  was found in this pass; flag as unverified rather than assume.

## 8. Application-question angles

- Why this company: lead with the technical match, not generic "I love crypto." Frame it as: you
  have already built and shipped the same category of problem this team owns (real-time,
  WebSocket-fed, chart-dense UI performance work, at Plutus) for a mass, non-technical user base
  (at Eugenia and Nextia), and Kraken's Consumer team is solving that exact problem at a much
  larger scale (13M+ users, onboarding "the next 100 million"). One or two sentences, not a
  company-history recitation.
- Why you fit: anchor on the performance-and-accessibility-at-scale framing in the JD, and point
  to a concrete artifact (the lightweight-charts multi-pane implementation and WebSocket
  reconnect logic in Plutus, or the 50,000-user React/Swift/Java parity work at Nextia) rather
  than restating years of experience. Mention mentoring a 9-person team at Online Basics as the
  craft-and-standards side of the role.
- Anything else: remote-first fit (based in Mexico City, no relocation needed, comfortable
  operating with full ownership and no local manager) plus TN-visa eligibility as a forward-looking
  note if the conversation ever turns to a US-based team. Keep it short; do not raise the AI/agent
  background here unless asked, since it is not what this req is testing for.

## 9. Sources

researched: 2026-07-21

- https://www.kraken.com/about: founding date (2011, "14+ years"), 13M+ users, product line
  (spot/futures/margin/staking/xStocks), revenue model.
- https://www.kraken.com/careers: mission statement, remote-first policy language, benefits
  (stock, PTO, wellness, crypto pay option).
- https://blog.kraken.com/news/industry-news/krakens-workforce-forever-remote-first: remote-first
  as structural policy, 70+ countries.
- https://blog.kraken.com/news/industry-news/remote-is-how-kraken-operates: "seniority earned
  through impact, not proximity," borderless-team framing.
- https://blog.kraken.com/product/engineering/welcome-to-the-kraken-engineering-blog: engineering
  blog intro, open-source funding history, general engineering philosophy.
- https://blog.kraken.com/product/engineering/how-kraken-fixed-performance-issues-via-incremental-adoption-of-the-react-native-new-architecture
 : mobile stack (React Native, Swift, Kotlin, Rust backend), performance testing tools (Maestro,
  RTL, Sentry, Mixpanel), measured rendering speedups on the Pro app.
- https://himalayas.app/companies/kraken/tech-stack: web frontend stack detail (Django/HTMX plus
  React TypeScript SPAs), backend (Python/Django, DRF/GraphQL, AWS, Hashistack).
- https://www.cryptojobs.com/job/senior-software-engineer-frontend-consumer-8749 and
  https://www.ziprecruiter.co.uk/jobs/505371634-staff-software-engineer-mobile-frontend-consumer-at-kraken
 : Consumer team mandate ("next 100 million people"), role requirements (React/TypeScript,
  React Native/Next.js at staff level).
- https://unchainedcrypto.com/kraken-parent-payward-seeks-fresh-funding-at-20-billion-valuation-ahead-of-planned-ipo/
  and https://finance.yahoo.com/markets/crypto/articles/krakens-parent-company-payward-pushes-173105399.html
 : $800M raise, $20B valuation, Citadel/Jane Street/DRW backers.
- https://www.coindesk.com/business/2026/05/08/kraken-parent-payward-seeks-fresh-funding-at-usd20-billion-valuation-ahead-of-potential-ipo
 : Deutsche Borse secondary implying $13.3B valuation, decline from $20B peak.
- https://www.coindesk.com/business/2026/05/14/kraken-parent-payward-cuts-150-staff-streamlining-business-ahead-of-planned-ipo
 : May 2026 layoffs (150 staff, ~5% of ~3,000), Fed master account, OCC trust charter filing,
  IPO ~80% ready per Arjun Sethi, possible 2027 listing.
- https://financefeeds.com/kraken-cuts-150-staff-due-to-ai-delay-ipo-2027/: press framing of
  layoffs as tied to "AI efficiency," flagged as press characterization not confirmed roadmap.
- https://www.coindesk.com/business/2026/02/18/kraken-continues-acquisition-streak-by-buying-token-management-firm-magna-ahead-of-ipo-push
 : Magna acquisition, February 2026.
- https://cryptobriefing.com/kraken-layoffs-amid-ipo-expansion/: NinjaTrader ($1.5B), Bitnomial
  ($550M), Reap Technologies ($600M) acquisitions.
- https://finance.yahoo.com/news/sec-agrees-drop-lawsuit-against-081356049.html and
  https://www.banklesstimes.com/articles/2025/03/03/sec-agrees-to-drop-lawsuit-against-kraken-without-penalties/
 : March 2025 SEC lawsuit dismissal, prior 2023 $30M staking settlement referenced.
- https://www.thedailybeast.com/kraken-ceo-jesse-powell-says-hell-manage-out-any-woke-employees-the-hard-way/
  and https://fortune.com/crypto/2022/09/21/krakens-powell-steps-down-incoming-ceo-says-culture-will-not-change
 : 2022 culture-document controversy, leadership succession context.
- https://www.kraken.com/press/releases/kraken-announces-leadership-succession-plan and
  https://cryptoslate.com/people/dave-ripley/: leadership: Dave Ripley and Arjun Sethi as
  co-CEOs, Jesse Powell as board chair (2026).
