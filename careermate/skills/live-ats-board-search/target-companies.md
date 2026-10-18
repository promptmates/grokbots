# Target Companies

Verified ATS board tokens for live API search. Confirmed working Oct 15 2026 (every board returned valid JSON with at least 1 open job that day). 1260 boards across 5 platforms: 421 Greenhouse, 625 Ashby, 109 Lever, 37 Workable, 68 SmartRecruiters. Job counts (~Jobs) are a snapshot from Oct 15 2026 and change daily.

## How This Works

The agent searches these boards during Phase 2. You can customize this list:
- Add companies you're interested in
- Remove industries that don't apply
- The agent will search ALL of these unless your preferences filter some out
- Section headings (AI / ML, HR Tech / TA Tech, Fintech, UK / Europe Tech, etc.) can be excluded by name with `search_boards.py --exclude-section`

## API Endpoints

| Platform | URL Pattern | Auth Required |
|----------|-------------|---------------|
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/{token}/jobs` | No |
| Lever | `https://api.lever.co/v0/postings/{slug}?mode=json` | No |
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/{slug}` | No |
| Workable | `https://apply.workable.com/api/v1/widget/accounts/{slug}` | No |
| SmartRecruiters | `https://api.smartrecruiters.com/v1/companies/{id}/postings?limit=100&offset=0` | No (returns 200 with 0 jobs for unknown IDs; paginate by 100) |

---


## Greenhouse Boards (421 verified)


### AI / ML
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Anthropic | anthropic | 654 | AI safety, SF, hybrid |
| Arize AI | arizeai | 25 |  |
| Bolt.new (StackBlitz) | stackblitz | 7 | Bolt.new |
| CoreWeave | coreweave | 306 |  |
| Cresta | cresta | 86 |  |
| Descript | descript | 11 |  |
| Domino Data Lab | dominodatalab | 21 |  |
| Eudia | eudia | 23 |  |
| Extend | extend | 15 |  |
| Figure | figureai | 98 |  |
| Glean | gleanwork | 135 |  |
| Helsing | helsing | 157 |  |
| HeyGen | heygen | 21 |  |
| Imbue | imbue | 2 |  |
| Inflection AI | inflectionai | 6 | Personal AI |
| Invisible Technologies | invisibletech | 22 |  |
| Labelbox | labelbox | 7 |  |
| Lightmatter | lightmatter | 64 |  |
| Nebius | nebius | 376 |  |
| Observe.AI | observeai | 9 |  |
| Otter.ai | otterai | 23 |  |
| Pilot | pilothq | 10 |  |
| PolyAI | polyai | 2 |  |
| Regie.ai | regie | 1 |  |
| SambaNova | sambanovasystems | 62 |  |
| Scale AI | scaleai | 179 | AI data infrastructure |
| Snorkel AI | snorkelai | 44 |  |
| Stability AI | stabilityai | 6 | Image generation |
| Tenstorrent | tenstorrent | 127 |  |
| Together AI | togetherai | 73 | Open-source AI infra |
| Turing | turing | 29 |  |
| Typeface | typeface | 15 |  |
| Vectara | vectara | 4 |  |
| Vercel | vercel | 92 | Frontend deployment |
| Weights & Biases | weights_and_biases | 8 | Now part of CoreWeave |
| xAI | xai | 304 | xAI (board titled SpaceXSI) |
| You.com | youcom | 8 |  |

### HR Tech / TA Tech
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| BrightHire | brighthire | 6 |  |
| Built In | builtin | 3 |  |
| Carrot Fertility | carrotfertility | 14 |  |
| Carta | carta | 72 |  |
| Checkr | checkr | 43 |  |
| ClassPass | classpass | 30 |  |
| Culture Amp | cultureamp | 31 | Employee engagement |
| Degreed | degreed | 2 |  |
| GoodTime | goodtime | 2 |  |
| Greenhouse | greenhouse | 18 |  |
| Guild | guild | 3 |  |
| Gusto | gusto | 101 | Payroll / HR for SMB |
| Indeed Flex | indeedflex | 18 |  |
| Instawork | instawork | 57 |  |
| InStride | instride | 3 |  |
| Justworks | justworks | 101 |  |
| Karat | karat | 16 |  |
| Lattice | lattice | 9 | Performance management |
| Modern Health | modernhealth | 7 |  |
| SeekOut | seekout | 2 |  |
| Skillsoft | skillsoft | 12 |  |
| Talkspace | talkspace | 25 |  |
| Textio | textio | 2 |  |
| Wellhub | gympass | 87 | Formerly Gympass |
| Workstream | workstream | 25 |  |
| ZipRecruiter | ziprecruiter | 44 |  |

### Growth-Stage Tech
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| ACLU | aclu | 16 |  |
| Ada | ada18 | 8 |  |
| Airbnb | airbnb | 163 | Travel / hospitality |
| Airtable | airtable | 5 |  |
| Albedo | albedo | 5 |  |
| AON3D | aon3d | 2 |  |
| Apollo | apolloio | 53 |  |
| Asana | asana | 106 |  |
| AssemblyAI | assemblyai | 11 |  |
| Astranis | astranis | 181 |  |
| Attain | attain | 10 |  |
| Bitmovin | bitmovin | 11 |  |
| Box | boxinc | 127 |  |
| Brex | brex | 256 | Corporate cards |
| Buildkite | buildkite | 8 |  |
| Calendly | calendly | 9 |  |
| Calm | calm | 2 | Wellness |
| Caribou | caribou | 4 |  |
| CircleCI | circleci | 13 |  |
| Coalition | coalition | 42 |  |
| Coast | coast | 19 |  |
| Cockroach Labs | cockroachlabs | 18 |  |
| CoLab | colabsoftware | 21 |  |
| Collibra | collibra | 32 |  |
| Consensys | consensys | 8 |  |
| Contentful | contentful | 23 |  |
| Cortex | cortex | 5 |  |
| Coursera | coursera | 21 |  |
| Cribl | cribl | 68 |  |
| Deliveroo | deliveroo | 224 |  |
| Dialpad | dialpad | 55 |  |
| Discord | discord | 49 | Community platform |
| DoorDash | doordashusa | 454 |  |
| Dremio | dremio | 8 |  |
| Dropbox | dropbox | 21 |  |
| Duolingo | duolingo | 63 | EdTech |
| Elastic | elastic | 380 |  |
| Enveritas | enveritas | 5 |  |
| Epic Games | epicgames | 142 |  |
| Faire | faire | 79 | Wholesale marketplace |
| Figma | figma | 142 | Design platform |
| Fireblocks | fireblocks | 28 |  |
| Fivetran | fivetran | 180 |  |
| General Legal | general | 1 |  |
| GiveCampus | givecampus | 8 |  |
| Gong.io | gongio | 97 |  |
| Grafana Labs | grafanalabs | 106 |  |
| HackerRank | hackerrank | 32 |  |
| Harness | harnessinc | 64 |  |
| Heart Aerospace | heartaerospace | 5 |  |
| Honeycomb | honeycomb | 25 |  |
| Hubble Network | hubblenetwork | 18 |  |
| Human Interest | humaninterest | 70 |  |
| Icarus | icarus | 23 |  |
| Instacart | instacart | 122 | Grocery / delivery |
| Inversion Space | inversionspace | 88 |  |
| Island | island | 28 |  |
| JFrog | jfrog | 65 |  |
| LaunchDarkly | launchdarkly | 56 | Feature flags |
| Limrun | limrun | 5 |  |
| Lob | lob | 9 |  |
| Lucid | lucidsoftware | 31 |  |
| Lucid Bots | lucidbots | 2 |  |
| Lyft | lyft | 173 |  |
| MarqVision | marqvision | 16 |  |
| Mattermost | mattermost | 13 |  |
| May Mobility | maymobility | 39 |  |
| Mercury | mercury | 75 | Banking for startups |
| Mesh | mesh | 19 |  |
| Mindbody | mindbody | 21 |  |
| Mixpanel | mixpanel | 52 |  |
| Momentic | momentic | 24 |  |
| Momentus | momentus | 9 |  |
| MongoDB | mongodb | 402 |  |
| Nabis | nabis | 22 |  |
| Navan | tripactions | 214 | Navan (token: tripactions) |
| Navier AI | navierai | 2 |  |
| Netlify | netlify | 5 | Web deployment |
| Nextdoor | nextdoor | 22 |  |
| Nira Energy | niraenergy | 4 |  |
| Nuro | nuro | 109 |  |
| Odeko | odeko | 20 |  |
| Oklo | oklo | 72 |  |
| OpenWork | openwork | 16 |  |
| Orbital Operations | orbitaloperations | 5 |  |
| Osmosis | osmosis | 4 |  |
| Overwatch | overwatch | 2 |  |
| Peloton | peloton | 55 |  |
| Pendo | pendo | 26 |  |
| Pie Insurance | pieinsurance | 27 |  |
| Pinterest | pinterest | 157 |  |
| PlanetScale | planetscale | 11 | Serverless databases |
| Postscript | postscript | 3 |  |
| Public | public | 2 |  |
| RADAR | radar | 7 |  |
| Recidiviz | recidiviz | 6 |  |
| Reddit | reddit | 149 |  |
| Reflex | reflex | 3 |  |
| Relativity Space | relativity | 365 |  |
| Remora | remoracarbon | 9 |  |
| Riot Games | riotgames | 170 |  |
| Roblox | roblox | 259 |  |
| Rubrik | rubrik | 133 |  |
| Salt Security | saltsecurity | 13 |  |
| Scopely | scopely | 174 |  |
| Sendbird | sendbird | 5 |  |
| Sigma Computing | sigmacomputing | 75 |  |
| SingleStore | singlestore | 45 |  |
| SIRUM | sirum | 4 |  |
| Smartsheet | smartsheet | 96 |  |
| Spaceium | spaceium | 10 |  |
| SpaceX | spacex | 2751 |  |
| Starburst | starburst | 31 |  |
| StockX | stockx | 35 | Sneaker / collectibles |
| Submittable | submittable | 3 |  |
| Superset | superset | 4 |  |
| Swayable | swayable | 17 |  |
| Sweetgreen | sweetgreen | 64 |  |
| Tailscale | tailscale | 62 |  |
| Torq | torq | 25 |  |
| Twitch | twitch | 46 |  |
| Udemy | udemy | 7 |  |
| UserGems | usergems | 4 |  |
| Veriff | veriff | 10 |  |
| Waymo | waymo | 361 |  |
| Webflow | webflow | 20 | Visual web dev |
| Wrike | wrike | 60 |  |
| Yuma AI | yuma | 1 |  |
| Zerocater | zerocater | 11 |  |
| Zipline | flyzipline | 349 |  |

### Enterprise SaaS
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Abnormal Security | abnormalsecurity | 82 |  |
| Braze | braze | 320 |  |
| Celonis | celonis | 202 |  |
| Chainguard | chainguard | 79 | Supply chain security, remote-first |
| Cloudflare | cloudflare | 439 | Edge computing / security |
| Databricks | databricks | 897 | Big data / AI |
| Datadog | datadog | 439 | Observability |
| Flexport | flexport | 209 | Logistics platform |
| GitLab | gitlab | 218 | DevOps, all-remote |
| Huntress | huntress | 36 |  |
| Intercom (Fin) | intercom | 108 | Board name: Fin |
| Klaviyo | klaviyo | 147 |  |
| Motive | gomotive | 149 |  |
| Netskope | netskope | 135 |  |
| New Relic | newrelic | 56 |  |
| Okta | okta | 379 | Identity / security |
| Orca Security | orcasecurity | 10 | Cloud security |
| PagerDuty | pagerduty | 56 |  |
| project44 | project44 | 29 |  |
| Qualtrics | qualtrics | 78 |  |
| Samsara | samsara | 262 | IoT / operations |
| Sprout Social | sproutsocial | 24 |  |
| Squarespace | squarespace | 34 |  |
| Stripe | stripe | 725 | Payments infrastructure |
| Tanium | tanium | 72 |  |
| Toast | toast | 310 | Restaurant tech |
| Twilio | twilio | 137 | Communications APIs |
| Verkada | verkada | 320 | Physical security, onsite-heavy |
| Wiz | wizinc | 120 | Cloud security |
| Yext | yext | 23 |  |
| Zscaler | zscaler | 366 |  |

### Enterprise / Global
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Auto Trader | autotrader | 17 |  |
| Blockchain.com | blockchain | 39 |  |
| Engine | engine | 82 |  |
| Free Now | freenow | 19 |  |
| Gymshark | gymshark | 13 |  |
| HP | hp | 8 |  |
| Make | make | 7 |  |
| Ovo Energy | ovoenergy | 7 |  |
| Rocket Lab | rocketlab | 580 |  |
| Scout24 | scout24 | 12 |  |
| Tripadvisor | tripadvisor | 98 |  |
| Upwork | upwork | 9 |  |
| Workleap | workleap | 5 |  |

### Unicorns
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| 6sense | 6sense | 28 |  |
| AlphaSense | alphasense | 203 |  |
| Anduril Industries | andurilindustries | 2537 |  |
| AppDirect | appdirect | 72 |  |
| AppLovin | applovin | 42 |  |
| AppsFlyer | appsflyer | 49 |  |
| Axonius | axonius | 22 |  |
| BigID | bigid | 6 |  |
| Branch Metrics | branchmetrics | 15 |  |
| Bringg | bringg | 2 |  |
| C6 Bank | c6bank | 156 |  |
| Careem | careem | 17 |  |
| Cato Networks | catonetworks | 108 |  |
| Cognite | cognite | 53 |  |
| Colossal Biosciences | colossalbiosciences | 14 |  |
| Coupang | coupang | 695 |  |
| DiDi | didi | 9 |  |
| Digital Currency | digitalcurrencygroup | 1 |  |
| DistroKid | distrokid | 1 |  |
| Dragos | dragos | 51 |  |
| DriveWealth | drivewealth | 19 |  |
| Druva | druva | 34 |  |
| Ebanx | ebanx | 40 |  |
| Emplifi | emplifi | 5 |  |
| Feedzai | feedzai | 31 |  |
| Flexe | flexe | 2 |  |
| Flo Health | flohealth | 22 |  |
| Formlabs | formlabs | 239 |  |
| Forter | forter | 21 |  |
| Glance | glance | 36 |  |
| Groupon | groupon | 24 |  |
| HighRadius | highradius | 75 |  |
| HomeLight | homelight | 16 |  |
| ID.me | idme | 49 |  |
| Incode | incode | 9 |  |
| InMobi | inmobi | 78 |  |
| Krafton | krafton | 54 |  |
| Lightricks | lightricks | 5 |  |
| Locus Robotics | locusrobotics | 4 |  |
| Lookout | lookout | 2 |  |
| MasterClass | masterclass | 5 |  |
| MOLOCO | moloco | 41 |  |
| NetDocuments | netdocuments | 17 |  |
| Neuralink | neuralink | 80 |  |
| Nextiva | nextiva | 26 |  |
| OneTrust | onetrust | 88 |  |
| PandaDoc | pandadoc | 10 |  |
| PAX Labs | paxlabs | 7 |  |
| Picsart | picsart | 9 |  |
| PsiQuantum | psiquantum | 78 |  |
| Quince | quince | 146 |  |
| QuintoAndar | quintoandar | 98 |  |
| Relex | relex | 41 |  |
| River AI | riverai | 19 |  |
| Roivant Sciences | roivantsciences | 10 |  |
| Roku | roku | 114 |  |
| Scandit | scandit | 8 |  |
| Shein | shein | 19 |  |
| Slice | slice | 27 |  |
| Stitch Fix | stitchfix | 14 |  |
| Sword Health | swordhealth | 47 |  |
| Thatch | thatch | 29 |  |
| Transmit Security | transmitsecurity | 14 |  |
| Truecaller | truecaller | 32 |  |
| Unite Us | uniteus | 15 |  |
| Vonage | vonage | 16 |  |
| Vox Media | voxmedia | 17 |  |
| VTS | vts | 17 |  |
| Workato | workato | 63 |  |
| Yotpo | yotpo | 14 |  |
| Yugabyte | yugabyte | 15 |  |
| Zenoti | zenoti | 55 |  |

### Fintech
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Adyen | adyen | 237 |  |
| Affirm | affirm | 211 | Buy now pay later |
| Alloy | alloy | 24 |  |
| Alpaca | alpaca | 75 |  |
| Axiom | axiom | 17 |  |
| Axle | axle | 48 |  |
| Baubap | baubap | 3 |  |
| Betterment | betterment | 24 |  |
| Bill.com | billcom | 43 | Business payments |
| Block | block | 224 |  |
| Chime | chime | 72 | Neobank |
| Coinbase | coinbase | 229 | Crypto (filter if excluded) |
| Flex | flex | 32 |  |
| Gemini | gemini | 32 |  |
| GoCardless | gocardless | 32 |  |
| Grey | grey | 18 |  |
| Groww | groww | 10 |  |
| Legalist | legalist | 4 |  |
| Lithic | lithic | 11 |  |
| Long Term Stock Exchange | ltse | 1 |  |
| Melio | melio | 24 |  |
| Monzo | monzo | 69 |  |
| N26 | n26 | 34 |  |
| Nova Credit | novacredit | 8 |  |
| Payoneer | payoneer | 97 |  |
| Prodigal | prodigal | 14 |  |
| Ripple | ripple | 108 |  |
| Robinhood | robinhood | 154 | Trading platform |
| Rocket Money | truebill | 18 | Rocket Money (token: truebill) |
| SmartAsset | smartasset | 4 |  |
| SoFi | sofi | 51 | Digital banking |
| Solaris | solarisbank | 22 |  |
| Upgrade | upgrade | 28 |  |
| Xendit | xendit | 27 |  |

### Healthcare / Life Sciences
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Akido Labs | akidolabs | 21 |  |
| Ansa Biotechnologies | ansabiotechnologies | 3 |  |
| BillionToOne | billiontoone | 87 |  |
| Clara | clara | 147 |  |
| Culture Biosciences | culturebiosciences | 4 |  |
| Daybreak Health | daybreakhealth | 31 |  |
| Doctolib | doctolib | 149 |  |
| Flatiron Health | flatironhealth | 20 | Oncology data |
| General Proximity | generalproximity | 8 |  |
| Ginkgo Bioworks | ginkgobioworks | 20 | Synthetic biology |
| Isomorphic Labs | isomorphiclabs | 29 |  |
| Kernal Biologics | kernalbio | 6 |  |
| Komodo Health | komodohealth | 27 |  |
| Luminate | luminate | 3 |  |
| Maven Clinic | mavenclinic | 36 |  |
| Meru Health | meruhealth | 1 |  |
| Omada | omadahealth | 18 |  |
| One Medical | onemedical | 395 |  |
| Ophelia | ophelia | 14 |  |
| Oscar Health | oscar | 231 |  |
| Pair Team | pairteam | 5 |  |
| Papa | papa | 3 |  |
| Parallel Bio | parallel | 16 |  |
| Pelago | pelago | 14 |  |
| Qventus | qventus | 17 |  |
| Recursion | recursionpharmaceuticals | 13 |  |
| Veracyte | veracyte | 26 | Genomic diagnostics |
| Zocdoc | zocdoc | 59 |  |

### Consumer / Marketplace
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Eventbrite | eventbriteinc | 1 |  |
| GetYourGuide | getyourguide | 71 |  |
| Glossier | glossier | 21 |  |
| Grover | grover | 3 |  |
| HelloFresh | hellofresh | 410 |  |
| Kickstarter | kickstarter | 1 |  |
| LAIKA | laika | 2 |  |
| Medium | medium | 1 |  |
| Pronto | pronto | 30 |  |
| Raisin | raisin | 41 |  |
| Rent the Runway | renttherunway | 24 |  |
| Roofr | roofr | 10 |  |
| SeatGeek | seatgeek | 37 |  |
| SumUp | sumup | 334 |  |

### UK / Europe Tech
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Algolia | algolia | 37 |  |
| Bird | bird | 31 |  |
| Bitpanda | bitpanda | 31 |  |
| Cabify | cabify | 69 |  |
| CarbonChain | carbonchain | 1 |  |
| Cleo | cleo | 5 |  |
| Cognism | cognism | 18 |  |
| Dataiku | dataiku | 14 |  |
| Diligent | diligent | 6 |  |
| Flix | flix | 143 |  |
| Focal Systems | focalsystems | 30 |  |
| GoStudent | gostudent | 28 |  |
| Graphcore | graphcore | 177 |  |
| Isar Aerospace | isaraerospace | 115 |  |
| Ivalua | ivalua | 48 |  |
| Juno | juno | 14 |  |
| Konux | konux | 2 |  |
| Ledgy | ledgy | 4 |  |
| Lighthouse | lighthouse | 36 |  |
| Marvel Fusion | marvelfusion | 15 |  |
| Mirakl | mirakl | 29 |  |
| Nothing | nothing | 8 |  |
| Parloa | parloa | 53 |  |
| Prolific | prolific | 30 |  |
| Prospa | prospa | 8 |  |
| Shift Technology | shifttechnology | 28 |  |
| Sixfold Bioscience | sixfold | 3 |  |
| Staffbase | staffbase | 22 |  |
| Tide | tide | 102 |  |
| Trade Republic | traderepublicbank | 42 |  |
| Trivago | trivago | 17 |  |
| TrueLayer | truelayer | 3 |  |
| Typeform | typeform | 13 |  |
| Urban Sports Club | urbansportsclub | 4 |  |
| Vay | vay | 15 |  |
| Wolt | wolt | 211 |  |

---

## Ashby Boards (625 verified)


### AI / ML
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Abridge | abridge | 43 |  |
| Aleph Alpha | alephalpha | 4 |  |
| Anyscale | anyscale | 20 | Ray / distributed compute |
| Artisan | artisan | 4 |  |
| Baseten | baseten | 107 |  |
| Braintrust | braintrust | 27 |  |
| Browserbase | browserbase | 9 |  |
| Cerebras | cerebras | 125 | AI chips |
| Character AI | character | 13 | Conversational AI |
| Chroma | trychroma | 1 |  |
| Clay | claylabs | 57 |  |
| CodeRabbit | coderabbit | 47 |  |
| Cognition | cognition | 102 |  |
| Cohere | cohere | 118 | Enterprise AI |
| Crusoe | crusoe | 349 |  |
| Cursor (Anysphere) | cursor | 133 |  |
| d-Matrix | d-matrix | 42 |  |
| Decagon | decagon | 140 |  |
| DeepL | deepl | 7 |  |
| E2B | e2b | 14 |  |
| ElevenLabs | elevenlabs | 154 |  |
| Ema | ema | 38 |  |
| Etched | etched | 115 |  |
| Exa | exa | 56 |  |
| Factory | factory | 59 |  |
| Faculty | faculty | 78 |  |
| Fathom | fathom | 1 |  |
| Fireworks AI | fireworks | 88 |  |
| Gamma | gamma | 21 |  |
| Genspark | genspark | 9 |  |
| Granola | granola | 22 |  |
| Graphite | graphite | 7 |  |
| Greptile | greptile | 18 |  |
| Handshake | handshake | 90 |  |
| Harvey | harvey | 343 |  |
| Lambda | lambda | 91 |  |
| LangChain | langchain | 101 |  |
| Legora | legora | 302 |  |
| Liquid AI | liquid | 2 |  |
| LlamaIndex | llamaindex | 3 |  |
| Lovable | lovable | 81 |  |
| Luma AI | lumaai | 35 |  |
| Mercor | mercor | 112 |  |
| Midjourney | midjourney | 17 |  |
| Mintlify | mintlify | 15 |  |
| Modal | modal | 43 | Serverless compute for AI |
| Nomic | nomic | 6 |  |
| Notion | notion | 129 | Workspace platform |
| OpenAI | openai | 802 | AI research, SF onsite |
| Parallel | parallel | 26 |  |
| Pathos | pathos | 3 |  |
| Patronus AI | patronus | 5 |  |
| Perplexity | perplexity | 131 | AI search |
| Physical Intelligence | physicalintelligence | 41 |  |
| Pika | pika | 15 |  |
| Pinecone | pinecone | 5 |  |
| Poolside | poolside | 2 |  |
| Ramp | ramp | 163 | Corporate spend |
| Rasa | rasa | 2 |  |
| Reducto | reducto | 40 |  |
| Reka | reka | 9 |  |
| Relevance AI | relevanceai | 1 |  |
| Replit | replit | 65 |  |
| Rilla | rilla | 30 |  |
| Rogo | rogo | 89 |  |
| Runway | runway-ml | 49 | Creative AI video |
| Sierra | sierra | 186 |  |
| Speak | speak | 34 |  |
| Speakeasy | speakeasy | 5 |  |
| Suno | suno | 71 |  |
| Synthesia | synthesia | 49 |  |
| Tavily | tavily | 18 |  |
| Tavus | tavus | 19 |  |
| Tennr | tennr | 27 |  |
| Thinking Machines | thinkingmachines | 55 |  |
| Tractable | tractable | 5 |  |
| Unify | unify | 10 |  |
| Unstructured | unstructured | 5 |  |
| Vapi | vapi | 23 |  |
| Warp | warp | 22 |  |
| Wayve | wayve | 168 |  |
| Weaviate | weaviate | 3 |  |
| World Labs | worldlabs | 11 |  |
| Writer | writer | 47 |  |
| Zed | zed | 1 |  |

### HR Tech / TA Tech
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| A.Team | ateam | 2 |  |
| Alex | alexai | 2 |  |
| Ashby | ashby | 62 | ATS / HR tech |
| Beamery | beamery | 5 |  |
| Benepass | benepass | 5 |  |
| Catalant | catalant | 10 |  |
| ChartHop | charthop | 1 |  |
| Contra | contra | 5 |  |
| Dex | dex | 4 |  |
| Docebo | docebo | 43 |  |
| Forma | forma | 3 |  |
| Grow Therapy | grow-therapy | 27 |  |
| Humaans | humaans | 12 |  |
| Juicebox | juicebox | 31 |  |
| Kota | kota | 8 |  |
| Metaview | metaview | 39 |  |
| Nava Benefits | nava-benefits | 4 |  |
| Oyster | oyster | 22 | Global employment |
| Paraform | paraform | 16 |  |
| Payscale | payscale | 12 |  |
| Ravio | ravio | 5 |  |
| Rula | rula | 37 |  |
| Shiftsmart | shiftsmart | 7 |  |
| TestGorilla | testgorilla | 4 |  |
| Visier | visier | 8 |  |
| Zenjob | zenjob | 12 |  |

### Growth-Stage Tech
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| 9 Mothers | 9-mothers | 6 |  |
| Abacum | abacum | 16 |  |
| Abundant | abundant | 9 |  |
| Accord | accord | 5 |  |
| Acorns | acorns | 12 |  |
| AfterQuery | afterquery | 39 |  |
| Agave | agave | 10 |  |
| AgentMail | agentmail | 9 |  |
| Airbyte | airbyte | 13 |  |
| Airgoods | airgoods | 2 |  |
| Alchemy | alchemy | 22 |  |
| Ambition | ambition | 1 |  |
| Ambral | ambral | 3 |  |
| Amplitude | amplitude | 39 | Product analytics |
| Apolink | apolink | 4 |  |
| Aragorn AI | aragorn | 1 |  |
| Arketa | arketa | 7 |  |
| Artie | artie | 5 |  |
| Artos | artosai | 5 |  |
| Asimov | asimov | 7 |  |
| Assembled | assembledhq | 17 |  |
| Astro Mechanica | astro-mechanica | 26 |  |
| Atlan | atlan | 7 |  |
| Atomic Industries | atomic | 10 |  |
| Attio | attio | 37 |  |
| Auctor | auctor | 11 |  |
| Aurelian | aurelian | 8 |  |
| authzed | authzed | 5 |  |
| Automat | automat | 7 |  |
| Avoca | avoca | 27 |  |
| Benchling | benchling | 56 | Life sciences R&D |
| Bestow | bestow | 5 |  |
| Beyond Reach Labs | beyondreachlabs | 5 |  |
| Bild AI | bild-ai | 4 |  |
| Blacksmith | blacksmith | 20 |  |
| Bland AI | bland | 16 |  |
| Blissway | blissway | 12 |  |
| Bolna AI | bolna | 7 |  |
| Boostly | boostly | 1 |  |
| BootLoop | bootloop | 1 |  |
| Brainbase Labs | brainbaselabs | 6 |  |
| Broccoli AI | broccoli | 34 |  |
| Brumby | brumby | 5 |  |
| Cambio | cambio | 7 |  |
| Cambly | cambly | 7 |  |
| Campfire | campfire | 52 |  |
| Capy | capy | 2 |  |
| Cardboard | cardboard | 7 |  |
| Casco | casco | 1 |  |
| Centralize | centralize | 3 |  |
| Charge Robotics | charge-robotics | 14 |  |
| Chili Piper | chilipiper | 2 |  |
| Cinder | cinder | 9 |  |
| Circleback | circleback | 10 |  |
| ClassDojo | classdojo | 11 |  |
| Clearly AI | clearly-ai | 2 |  |
| Clerk | clerk | 2 |  |
| Clickhouse | clickhouse | 197 |  |
| ClickUp | clickup | 51 | Project management |
| Clueso | clueso | 3 |  |
| Coder | coder | 25 |  |
| Codes Health | codes-health | 15 |  |
| Complir | complir | 3 |  |
| Concourse | concourse | 7 |  |
| Conductor | conductor | 3 |  |
| Conduit | conduit | 2 |  |
| Confido | confido | 38 |  |
| Coperniq | coperniq | 3 |  |
| Corvus Robotics | corvus-robotics | 8 |  |
| Credal.ai | credal | 5 |  |
| CTGT | ctgt | 3 |  |
| Curri | curri | 22 |  |
| d_model | dmodel | 2 |  |
| Datafold | datafold | 5 |  |
| Dataleap | dataleap | 8 |  |
| David AI | david-ai | 16 |  |
| Dedalus Labs | dedalus-labs | 4 |  |
| Deepgram | deepgram | 88 |  |
| Deepnote | deepnote | 3 |  |
| DiligenceSquared | diligencesquared | 9 |  |
| Ditto | ditto | 8 |  |
| Docker | docker | 68 |  |
| Domu Technology | domu | 2 |  |
| Doppler | doppler | 1 |  |
| Drata | drata | 32 | Compliance automation |
| Dyneti Technologies | dyneti | 9 |  |
| Ekho | ekho | 3 |  |
| Electric Air | electricair | 5 |  |
| Ello | ello | 4 |  |
| Eloquent AI | eloquentai | 13 |  |
| Enode | enode | 5 |  |
| Envoy | envoy | 22 |  |
| Eventual | eventual | 4 |  |
| Expensify | expensify | 2 |  |
| Fieldguide | fieldguide | 51 |  |
| Firecrawl | firecrawl | 33 |  |
| FirstWork | firstwork | 10 |  |
| Flai | flai | 14 |  |
| Fleetline | fleetline | 3 |  |
| FleetWorks | fleetworks | 7 |  |
| Flowtel | flowtel | 1 |  |
| FlutterFlow | flutterflow | 3 |  |
| Freshpaint | freshpaint | 4 |  |
| FullStory | fullstory | 10 |  |
| FurtherAI | furtherai | 10 |  |
| Gecko Robotics | gecko-robotics | 21 |  |
| General Astronautics | generalastro | 5 |  |
| Gigs | gigs | 52 |  |
| Glimpse | glimpse | 8 |  |
| GoLinks | golinks | 6 |  |
| Gorgias | gorgias | 16 |  |
| GovDash | govdash | 3 |  |
| GovEagle | goveagle | 2 |  |
| Great Question | greatquestion | 4 |  |
| Gumloop | gumloop | 12 |  |
| H3X Technologies | h3x-technologies | 9 |  |
| Halluminate | halluminate | 10 |  |
| Hex | hex | 40 |  |
| Hightouch | hightouch | 1 |  |
| HockeyStack | hockeystack | 3 |  |
| Homebase | homebase | 17 |  |
| Hudu | hudu | 1 |  |
| Human Archive | humanarchive | 21 |  |
| Humanly | humanly | 2 |  |
| Hyperbound | hyperbound | 9 |  |
| Hypercubic | hypercubic | 2 |  |
| Hyperspell | hyperspell | 1 |  |
| idler | idler | 7 |  |
| Infisical | infisical | 7 |  |
| InfluxData | influxdata | 4 |  |
| Inkeep | inkeep | 3 |  |
| Interfere | interfere | 4 |  |
| Invopop | invopop | 2 |  |
| Ironclad | ironcladhq | 30 |  |
| Jiga | jiga | 10 |  |
| Jobber | jobber | 42 |  |
| Julius | julius | 4 |  |
| Kastle | kastle | 14 |  |
| Knock | knock | 3 |  |
| Kodex | kodex | 8 |  |
| Kong | kong | 88 |  |
| Kustomer | kustomer | 2 |  |
| Lago | lago | 1 |  |
| LanceDB | lancedb | 13 |  |
| Lapel | lapel | 9 |  |
| Ledger | ledger | 11 |  |
| Lemonade | lemonade | 39 |  |
| Linear | linear | 31 | Project management |
| LiteLLM | litellm | 10 |  |
| LiveFlow | liveflow | 4 |  |
| LiveKit | livekit | 28 |  |
| Luminai | luminai | 18 |  |
| Mach9 | mach9 | 18 |  |
| Magic Patterns | magicpatterns | 7 |  |
| Mastra | mastra | 2 |  |
| Material Security | materialsecurity | 2 |  |
| Meadow | meadow | 6 |  |
| Mem0 | mem0 | 1 |  |
| Middesk | middesk | 15 |  |
| Miro | miro | 22 | Visual collaboration |
| Miso Labs | misolabs | 1 |  |
| Monarch Money | monarchmoney | 11 |  |
| Monte Carlo | montecarlodata | 10 |  |
| MorphoAI | morpho | 11 |  |
| Mundo AI | mundo-ai | 3 |  |
| Mutiny | mutiny | 9 |  |
| Mux | mux | 1 |  |
| Nango | nango | 8 |  |
| Nash | nash | 22 |  |
| Neon | neon | 4 |  |
| New Story | new-story | 1 |  |
| Notabene | notabene | 4 |  |
| Nowadays | nowadays | 3 |  |
| Nox Metals | nox-metals | 36 |  |
| Numeral | numeral | 23 |  |
| OffDeal | offdeal | 5 |  |
| Offstream | offstream | 1 |  |
| Omni | omni | 35 |  |
| One Robot | onerobot | 3 |  |
| Onebrief | onebrief | 31 |  |
| OneSchema | oneschema | 2 |  |
| Opencall | opencall | 4 |  |
| OutRival | outrival | 2 |  |
| Outschool | outschool | 9 |  |
| Outset | outset | 20 |  |
| Owner | owner | 48 |  |
| Padlet | padlet | 17 |  |
| Paradigm | paradigm | 6 |  |
| Paragon | paragon | 1 |  |
| Paxos | paxos | 20 |  |
| PermitFlow | permitflow | 42 |  |
| Phantom | phantom | 13 |  |
| Phonely | phonely | 19 |  |
| Pirros | pirros | 2 |  |
| Pivot Robotics | pivotrobotics | 5 |  |
| Plaid | plaid | 127 | Financial data APIs |
| PointOne | pointone | 16 |  |
| Polymath | polymath | 4 |  |
| Popl | popl | 6 |  |
| Posh | posh | 12 |  |
| Poshmark | poshmark | 33 | Fashion marketplace |
| PostHog | posthog | 10 | Product analytics, open-source |
| Proof of Human | proofofhuman | 3 |  |
| Pylon | pylon | 18 |  |
| Quicknode | quicknode | 2 |  |
| Quindar | quindar | 20 |  |
| Railway | railway | 7 | App deployment |
| Raindrop | raindrop | 9 |  |
| Reacher | reacher | 8 |  |
| ReadMe | readme | 2 |  |
| Reality Defender | realitydefender | 2 |  |
| Recall.ai | recall | 6 |  |
| REGENT | regent | 32 |  |
| Relace | relace | 6 |  |
| Relling | relling | 11 |  |
| Render | render | 39 | Cloud hosting |
| Replo | replo | 2 |  |
| Rescale | rescale | 17 |  |
| Resend | resend | 14 |  |
| Retell AI | retell-ai | 27 |  |
| RevenueCat | revenuecat | 17 |  |
| Revise Robotics | reviserobotics | 2 |  |
| REZI | rezi | 2 |  |
| Rivet | rivet | 26 |  |
| Rivia.AI | rivia | 8 |  |
| Roboflow | roboflow | 36 |  |
| Rollstack | rollstack | 2 |  |
| Rutter | rutter | 1 |  |
| Ryvn | ryvn | 1 |  |
| SafetyKit | safetykit | 9 |  |
| Salient | salient | 15 |  |
| Sanity | sanity | 34 |  |
| Saronic | saronic | 237 |  |
| Sentry | sentry | 46 |  |
| SF Tensor | sf-tensor | 7 |  |
| Shadeform | shadeform | 6 |  |
| Sieve | sieve | 13 |  |
| Sift | sift | 7 |  |
| SigNoz | signoz | 15 |  |
| Simetrik | simetrik | 8 |  |
| Simple AI | simple-ai | 11 |  |
| SkydropX | skydropx | 40 |  |
| Snapdocs | snapdocs | 3 |  |
| SnapMagic | snapmagic | 7 |  |
| Snowflake | snowflake | 357 | Data cloud |
| Snyk | snyk | 27 |  |
| Sola | sola | 5 |  |
| Solidroad | solidroad | 8 |  |
| Sorare | sorare | 2 |  |
| SpruceID | spruceid | 5 |  |
| Spur | spur | 3 |  |
| Stepful | stepful | 42 |  |
| Stilta | stilta | 4 |  |
| Strava | strava | 36 |  |
| Subsets | subsets | 1 |  |
| Substrate | substrate | 7 |  |
| Supabase | supabase | 54 | Open-source Firebase |
| Svix | svix | 2 |  |
| Sweep | sweep | 7 |  |
| Switchboard | switchboard | 10 |  |
| Sygaldry Technologies | sygaldry-technologies | 15 |  |
| Tailor | tailor | 54 |  |
| Tajir | tajir | 3 |  |
| Tamarind Bio | tamarindbio | 7 |  |
| Teleport | goteleport | 25 |  |
| Temporal | temporal | 69 | Workflow orchestration |
| Thera | thera | 6 |  |
| Thumbtack | thumbtack | 55 |  |
| Thunder Compute | thundercompute | 1 |  |
| Toku | toku | 23 |  |
| Topline Pro | topline-pro | 12 |  |
| TRM Labs | trm-labs | 112 |  |
| Turion Space | turion-space | 5 |  |
| Uniswap | uniswap | 6 |  |
| UpCodes | upcodes | 5 |  |
| Uplane | uplane | 16 |  |
| Usul | usul | 6 |  |
| Vanta | vanta | 84 | Security compliance |
| Vetcove | vetcove | 27 |  |
| Voodoo | voodoo | 118 |  |
| Vooma | vooma | 11 |  |
| Vori | vori | 11 |  |
| Vorticity | vorticity | 1 |  |
| Wafer | wafer | 1 |  |
| Wealthsimple | wealthsimple | 46 |  |
| Weave | weave | 28 |  |
| Wistia | wistia | 2 |  |
| WorkOS | workos | 29 |  |
| Zapier | zapier | 11 |  |
| Zensors | zensors | 5 |  |

### Enterprise SaaS
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| 1Password | 1password | 71 |  |
| Gainsight | gainsight | 17 |  |
| Iterable | iterable | 10 |  |
| Persona | persona | 15 |  |
| Semgrep | semgrep | 12 |  |
| Socure | socure | 88 |  |
| UiPath | uipath | 105 |  |

### Enterprise / Global
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Allica Bank | allica-bank | 36 |  |
| Andela | andela | 16 |  |
| Ankorstore | ankorstore | 1 |  |
| Black Forest Labs | black-forest-labs | 14 |  |
| Funding Circle | fundingcircle | 23 |  |
| Kayak | kayak | 43 |  |
| Moneybox | moneybox | 21 |  |
| Pennylane | pennylane | 142 |  |
| Signal AI | signal-ai | 2 |  |
| Swan | swan | 6 |  |
| Workhuman | workhuman | 8 |  |
| Xero | xero | 107 |  |

### Unicorns
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Benevity | benevity | 19 |  |
| Blockstream | blockstream | 46 |  |
| Clubhouse | clubhouse | 3 |  |
| EliseAI | eliseai | 130 |  |
| Epidemic Sound | epidemic-sound | 25 |  |
| HoneyBook | honeybook | 7 |  |
| Illumio | illumio | 65 |  |
| Injective | injective | 12 |  |
| Lunar | lunar | 15 |  |
| MEGAZONE | megazone | 13 |  |
| Morning Consult | morningconsult | 9 |  |
| Mural | mural | 11 |  |
| Musinsa | musinsa | 1 |  |
| Neo Financial | neofinancial | 56 |  |
| Odyssey | odyssey | 7 |  |
| OpenEvidence | openevidence | 9 |  |
| Rohlik | rohlik | 92 |  |
| SandboxAQ | sandboxaq | 28 |  |
| Simile | simile | 10 |  |
| Sisense | sisense | 4 |  |
| Sky Mavis | skymavis | 6 |  |
| Solstice | solstice | 17 |  |
| SpotOn | spoton | 76 |  |
| Tekion | tekion | 94 |  |
| Trulioo | trulioo | 26 |  |
| Trustly | trustly | 34 |  |
| Virta Health | virtahealth | 21 |  |
| Wayflyer | wayflyer | 15 |  |
| WHOOP | whoop | 172 |  |
| Zilch | zilch | 16 |  |

### Fintech
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| AiPrise | aiprise | 18 |  |
| Airwallex | airwallex | 502 |  |
| AtoB | atob | 9 |  |
| Atrato | atrato | 1 |  |
| Avallon AI | avallon | 3 |  |
| Bankjoy | bankjoy | 12 |  |
| Belvo | belvo | 3 |  |
| Blee | blee | 5 |  |
| Bluedot | bluedot | 3 |  |
| Bree | bree | 13 |  |
| Bretton AI | brettonai | 6 |  |
| Casca | casca | 7 |  |
| Chariot | chariot | 19 |  |
| Chestnut | chestnut | 4 |  |
| Dave | dave | 7 |  |
| Event Horizon Labs | event-horizon-labs | 1 |  |
| Fernstone | fernstone | 4 |  |
| FINNY AI | finny | 8 |  |
| Greenboard | greenboard | 6 |  |
| Hedge | hedge | 16 |  |
| Heron | herondata | 6 |  |
| Kalshi | kalshi | 49 |  |
| Modern Treasury | moderntreasury | 9 |  |
| Mollie | mollie | 46 |  |
| Nubank | nubank | 99 |  |
| OneChronos | onechronos | 1 |  |
| Pleo | pleo | 25 |  |
| Prelim | prelim | 8 |  |
| Qonto | qonto | 55 |  |
| Rho | rho | 43 |  |
| Solva | solva | 2 |  |
| Spade | spade | 13 |  |
| Sphinx | sphinx | 8 |  |
| Tank Payments | tank-payments | 2 |  |
| Thndr | thndr | 14 |  |
| Tilt | tilt | 2 |  |
| Titan | titan | 11 |  |
| True Link | truelinkfinancial | 3 |  |
| Veritus | veritus | 4 |  |
| Wallbit | wallbit | 2 |  |
| Y Combinator | ycombinator | 11 |  |
| Ziina | ziina | 13 |  |

### Healthcare / Life Sciences
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Adaptyv | adaptyv | 34 |  |
| AIOS | aios | 18 |  |
| Ambience Healthcare | ambiencehealthcare | 19 |  |
| Anthrogen | anthrogen | 8 |  |
| Arini | arini | 2 |  |
| Axle Health | axle-health | 4 |  |
| Blueberry Pediatrics | blueberrypediatrics | 8 |  |
| Bunkerhill Health | bunkerhillhealth | 6 |  |
| Camber | camber | 15 |  |
| Candid Health | candidhealth | 36 |  |
| CareMessage | caremessage | 7 |  |
| Claim Health | claim-health | 9 |  |
| Clarion | clarion | 8 |  |
| Color Health | color-health | 19 | Population health genomics |
| Commure | commure | 84 |  |
| Decoda Health | decodahealth | 2 |  |
| Dodo | dodo | 8 |  |
| Finni Health | finni-health | 149 |  |
| Flint | flint | 8 |  |
| Fortuna Health | fortuna-health | 3 |  |
| Headway | headway | 86 |  |
| HealthSherpa | healthsherpa | 1 |  |
| Hims & Hers | hims-and-hers | 154 | Telehealth / DTC |
| Insitro | insitro | 14 |  |
| Invert | invert | 6 |  |
| Kivo Health | kivo-health | 5 |  |
| Klarify | klarify | 2 |  |
| Knowtex | knowtex | 5 |  |
| Latent | latent | 25 |  |
| Legion Health | legionhealth | 158 |  |
| Mednet | mednet | 5 |  |
| Metriport | metriport | 17 |  |
| Probably Genetic | probablygenetic | 4 |  |
| Serif Health | serifhealth | 2 |  |
| Tempo | tempo | 9 |  |
| Triomics | triomics | 14 |  |
| Vera Health | verahealth | 11 |  |
| Verse Medical | versemedical | 35 |  |
| Vitalize | vitalize | 18 |  |

### Consumer / Marketplace
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| AnswerThis | answerthis | 2 |  |
| Babbel | babbel | 10 |  |
| BeReal | bereal | 28 |  |
| Bumble | bumbleinc | 22 |  |
| Clipboard | clipboard | 41 |  |
| Eight Sleep | eightsleep | 42 |  |
| Enpal | enpal | 149 |  |
| Hotplate | hotplate | 3 |  |
| Innate | innate | 3 |  |
| Mosaic | mosaic | 5 |  |
| Novig | novig | 15 |  |
| Patreon | patreon | 13 |  |
| Pax Historia | pax-historia | 2 |  |
| Quora | quora | 8 |  |
| Short Story | shortstory | 18 |  |
| Snackpass | snackpass | 1 |  |
| Spellbrush | spellbrush | 10 |  |
| Squire Technologies | getsquire | 2 |  |
| Substack | substack | 16 |  |
| Too Good To Go | toogoodtogo | 44 |  |
| Tsenta | tsenta | 1 |  |
| Tuesday Labs | tuesday-labs | 1 |  |

### UK / Europe Tech
| Company | Token | ~Jobs | Notes |
|---------|-------|-------|-------|
| Accurx | accurx | 13 |  |
| Alan | alan | 121 |  |
| Anima | anima | 8 |  |
| Aspora | aspora | 7 |  |
| Back Market | backmarket | 31 |  |
| Billie | billie | 2 |  |
| Birdie | birdie | 1 |  |
| CircuitHub | circuithub | 8 |  |
| ClaimSorted | claimsorted | 15 |  |
| Comena | comena | 6 |  |
| Conveo | conveo | 13 |  |
| Cosine | cosine | 8 |  |
| Deepset | deepsetai | 3 |  |
| Duffel | duffel | 10 |  |
| Dust | dust | 26 |  |
| Elliptic | elliptic | 25 |  |
| Elyos AI | elyos | 11 |  |
| Encord | encord | 39 |  |
| Finary.com | finary | 7 |  |
| Finto | finto | 7 |  |
| Fleek | fleek | 10 |  |
| Formance | formance | 4 |  |
| Forto | forto | 10 |  |
| Freetrade | freetrade | 4 |  |
| H Company | hcompany | 33 |  |
| Happl | happl | 4 |  |
| Healthtech 1 | healthtech-1 | 7 |  |
| Hopper | hopper | 20 |  |
| Improbable | improbable | 4 |  |
| Juro | juro | 1 |  |
| Langdock | langdock | 20 |  |
| LemFi | lemfi | 15 |  |
| Lemon Markets | lemon-markets | 16 |  |
| Lendable | lendable | 66 |  |
| Lightdash | lightdash | 2 |  |
| Lucis | lucis | 14 |  |
| Marshmallow | marshmallow | 15 |  |
| Mercura | mercura | 10 |  |
| Meticulous | meticulous | 6 |  |
| Moss | moss | 29 |  |
| Motorway | motorway | 17 |  |
| Multiverse | multiverse | 28 |  |
| n8n | n8n | 41 |  |
| Nabla | nabla | 11 |  |
| OakNorth | oaknorth | 20 |  |
| Oneleet | oneleet | 8 |  |
| Owkin | owkin | 5 |  |
| Paddle | paddle | 15 |  |
| Permutive | permutive | 1 |  |
| Photoroom | photoroom | 12 |  |
| Pliant | pliant | 37 |  |
| PowerUs | powerus | 2 |  |
| Primer (payments) | primer | 26 | Primer.io payments, London |
| Proxima Fusion | proxima-fusion | 54 |  |
| Quantexa | quantexa | 30 |  |
| Solve Intelligence | solveintelligence | 17 |  |
| Supercell | supercell | 38 |  |
| Taktile | taktile | 37 |  |
| Tekton Dynamics | tekton-dynamics | 2 |  |
| telli | telli | 19 |  |
| The Exploration Company | the-exploration-company | 101 |  |
| Thought Machine | thought-machine | 40 |  |
| Trainline | trainline | 33 |  |
| Trigger.dev | triggerdev | 6 |  |
| Unmind | unmind | 1 |  |
| Upflow | upflow | 2 |  |
| Upvest | upvest | 15 |  |
| Verto | verto | 1 |  |
| voize | voize | 47 |  |
| What3words | what3words | 5 |  |
| Zego | zego | 42 |  |
| Zeit AI | zeit-ai | 7 |  |

---

## Lever Boards (109 verified)


### AI / ML
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Zilliz | zilliz | 11 |  |

### HR Tech / TA Tech
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| 15Five | 15five | 1 | HR tech |
| 360Learning | 360learning | 40 |  |
| CoderPad | coderpad | 6 |  |
| Employ | employ | 2 |  |
| Findem | findem | 4 |  |
| Iru (formerly Kandji) | iru | 22 | Formerly Kandji |
| Symplicity | symplicity | 1 |  |

### Growth-Stage Tech
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Aircall | aircall | 77 |  |
| Aleph | aleph | 102 |  |
| Anchorage Digital | anchorage | 23 |  |
| Bolster | bolster | 4 |  |
| Canary Technologies | canarytechnologies | 32 |  |
| CaptivateIQ | captivateiq | 24 |  |
| Cloudinary | cloudinary | 10 |  |
| Copia | copia | 4 |  |
| doola | doola | 7 |  |
| Emi Labs | emilabs | 12 |  |
| Epsilon3 | epsilon3 | 4 |  |
| Finch | finch | 12 |  |
| Fleetzero | fleetzero | 3 |  |
| Fly.io | fly | 1 |  |
| Glide | glide | 24 |  |
| Gopuff | gopuff | 802 |  |
| Gridware | gridware | 19 |  |
| Handoff | handoff | 10 |  |
| Hive | hive | 74 |  |
| Living Carbon | livingcarbon | 1 |  |
| Mashgin | mashgin | 13 |  |
| MaverickX | maverickx | 7 |  |
| Meesho | meesho | 58 |  |
| Moonpay | moonpay | 17 |  |
| Multiply Labs | multiplylabs | 8 |  |
| Netomi | netomi | 20 |  |
| Olo | olo | 10 |  |
| Outreach | outreach | 24 |  |
| PickTrace | picktrace | 2 |  |
| Prosper | prosper | 16 |  |
| Pyka | pyka | 22 |  |
| Rigetti Computing | rigetti | 17 |  |
| Shield AI | shieldai | 619 |  |
| Skyways | skyways | 21 |  |
| Smartcuts | smartcuts | 2 |  |
| Snappr | snappr | 16 |  |
| Spotify | spotify | 81 |  |
| Superside | superside | 17 |  |
| VergeSense | vergesense | 2 |  |

### Enterprise SaaS
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Palantir | palantir | 310 | Data analytics / defense |
| Veeva | veeva | 929 |  |

### Enterprise / Global
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Achievers | achievers | 15 |  |
| Healx | healx | 1 |  |
| Immutable | immutable | 4 |  |
| Toptal | toptal | 28 |  |
| Vestiaire Collective | vestiairecollective | 9 |  |

### Unicorns
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| ActiveCampaign | activecampaign | 12 |  |
| Animoca Brands | animocabrands | 12 |  |
| Articulate | articulate | 1 |  |
| Coupa | coupa | 34 |  |
| CRED | cred | 7 |  |
| Deliverect | deliverect | 29 |  |
| dLocal | dlocal | 52 |  |
| Dream Games | dreamgames | 20 |  |
| FloQast | floqast | 34 |  |
| GoodLeap | goodleap | 30 |  |
| Houzz | houzz | 3 |  |
| Jumpcloud | jumpcloud | 33 |  |
| Kabam | kabam | 24 |  |
| Kavak | kavak | 11 |  |
| Lalamove | lalamove | 168 |  |
| Matillion | matillion | 20 |  |
| Mindtickle | mindtickle | 20 |  |
| Ninja Van | ninjavan | 141 |  |
| Nium | nium | 19 |  |
| Paytm | paytm | 182 |  |
| Pivotal | pivotal | 23 |  |
| Sysdig | sysdig | 34 |  |
| Veepee | veepee | 111 |  |
| YouniteD | younited | 6 |  |
| Zeta | zeta | 24 |  |
| Zoox | zoox | 239 |  |

### Fintech
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| FamPay | fampay | 17 |  |
| Fintual | fintual | 13 |  |
| Jeeves | tryjeeves | 84 |  |
| STARK BANK | starkbank | 4 |  |
| Two Dots | twodots | 4 |  |
| Wealthfront | wealthfront | 24 |  |
| Zippi | zippi | 4 |  |

### Healthcare / Life Sciences
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Included Health | includedhealth | 51 |  |
| Lyra Health | lyrahealth | 512 |  |
| PostEra | postera | 2 |  |
| Ro | ro | 55 | Telehealth |
| Synapticure | synapticure | 7 |  |
| Verifiable | verifiable | 2 |  |
| Volta Labs | voltalabs | 3 |  |

### Consumer / Marketplace
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Contentsquare | contentsquare | 20 |  |
| Match Group | matchgroup | 65 |  |
| Moonpig | moonpig | 12 |  |
| Tendo | tendo | 4 |  |
| Text.ai | text | 5 |  |
| Tovala | tovala | 10 |  |

### UK / Europe Tech
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Agicap | agicap | 25 |  |
| BlaBlaCar | blablacar | 9 |  |
| Farfetch | farfetch | 44 |  |
| Finn | finn | 28 |  |
| Malt | malt | 25 |  |
| Mytos | mytos | 13 |  |
| Pigment | pigment | 140 |  |
| Swile | swile | 32 |  |
| Zopa | zopa | 34 |  |

---

## Workable Boards (37 verified)


### HR Tech / TA Tech
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Fuel50 | fuel50 | 3 |  |

### Growth-Stage Tech
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Aerones | aerones | 35 |  |
| HOKALI | hokali | 90 |  |
| Jasper.ai | jasper | 1 |  |
| Leena AI | leena-ai | 14 |  |
| Panorama Education | panorama-education | 8 |  |
| Platzi | platzi | 20 |  |
| Povio | povio | 19 |  |
| Rational | rational | 7 |  |
| Raven | raven | 37 |  |
| Ryse | ryse | 18 |  |
| Sorting Robotics | sorting-robotics | 12 |  |
| testRigor | testrigor | 4 |  |
| Text Blaze | blaze | 2 |  |
| Vulcan Technologies | vulcan | 37 |  |
| Writesonic | writesonic | 7 |  |

### Enterprise / Global
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Hugging Face | huggingface | 6 |  |
| Kroo | kroo | 19 |  |
| Lantum | lantum | 1 |  |
| Patchwork Health | patchworkhealth | 2 |  |
| Rokt | rokt | 12 |  |
| Starling Bank | starling-bank | 99 |  |
| Workmotion | workmotion | 39 |  |
| Yapily | yapily | 5 |  |
| Zoopla | zoopla | 3 |  |

### Unicorns
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Apna | apna | 145 |  |
| Exotec | exotec | 82 |  |
| Mercari | mercari | 135 |  |
| SmartNews | smartnews | 25 |  |
| Tresata | tresata | 1 |  |

### Fintech
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Ajaib | ajaib | 53 |  |
| Tint | tint | 1 |  |

### Healthcare / Life Sciences
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| Helium Health | helium-health | 8 |  |
| Malama Health | malama-health | 29 |  |
| Measured | measured | 4 |  |
| TetraScience | tetrascience | 32 |  |

### Consumer / Marketplace
| Company | Slug | ~Jobs | Notes |
|---------|-------|-------|-------|
| AirHelp | airhelp | 18 |  |

---

## SmartRecruiters Boards (68 verified)


### HR Tech / TA Tech
| Company | Company ID | ~Jobs | Notes |
|---------|-------|-------|-------|
| AmazingHiring | amazinghiring | 5 |  |
| Coople | coople | 1 |  |
| Gloat | gloat | 7 |  |
| Goodhire | goodhire | 1 |  |
| Harver | harver | 4 |  |
| HiBob | hibob | 1 |  |
| Hirevue | hirevue | 2 |  |
| Paradox | paradox | 6 |  |
| Pymetrics | pymetrics | 3 |  |
| Veremark | veremark | 6 |  |
| WayUp | wayup | 2 |  |

### Growth-Stage Tech
| Company | Company ID | ~Jobs | Notes |
|---------|-------|-------|-------|
| ElectroNeek | electroneek | 2 |  |
| ModernLoop | modernloop | 15 |  |
| Navattic | navattic | 1 |  |
| Pahamify | pahamify | 1 |  |
| Shaped | shaped | 9 |  |
| Skill-lync | skill-lync | 3 |  |
| Statiq. | statiq | 1 |  |
| Unschool | unschool | 1 |  |
| Vendease | vendease | 5 |  |

### Enterprise / Global
| Company | Company ID | ~Jobs | Notes |
|---------|-------|-------|-------|
| ASOS | asos | 64 |  |
| Auto1 Group | auto1 | 687 |  |
| Bosch | boschgroup | 5061 |  |
| Canva | canva | 118 |  |
| Continental | continental | 568 |  |
| Delivery Hero | deliveryhero | 939 |  |
| Fiverr | fiverr | 3 |  |
| Gousto | gousto | 7 |  |
| Grab | grab | 446 |  |
| Judo Bank | judobank | 24 |  |
| Omio | omio | 2 |  |
| Reward Gateway | rewardgateway | 9 |  |
| Rocket Internet | rocketinternet | 17 |  |
| ServiceNow | servicenow | 686 |  |
| Wise | wise | 416 |  |
| Zenefits | zenefits | 3 |  |

### Unicorns
| Company | Company ID | ~Jobs | Notes |
|---------|-------|-------|-------|
| ByteDance | bytedance | 2 |  |
| CARS24 | cars24 | 1 |  |
| Devoted Health | devotedhealth | 2 |  |
| Ecovadis | ecovadis | 24 |  |
| Freshworks | freshworks | 131 |  |
| IAD | iad | 16 |  |
| iTutorGroup | itutorgroup | 1 |  |
| LetsGetChecked | letsgetchecked | 1 |  |
| M1 Finance | m1finance | 1 |  |
| Nexthink | nexthink | 75 |  |
| NoBroker | nobroker | 1 |  |
| Polygon Technology | polygontechnology | 2 |  |
| Rebel Foods | rebelfoods | 1 |  |
| Sportradar | sportradar | 95 |  |
| Upstox | upstox | 1 |  |
| VIPKID | vipkid | 1 |  |
| Wayfair | wayfair | 1 |  |
| WeWork | wework | 2 |  |
| Xiaomi | xiaomi | 1 |  |

### Fintech
| Company | Company ID | ~Jobs | Notes |
|---------|-------|-------|-------|
| BukuWarung | bukuwarung | 3 |  |
| Finku | finku | 1 |  |
| Kodo | kodo | 1 |  |

### Healthcare / Life Sciences
| Company | Company ID | ~Jobs | Notes |
|---------|-------|-------|-------|
| AlemHealth | alemhealth | 1 |  |
| Dashlabs.ai | dashlabsai | 5 |  |
| Loop Health | loophealth | 1 |  |
| PicnicAI | picnic | 2 |  |

### Consumer / Marketplace
| Company | Company ID | ~Jobs | Notes |
|---------|-------|-------|-------|
| Bellabeat | bellabeat | 1 |  |
| Lokal | lokal | 9 |  |
| Vinci Games | vincigames | 1 |  |
| Yassir | yassir | 6 |  |

### UK / Europe Tech
| Company | Company ID | ~Jobs | Notes |
|---------|-------|-------|-------|
| HireSweet | hiresweet | 2 |  |
| Kombo | kombo | 156 |  |

---

## Adding Your Own Companies

**To find a board token:**

1. Go to their careers page
2. Click any job posting
3. Look at the URL:
   - `boards.greenhouse.io/COMPANY/jobs/123` -> token is `COMPANY`
   - `job-boards.greenhouse.io/COMPANY/jobs/123` -> token is `COMPANY`
   - `jobs.lever.co/COMPANY/abc-123` -> slug is `COMPANY`
   - `jobs.ashbyhq.com/COMPANY` -> Ashby token is `COMPANY`
   - `apply.workable.com/COMPANY/` -> Workable slug is `COMPANY`
   - `jobs.smartrecruiters.com/COMPANY/123` or `careers.smartrecruiters.com/COMPANY` -> SmartRecruiters ID is `COMPANY`
4. Add it to the appropriate section above

**Or run the discovery script:**

```bash
python3 discover_boards.py --company "Company Name"
```

This tries common token patterns across all 5 platforms and reports which one works.

**To discover boards for a whole list:**

```bash
python3 discover_boards.py --file my_companies.txt --output results.md
```

---

## Search Priority

When running a search, the agent should:
1. Start with companies matching the user's industry preferences
2. Always include AI/ML companies (they hire across all functions)
3. Always include HR Tech / TA Tech companies (if user has People/TA background)
4. Search at least 20 boards per run for meaningful coverage
5. Skip any board that returns a 404 without retrying
6. Prioritize boards with 50+ jobs (more likely to have diverse roles)
