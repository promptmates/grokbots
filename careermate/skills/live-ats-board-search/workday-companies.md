# Workday Companies

Public Workday career sites for the OPT-IN Workday search (`search_boards.py --include-workday`). Never searched by default.

> This checks public Workday job pages directly. Workday's site terms restrict automated access, so it's offered as an optional, use-at-your-own-discretion feature. It runs slowly, reads job listings only, and never logs in or applies.

112 sites, each verified Oct 17 2026 with one read-only CXS request and checked against the tenant's robots.txt (sites a tenant disallows in robots.txt are not listed). ~Jobs is that day's total (Workday caps reported totals at 2000). Defense-only employers are deliberately excluded.

Columns: Tenant and wdN form the host `https://<tenant>.wd<N>.myworkdayjobs.com`; Site is the career-site name. Search endpoint: `POST https://<tenant>.wd<N>.myworkdayjobs.com/wday/cxs/<tenant>/<site>/jobs` with `{"appliedFacets":{},"limit":20,"offset":0,"searchText":"..."}`. Public posting URL: `https://<tenant>.wd<N>.myworkdayjobs.com/en-US/<site><externalPath>`.

Add companies with `../discover-ats-boards/discover_workday.py --append <this file>`; re-check the list with `discover_workday.py --verify <this file>`. Section headings can be skipped with `search_boards.py --exclude-section`.

## Workday Boards

### Texas Enterprises
| Company | Tenant | wdN | Site | Careers URL | ~Jobs |
|---------|--------|-----|------|-------------|-------|
| Academy Sports | academy | wd1 | Careers | https://academy.wd1.myworkdayjobs.com/en-US/Careers | 881 |
| Applied Materials | amat | wd1 | External | https://amat.wd1.myworkdayjobs.com/en-US/External | 2000 |
| Baker Hughes | bakerhughes | wd5 | BakerHughes | https://bakerhughes.wd5.myworkdayjobs.com/en-US/BakerHughes | 716 |
| CrowdStrike | crowdstrike | wd5 | crowdstrikecareers | https://crowdstrike.wd5.myworkdayjobs.com/en-US/crowdstrikecareers | 357 |
| Flex | flextronics | wd1 | Careers | https://flextronics.wd1.myworkdayjobs.com/en-US/Careers | 1461 |
| Frost Bank | frostbank | wd5 | External | https://frostbank.wd5.myworkdayjobs.com/en-US/External | 181 |
| Hewlett Packard Enterprise | hpe | wd5 | ACJobSite | https://hpe.wd5.myworkdayjobs.com/en-US/ACJobSite | 1604 |
| iHeartMedia | iheartmedia | wd5 | External_iHM | https://iheartmedia.wd5.myworkdayjobs.com/en-US/External_iHM | 305 |
| Kimberly-Clark | kimberlyclark | wd1 | GLOBAL | https://kimberlyclark.wd1.myworkdayjobs.com/en-US/GLOBAL | 160 |
| McKesson | mckesson | wd3 | External_Careers | https://mckesson.wd3.myworkdayjobs.com/en-US/External_Careers | 680 |
| NXP Semiconductors | nxp | wd3 | careers | https://nxp.wd3.myworkdayjobs.com/en-US/careers | 809 |
| Q2 | q2ebanking | wd5 | Q2 | https://q2ebanking.wd5.myworkdayjobs.com/en-US/Q2 | 59 |
| Rackspace | rackspace | wd1 | External | https://rackspace.wd1.myworkdayjobs.com/en-US/External | 63 |
| SailPoint | sailpoint | wd1 | SailPoint | https://sailpoint.wd1.myworkdayjobs.com/en-US/SailPoint | 105 |
| Silicon Labs | silabs | wd1 | SiliconLabsCareers | https://silabs.wd1.myworkdayjobs.com/en-US/SiliconLabsCareers | 87 |
| Sysco | sysco | wd5 | syscocareers | https://sysco.wd5.myworkdayjobs.com/en-US/syscocareers | 2000 |
| Toyota North America | toyota | wd503 | TMNA | https://toyota.wd503.myworkdayjobs.com/en-US/TMNA | 117 |
| University of Texas at Austin | utaustin | wd1 | UTstaff | https://utaustin.wd1.myworkdayjobs.com/en-US/UTstaff | 626 |
| USAA | usaa | wd1 | USAAJOBSWD | https://usaa.wd1.myworkdayjobs.com/en-US/USAAJOBSWD | 211 |

### Tech / Software / Semiconductors
| Company | Tenant | wdN | Site | Careers URL | ~Jobs |
|---------|--------|-----|------|-------------|-------|
| Adobe | adobe | wd5 | external_experienced | https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced | 305 |
| Analog Devices | analogdevices | wd1 | External | https://analogdevices.wd1.myworkdayjobs.com/en-US/External | 821 |
| Autodesk | autodesk | wd1 | Ext | https://autodesk.wd1.myworkdayjobs.com/en-US/Ext | 355 |
| Broadcom | broadcom | wd1 | External_Career | https://broadcom.wd1.myworkdayjobs.com/en-US/External_Career | 356 |
| Cadence | cadence | wd1 | External_Careers | https://cadence.wd1.myworkdayjobs.com/en-US/External_Careers | 659 |
| Ciena | ciena | wd5 | Careers | https://ciena.wd5.myworkdayjobs.com/en-US/Careers | 147 |
| Entegris | entegris | wd1 | EntegrisCareers | https://entegris.wd1.myworkdayjobs.com/en-US/EntegrisCareers | 617 |
| HP Inc | hp | wd5 | ExternalCareerSite | https://hp.wd5.myworkdayjobs.com/en-US/ExternalCareerSite | 839 |
| Intel | intel | wd1 | External | https://intel.wd1.myworkdayjobs.com/en-US/External | 735 |
| KLA | kla | wd1 | Search | https://kla.wd1.myworkdayjobs.com/en-US/Search | 1085 |
| Marvell | marvell | wd1 | MarvellCareers | https://marvell.wd1.myworkdayjobs.com/en-US/MarvellCareers | 327 |
| Micron | micron | wd1 | External | https://micron.wd1.myworkdayjobs.com/en-US/External | 3174 |
| Motorola Solutions | motorolasolutions | wd5 | Careers | https://motorolasolutions.wd5.myworkdayjobs.com/en-US/Careers | 915 |
| NVIDIA | nvidia | wd5 | NVIDIAExternalCareerSite | https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite | 2000 |
| Red Hat | redhat | wd5 | Jobs | https://redhat.wd5.myworkdayjobs.com/en-US/Jobs | 171 |
| Salesforce | salesforce | wd12 | External_Career_Site | https://salesforce.wd12.myworkdayjobs.com/en-US/External_Career_Site | 1554 |
| Semrush | semrush | wd5 | semrushcareers | https://semrush.wd5.myworkdayjobs.com/en-US/semrushcareers | 17 |
| Workday | workday | wd5 | Workday | https://workday.wd5.myworkdayjobs.com/en-US/Workday | 388 |
| Workiva | workiva | wd503 | careers | https://workiva.wd503.myworkdayjobs.com/en-US/careers | 109 |
| Zendesk | zendesk | wd1 | zendesk | https://zendesk.wd1.myworkdayjobs.com/en-US/zendesk | 139 |

### Healthcare / Life Sciences
| Company | Tenant | wdN | Site | Careers URL | ~Jobs |
|---------|--------|-----|------|-------------|-------|
| Abbott | abbott | wd5 | abbottcareers | https://abbott.wd5.myworkdayjobs.com/en-US/abbottcareers | 2000 |
| Agilent | agilent | wd5 | Agilent_Careers | https://agilent.wd5.myworkdayjobs.com/en-US/Agilent_Careers | 373 |
| Alcon | alcon | wd5 | careers_alcon | https://alcon.wd5.myworkdayjobs.com/en-US/careers_alcon | 386 |
| Amgen | amgen | wd1 | Careers | https://amgen.wd1.myworkdayjobs.com/en-US/Careers | 1695 |
| AstraZeneca | astrazeneca | wd3 | Careers | https://astrazeneca.wd3.myworkdayjobs.com/en-US/Careers | 1097 |
| Baxter | baxter | wd1 | baxter | https://baxter.wd1.myworkdayjobs.com/en-US/baxter | 492 |
| BD | bdx | wd1 | EXTERNAL_CAREER_SITE_USA | https://bdx.wd1.myworkdayjobs.com/en-US/EXTERNAL_CAREER_SITE_USA | 660 |
| Biogen | biibhr | wd3 | external | https://biibhr.wd3.myworkdayjobs.com/en-US/external | 269 |
| Bristol Myers Squibb | bristolmyerssquibb | wd5 | BMS | https://bristolmyerssquibb.wd5.myworkdayjobs.com/en-US/BMS | 655 |
| Cardinal Health | cardinalhealth | wd1 | EXT | https://cardinalhealth.wd1.myworkdayjobs.com/en-US/EXT | 828 |
| Centene | centene | wd5 | Centene_External | https://centene.wd5.myworkdayjobs.com/en-US/Centene_External | 353 |
| CenterWell (Humana) | humana | wd5 | CenterWell_External_Career_Site | https://humana.wd5.myworkdayjobs.com/en-US/CenterWell_External_Career_Site | 1805 |
| Cigna | cigna | wd5 | cignacareers | https://cigna.wd5.myworkdayjobs.com/en-US/cignacareers | 523 |
| CVS Health | cvshealth | wd1 | CVS_Health_Careers | https://cvshealth.wd1.myworkdayjobs.com/en-US/CVS_Health_Careers | 19247 |
| Danaher | danaher | wd1 | DanaherJobs | https://danaher.wd1.myworkdayjobs.com/en-US/DanaherJobs | 1439 |
| Edwards Lifesciences | edwards | wd5 | EdwardsCareers | https://edwards.wd5.myworkdayjobs.com/en-US/EdwardsCareers | 396 |
| Elevance Health | elevancehealth | wd1 | ANT | https://elevancehealth.wd1.myworkdayjobs.com/en-US/ANT | 236 |
| Gilead | gilead | wd1 | gileadcareers | https://gilead.wd1.myworkdayjobs.com/en-US/gileadcareers | 413 |
| GSK | gsk | wd5 | GSKCareers | https://gsk.wd5.myworkdayjobs.com/en-US/GSKCareers | 668 |
| Humana | humana | wd5 | Humana_External_Career_Site | https://humana.wd5.myworkdayjobs.com/en-US/Humana_External_Career_Site | 260 |
| Illumina | illumina | wd1 | illumina-careers | https://illumina.wd1.myworkdayjobs.com/en-US/illumina-careers | 164 |
| Insulet | insulet | wd5 | insuletcareers | https://insulet.wd5.myworkdayjobs.com/en-US/insuletcareers | 199 |
| IQVIA | iqvia | wd1 | IQVIA | https://iqvia.wd1.myworkdayjobs.com/en-US/IQVIA | 1855 |
| Labcorp | labcorp | wd1 | External | https://labcorp.wd1.myworkdayjobs.com/en-US/External | 1848 |
| Medtronic | medtronic | wd1 | MedtronicCareers | https://medtronic.wd1.myworkdayjobs.com/en-US/MedtronicCareers | 1045 |
| Merck | msd | wd5 | SearchJobs | https://msd.wd5.myworkdayjobs.com/en-US/SearchJobs | 971 |
| Moderna | modernatx | wd1 | M_tx | https://modernatx.wd1.myworkdayjobs.com/en-US/M_tx | 268 |
| Novartis | novartis | wd3 | Novartis_Careers | https://novartis.wd3.myworkdayjobs.com/en-US/Novartis_Careers | 875 |
| Organon | organon | wd5 | SearchJobs | https://organon.wd5.myworkdayjobs.com/en-US/SearchJobs | 110 |
| Pfizer | pfizer | wd1 | PfizerCareers | https://pfizer.wd1.myworkdayjobs.com/en-US/PfizerCareers | 564 |
| Philips | philips | wd3 | jobs-and-careers | https://philips.wd3.myworkdayjobs.com/en-US/jobs-and-careers | 783 |
| Regeneron | regeneron | wd1 | Careers | https://regeneron.wd1.myworkdayjobs.com/en-US/Careers | 590 |
| ResMed | resmed | wd3 | ResMed_External_Careers | https://resmed.wd3.myworkdayjobs.com/en-US/ResMed_External_Careers | 268 |
| Roche | roche | wd3 | roche-ext | https://roche.wd3.myworkdayjobs.com/en-US/roche-ext | 1230 |
| Sanofi | sanofi | wd3 | SanofiCareers | https://sanofi.wd3.myworkdayjobs.com/en-US/SanofiCareers | 996 |
| Stryker | stryker | wd1 | StrykerCareers | https://stryker.wd1.myworkdayjobs.com/en-US/StrykerCareers | 1480 |
| Teladoc | teladoc | wd503 | teladochealth_is_hiring | https://teladoc.wd503.myworkdayjobs.com/en-US/teladochealth_is_hiring | 60 |
| Viatris | viatris | wd5 | External | https://viatris.wd5.myworkdayjobs.com/en-US/External | 356 |
| Zoetis | zoetis | wd5 | zoetis | https://zoetis.wd5.myworkdayjobs.com/en-US/zoetis | 124 |

### Financial Services / Professional Services
| Company | Tenant | wdN | Site | Careers URL | ~Jobs |
|---------|--------|-----|------|-------------|-------|
| Accenture | accenture | wd103 | AccentureCareers | https://accenture.wd103.myworkdayjobs.com/en-US/AccentureCareers | 2000 |
| Bank of America | ghr | wd1 | Lateral-US | https://ghr.wd1.myworkdayjobs.com/en-US/Lateral-US | 1943 |
| BlackRock | blackrock | wd1 | BlackRock_Professional | https://blackrock.wd1.myworkdayjobs.com/en-US/BlackRock_Professional | 292 |
| Capital One | capitalone | wd12 | Capital_One | https://capitalone.wd12.myworkdayjobs.com/en-US/Capital_One | 1976 |
| Crowe | crowe | wd12 | External_Careers | https://crowe.wd12.myworkdayjobs.com/en-US/External_Careers | 177 |
| Fidelity | fmr | wd1 | FidelityCareers | https://fmr.wd1.myworkdayjobs.com/en-US/FidelityCareers | 773 |
| Mastercard | mastercard | wd1 | CorporateCareers | https://mastercard.wd1.myworkdayjobs.com/en-US/CorporateCareers | 1113 |
| Morgan Stanley | ms | wd5 | External | https://ms.wd5.myworkdayjobs.com/en-US/External | 1260 |
| Nasdaq | nasdaq | wd1 | Global_External_Site | https://nasdaq.wd1.myworkdayjobs.com/en-US/Global_External_Site | 164 |
| PayPal | paypal | wd1 | jobs | https://paypal.wd1.myworkdayjobs.com/en-US/jobs | 335 |
| Prudential | pru | wd5 | Careers | https://pru.wd5.myworkdayjobs.com/en-US/Careers | 164 |
| PwC | pwc | wd3 | Global_Experienced_Careers | https://pwc.wd3.myworkdayjobs.com/en-US/Global_Experienced_Careers | 3895 |
| S&P Global | spgi | wd5 | SPGI_Careers | https://spgi.wd5.myworkdayjobs.com/en-US/SPGI_Careers | 294 |
| State Street | statestreet | wd1 | Global | https://statestreet.wd1.myworkdayjobs.com/en-US/Global | 1262 |
| Thomson Reuters | thomsonreuters | wd5 | External_Career_Site | https://thomsonreuters.wd5.myworkdayjobs.com/en-US/External_Career_Site | 467 |
| Travelers | travelers | wd5 | External | https://travelers.wd5.myworkdayjobs.com/en-US/External | 402 |
| Visa | visa | wd5 | Visa | https://visa.wd5.myworkdayjobs.com/en-US/Visa | 833 |
| Wells Fargo | wf | wd1 | WellsFargoJobs | https://wf.wd1.myworkdayjobs.com/en-US/WellsFargoJobs | 1534 |

### Consumer / Media / Industrial
| Company | Tenant | wdN | Site | Careers URL | ~Jobs |
|---------|--------|-----|------|-------------|-------|
| 3M | 3m | wd1 | Search | https://3m.wd1.myworkdayjobs.com/en-US/Search | 744 |
| Chevron | chevron | wd5 | jobs | https://chevron.wd5.myworkdayjobs.com/en-US/jobs | 146 |
| Coca-Cola | coke | wd1 | coca-cola-careers | https://coke.wd1.myworkdayjobs.com/en-US/coca-cola-careers | 205 |
| Disney | disney | wd5 | disneycareer | https://disney.wd5.myworkdayjobs.com/en-US/disneycareer | 416 |
| Dynata | dynata | wd108 | careers | https://dynata.wd108.myworkdayjobs.com/en-US/careers | 16 |
| Expedia Group | expedia | wd108 | search | https://expedia.wd108.myworkdayjobs.com/en-US/search | 181 |
| GE Vernova | gevernova | wd5 | Vernova_ExternalSite | https://gevernova.wd5.myworkdayjobs.com/en-US/Vernova_ExternalSite | 2225 |
| General Motors | generalmotors | wd5 | Careers_GM | https://generalmotors.wd5.myworkdayjobs.com/en-US/Careers_GM | 822 |
| Porch Group | porch | wd1 | careers | https://porch.wd1.myworkdayjobs.com/en-US/careers | 51 |
| Procter & Gamble | pg | wd5 | 1000 | https://pg.wd5.myworkdayjobs.com/en-US/1000 | 849 |
| Snap | snapchat | wd1 | snap | https://snapchat.wd1.myworkdayjobs.com/en-US/snap | 205 |
| Sony | sonyglobal | wd1 | SonyGlobalCareers | https://sonyglobal.wd1.myworkdayjobs.com/en-US/SonyGlobalCareers | 118 |
| Target | target | wd5 | targetcareers | https://target.wd5.myworkdayjobs.com/en-US/targetcareers | 2000 |
| Warner Bros. Discovery | warnerbros | wd5 | global | https://warnerbros.wd5.myworkdayjobs.com/en-US/global | 298 |
| Yahoo | ouryahoo | wd5 | careers | https://ouryahoo.wd5.myworkdayjobs.com/en-US/careers | 91 |
| Zillow | zillow | wd5 | Zillow_Group_External | https://zillow.wd5.myworkdayjobs.com/en-US/Zillow_Group_External | 179 |
