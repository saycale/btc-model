# Cross-scale Bitcoin price model: power law × saturation ceiling × halving cycles

An interactive page: three layers, four sliders, three diagnostics, five falsification criteria, monthly resolution from July 2010 to April 2040.

**Open the model →** https://saycale.github.io/btc-model/

**Русская версия →** https://saycale.github.io/btc-model/ru.html · [README на русском](README.ru.md)

[![The model, upper panel and controls](screen.en.png)](https://saycale.github.io/btc-model/)

## What this is

Three layers multiplied by one another. Each owns its own time scale, and they are stitched together rather than stacked: the third depends on the second.

**1. A power law** in the age of the network, `P ∝ t^3β`, with age counted in days from the genesis block. The browser now re-estimates the price slope whenever the embedded observations change. With the provisional 9 September 2026 point the full-sample slope is 5.640, exposed as the sensitivity coordinate β = 1.880. This is a price fit, not an independently measured Metcalfe exponent. The address decomposition remains beside it as a co-trend diagnostic and does not feed the forecast.

**2. Saturation** against a limiting number of owners. This layer decides how everything ends. Soft braking, `P = P_trend · L / (P_trend³ + L³)^⅓`, where the plateau `L` is a monetary constraint rather than a consequence of Metcalfe:

```
L = W · A / S        A = $8,447 terminal holding per owner
                     S ≈ 20.7M coins in circulation by the mid-2030s
```

The ceiling enters linearly: be wrong by a factor of two and the plateau moves by a factor of two. `A` is not measured separately — it is the calibration base expressed per person. The outer two quantities are pinned: the base ceiling of 1610M owners (near the middle of the plausible corridor, ~27% of adults) and a terminal capitalisation of $13.6T, about 43% of the value of all the gold ever mined at the 31 August 2026 close. `A` follows from dividing one by the other.

**3. Halving cycles** with the top and the bottom decaying separately. These are the four-year waves inside. Peak 18 months after the halving, trough at 26–30, return to trend by the next halving, cosine interpolation between the nodes.

The third layer is tied to the second by a multiplier ζ:

```
ζ = d_e + (1 − d_e)·φ        φ = g(with saturation) / g(pure power law)
```

φ is the share of the trend's travel that the ceiling lets through — the headroom. A euphoric peak is an overshoot above the trend, and a trend that has come up against the ceiling has almost no room above it. Swings among those who already own require no such headroom, and the share of the cycle that survives the exhaustion of headroom is set by the euphoria decay slider. The link introduces no new constants. At all four historical epochs φ = 1.00 to within half a percent — saturation had not switched on before 2026, and the calibration of layers 1–2 is untouched.

## Sliders and scenarios

The sliders do not pick a desired number. They switch between hypotheses about what happened to the market in the last cycle: was the disappearance of euphoria an irreversible change or a fluke. The four presets sit on a single axis — maturity on the left, speculation on the right:

| Scenario | Ceiling | Euphoria decay | Panic decay | Plateau | H5 peak | H5 trough | Drawdown |
|---|---|---|---|---|---|---|---|
| Cycle faded | 1800 | 0.00 | 1.00 | $735k | $379k | $301k | 21% |
| **Quiet cycle** (base) | 1610 | 0.15 | 0.50 | $657k | $394k | $245k | 38% |
| Cycle returns | 1350 | 0.50 | 0.25 | $551k | $432k | $209k | 52% |
| Cycle never broke | 1300 | 1.00 | 0.00 | $530k | $542k | $169k | 69% |

The column of peaks rises to the right along with the drawdown, which is awkward to read and worth stating plainly: **a high peak in 2029 points to a live cycle, which will be followed by the customary crash.** The scenarios are not «optimistic — base — pessimistic». By the 2035 price the left edge is optimistic; by the October 2029 price the right edge is.

The ceiling does two things at once, which is easy to miss. It sets the plateau level, and through ζ it sets how much of the cycle survives into the 2030s. At the base decays the H5 drawdown runs from 23% at a ceiling of 700M to 40% at 3200 — the troughs almost flatten out at the lower edge.

β is not meant for tuning. It sits on the panel as a check, with a live miss counter under it, and it takes part in the coherence indicator: the thinning of the graph of links comes from custodial holding, which is also what explains the death of euphoria and the removal of the barrier to entry.

## Diagnostics

Three indicators check the reader's settings while advising nothing. Their colour runs from blue through orange to red continuously, without thresholds: each check returns a tension between zero and one, and they combine as independent.

**Coherence indicator.** Five checks, each asking not «is this a good number» but whether one mechanism sits under a pair of settings. *Top and bottom* — the cause that killed euphoria is obliged sooner or later to reach panic. *Decay and ceiling* — institutional custody kills euphoria and removes the barrier to entry at the same time. *Cycle support* — whether the cycle of the 2030s rests on headroom or on an assumption. *Scale and regime* — whether the ceiling takes capitalisation to a level requiring a change of monetary regime, which the model does not contain. *β and institutionalisation* — custodial holding thins the graph of links and pulls the Metcalfe exponent toward n log n by the same process that puts out euphoria and lifts the ceiling, so a shift of β to the left with a live cycle and a shift to the right with a high ceiling both pull cause away from consequence. Three of the five are a direct contradiction and can reach red; the others stay caveats at any slider position.

**Share of amplitude by epoch.** Shows ζ for H5–H7: what the 2030s cycle rests on — the surviving headroom, or the premise that the speculative character of the asset survived on its own. At the base setting it reads H5 87% · H6 33% · H7 17%.

**Misses from the trend.** How many observations lie further than ±0.5 dex from the saturated trend. At the current reference β there are 17 of 195. The control is a sensitivity check; it is not a confidence interval.

Below the chart a fourth block, **what this requires of money**, converts the same trajectory into capitalisation: about $1.58T at the latest close against $13.6T at the plateau. It also shows the average annual increase along the path and the much smaller dollar value of issuance. This is an accounting comparison; it does not show that halvings cease to affect marginal supply or expectations.

## Data

195 observations from July 2010 through 9 September 2026. Completed months are approximate month closes compiled from public sources; the final `$78,587` value is a provisional spot observation dated 9 September, not a monthly close. The series sits in the page source as `OBS`, with `OBS_LAST_DATE` and `OBS_LAST_PROVISIONAL` preventing the partial month from being mislabeled.

The displayed β is the current price slope divided by three. The price/address regression is explicitly labeled a co-trend check and reports a Newey–West HAC(12) uncertainty estimate because monthly residuals are autocorrelated. Owner ceiling, saturation and future cycle amplitudes remain scenarios rather than estimates from the price sample.

## Reproducibility and change control

`data/observations.js` is the single browser data bundle used by both language pages. `data/provenance.json` records the date, kind and update contract for its latest observation; run `python3 tools/validate_data.py` after any change. `model-core.js` contains the shared regression, calibration and permalink mechanics.

The project keeps a versioned [forecast ledger](FORECAST_LEDGER.md). It records a scenario before its target date and is intentionally append-only for open claims. Continuous integration runs data validation, the independent audit tests and JavaScript syntax checks on every push and pull request.

The number of owners is not directly measurable; the 106M figure appears only as a lower industry benchmark in a sensitivity example. Together with `A`, this is the weakest point of the model. Neither the number of owners nor the average holding size is measured separately. The multiplier ζ does not depend on the level anchoring: φ is a ratio of two growth rates.

Addresses are deliberately absent from the plateau calculation. About 57M non-zero addresses are measurable, but there is no defensible one-to-one mapping to owners: one owner may control many addresses, while a custodian can place many owners behind one. The institutionalisation explanation therefore remains a hypothesis until it can be tested against a consistent independent series for beneficial owners or custodied holdings.

## What could falsify this

Five conditions, from the nearest to the most distant. Two are worth naming here.

**Price settles below $58,000.** Then late June 2026 was not the trough of the cycle, and with it collapses the lower node of H4 — the node the decay amplitude is set by. Everything downstream depends on that calibration, so the criterion is the nearest of the five.

**The H5 trough stops shallower than −0.16 dex** in September 2030. The only item on the list the model survives rather than dies from: it would mean panic faded following euphoria and the mechanism of the cycle has stopped being purely human. There is currently not a single observation under the panic slider, and this is where the first one arrives.

The other three are on the page, in the "Falsification" section.

## How to run

The page is fully static and works offline. Open `index.html` (English) or `ru.html` (Russian) in a browser — no build, no server, no dependency installation. All computation happens in the browser and no request leaves the page.

The model takes about fifty lines of JavaScript in the source:

| Function | What it does |
|---|---|
| `pure(t, β)` | the power law, recalibrated through a reference point at day 2971 from genesis |
| `sat(p, L)` | the saturation envelope, `p·L / (p³ + L³)^⅓` |
| `plateau(W)` | the plateau level from the number of owners through the average holding size |
| `phiAt` / `zetaAt` | headroom left by the ceiling, and the share of the cycle that remains |
| `amps(d_e, d_p, W, β)` | projection of peak and trough amplitudes onto H5–H8 |
| `coherence(d_e, d_p, W, β)` | five coherence checks, each returning a continuous tension from 0 to 1 |
| `fuelState(W, d_e, β)` | what the cycle of the 2030s rests on |
| `modAt(i, A)` | the cycle overlay, cosine interpolation between the nodes |
| `EPOCHS` / `OBS` | the halving table with per-epoch amplitudes, and the observed series |

## Files

```
index.html      the model, English
ru.html         the model, Russian
chart.umd.js    Chart.js, vendored
fonts/          IBM Plex, vendored
```

## Dependencies

- [Chart.js](https://www.chartjs.org) 4.4.1 (MIT) — rendering, file `chart.umd.js`
- [IBM Plex](https://github.com/IBM/plex) (SIL OFL 1.1) — fonts, folder `fonts/`

Both are bundled locally. The page makes no external requests.

## Sources

- Santostasi, G. & Perrenod, S. (2026). *A Mechanistic Derivation of the Bitcoin Price Power Law: Network Adoption Dynamics and Generalised Metcalfe Scaling.* Zenodo. [10.5281/zenodo.19387099](https://doi.org/10.5281/zenodo.19387099)
- Baquero, C. & Menezes, R. (2026). [*Bitcoin's Power Law: Weak Structure, Strong Forecasts.*](https://arxiv.org/abs/2605.21316)
- [Glassnode: Entity-Adjusted Metrics](https://docs.glassnode.com/guides-and-tutorials/on-chain-concepts/entity-adjusted-metrics); [World Gold Council: How Much Gold Has Been Mined?](https://www.gold.org/goldhub/data/how-much-gold); [World Federation of Exchanges: 2025 global market statistics](https://www.world-exchanges.org/news/articles/new-wfe-data-public-markets-post-strong-growth-2025-despite-geopolitical-instability)
- Brause, D. (2026). *The Information Coherence Hypothesis: A Unified Informational Framework for Reality, Consciousness, and Meaning.* Zenodo. [10.5281/zenodo.18812955](https://doi.org/10.5281/zenodo.18812955)

## Licence

Text and model — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The libraries keep their own licences.

**Disclaimer.** An analytical model, not investment advice. The projection assumes the power-law regime holds and that no structural discontinuities occur in the adoption mechanism.

## Support

If the page was useful, a few satoshi go here:

```
bc1qppqdavfnkffmdrsq9nypsa2w57jmmeeurv7xew
```
