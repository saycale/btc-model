# Независимый технический аудит `btc-model`

Дата аудита: 9 сентября 2026 года<br>
Ревизия: `6827439d34570254eb220fcd51d37f2511956e35`<br>
Объект: `saycale/btc-model`, включая изменения после fork от `neokrasav4ik/btc-model`

## Краткий вывод

Реализация арифметически аккуратна: независимая Python-реализация воспроизводит формулы, plateau `$657,000`, holding `$8,447.14`, а также базовые `ζ` для H5–H7 (`0.870`, `0.333`, `0.168`) и амплитуды интерфейса. Явной ошибки знака, единиц или индексации в математическом ядре не найдено.

Но модель объединяет части с очень разным статусом доказательности:

| Часть | Вердикт | Что действительно подтверждено |
|---|---|---|
| Power-law как описательный long-run envelope | **Умеренно защищена** | Высокий исторический fit и полезность на 12–24-месячном горизонте воспроизводятся; это не доказывает структурный закон или прогноз до 2040 года. |
| Постоянный exponent `5.69` | **Частично защищён** | Число устойчиво на ряде близких окон, но зависит от origin/window; полная текущая monthly-выборка даёт `5.603`. |
| Декомпозиция `3 × β` через addresses | **Слабая / не независимая** | Числа `3.029`, `1.839` и произведение `5.571` воспроизводятся, но все regressions используют совместно трендующие price, time и addresses; addresses также не равны owners. |
| Saturation function | **Не идентифицирована данными** | Формула гладкая и математически корректная, но exponent мягкости `3` и форма перехода назначены. История почти не различает ceilings от примерно `$0.6M` до `$100M+`. |
| Owner ceiling и terminal holding | **Сценарные assumptions** | `L = W·A/S` — accounting identity. `W=1.61B` и terminal cap `$13.6T` не оценены независимо; `$8,447` выведены из них. |
| Наличие повторяющейся wave structure | **Слабое–умеренное внешнее подтверждение** | Независимая работа обнаруживает Bitcoin-specific waves выше AR(1) noise floor, но не подтверждает именно halving-cosine, выбранные nodes или decay данной модели. |
| Euphoria decay | **Suggestive, но статистически слабая** | Четыре значения монотонно падают. Для exponential decay 95% iid-интервал ratio на цикл `0.113–1.435`, то есть включает отсутствие затухания. |
| Panic decay | **Не проверена** | В коде и тексте честно отмечено: у slider нет ни одного out-of-sample наблюдения. |
| Связь `ζ = d_e + (1-d_e)φ` | **Механистическая гипотеза** | Математически согласована, эмпирически не оценена и не сравнена с альтернативными couplings. |
| Точные H5 peak/trough | **Curve-fitting / scenario output** | Это условные результаты выбранных sliders и post-hoc-calibrated nodes, не статистические point forecasts. |

Итоговый статус: это качественно выполненная **интерактивная сценарная модель**, содержащая полезный power-law baseline. Она пока не является статистически валидированной моделью точной цены и циклов 2029–2038 годов.

## 1. Что было воспроизведено

Независимый скрипт [`audit/audit.py`](audit/audit.py) читает только исходные массивы `OBS` и `ADR` из HTML и заново реализует математику на Python. Он не исполняет JavaScript модели.

Запуск:

```bash
python3 audit/audit.py
```

Полный machine-readable output сохраняется в [`audit/results.json`](audit/results.json).

Ключевые совпадения:

| Величина | Результат |
|---|---:|
| Наблюдения price / addresses / overlap | `194 / 197 / 191` |
| Terminal holding | `$8,447.142857` |
| Plateau при `W=1610M` | `$657,000` |
| `ζ` H5 / H6 / H7 | `0.8698 / 0.3328 / 0.1677` |
| H5 amplitude, peak / trough | `+0.0492 / −0.2414 dex` |
| Regression price on addresses, slope | `1.83935` |
| Regression addresses on age, slope | `3.02903` |
| Их произведение | `5.57145` |
| Direct price-on-age slope на overlap | `5.66902` |

Это подтверждает внутреннюю арифметическую целостность основной реализации.

## 2. Power law: сильная описательная часть, слабая «физическая» интерпретация

### 2.1 Full-sample результат изменился

На всех 194 текущих monthly observations fit даёт:

- exponent: `5.60289`;
- `R² = 0.96161`;
- RMSE: `0.30166 dex`.

Число `5.66902` на странице получается на overlap с address series — только по 191 месяцам до мая 2026 года. Поэтому формулировка о `5.69`, «измеренном по полной длине price series», после добавления июня–августа 2026 года больше не буквальна. Корректнее назвать `5.69` **внешним reference estimate на более раннем daily window**, а рядом показывать current-sample estimate и дату конца окна.

### 2.2 `R²` не равен количеству независимых свидетельств

Lag-1 autocorrelation monthly residuals равна `0.912`; Ljung–Box на 12 лагах решительно отвергает white noise (`Q=528.5`). IID standard error slope равна `0.081`, Newey–West/HAC(12) — уже `0.188`, более чем вдвое выше. HAC всё равно не решает вопрос возможной non-stationarity; он лишь показывает масштаб ошибки обычного IID interval.

Следовательно, 194 месяца — не 194 независимых подтверждения закона. Высокий `R²` показывает хорошую геометрическую аппроксимацию уровней, но не причинность и не calibration uncertainty.

### 2.3 Чувствительность к origin date

| Origin | Fitted exponent | `R²` |
|---|---:|---:|
| 2008-01-03 | 6.559 | 0.955 |
| 2009-01-03 | 5.603 | 0.962 |
| 2009-07-03 | 5.072 | 0.964 |
| 2010-01-03 | 4.443 | 0.962 |

Все варианты визуально «хороши», но дают существенно разные long-run extrapolations. Genesis — естественный и in-sample удачный origin, однако exponent не является shift-invariant свойством ряда. Это независимо согласуется с Baquero & Menezes, которые показывают почти трёхкратную variation на более широком shift sweep.

### 2.4 Реальная сильная сторона: long-horizon baseline

Monthly walk-forward с 11 yearly cutoffs (train строго до января каждого года, 2014–2024) дал:

| Horizon | Power law RMSE, dex | Last-price naive RMSE, dex | Победитель |
|---:|---:|---:|---|
| 1 month | 0.364 | 0.095 | Naive |
| 3 months | 0.332 | 0.181 | Naive |
| 6 months | 0.290 | 0.270 | примерно равны |
| 12 months | 0.383 | 0.518 | Power law |
| 18 months | 0.325 | 0.501 | Power law |
| 24 months | 0.370 | 0.687 | Power law |

Это почти воспроизводит опубликованный daily-data результат: naive выигрывает 1–3 месяца, crossover находится около 6 месяцев, power law выигрывает 12–24 месяца. Именно это — наиболее статистически защищённый practical claim проекта. Но tested horizon заканчивается 24 месяцами; из него нельзя автоматически вывести точность до 2040 года.

## 3. Metcalfe decomposition: численно верно, логически не независимо

Фраза «cubic-growth assumption and generalised Metcalfe are not fitted to the price — they measure independently» слишком сильна.

1. `β` считается регрессией `log(price)` на `log(addresses)`, поэтому непосредственно fitted to price.
2. Direct slope, address-growth slope и price-on-address slope используют одни и те же сильно трендующие ряды. Произведение двух slopes — не независимый replication direct slope.
3. Non-zero-balance addresses — не участники и не beneficial owners. Один пользователь создаёт много адресов; биржа/ETF агрегирует многих владельцев в малом числе адресов.
4. Price может вести address activity, а не наоборот. В cited independent analysis изменения price опережают изменения on-chain adoption metrics; это делает причинное прочтение `addresses → value` ещё менее надёжным.
5. Если `V` означает network value, правильной зависимой величиной обычно была бы market capitalisation, а не price per coin. Изменяющийся supply особенно важен в ранней истории.
6. Полоса `β=1.60…2.05` описана как `n log n … n²`, но `n log n` не является постоянной степенью `n^1.6`; его локальная elasticity равна `1 + 1/ln(n)` и зависит от `n`.

Рекомендуемая формулировка: **«descriptive co-trend consistency check»**, а не независимое измерение причинного Metcalfe exponent.

## 4. Saturation и monetary ceiling: данные их пока не видят

Форма

```text
sat(p,L) = pL / (p³ + L³)^(1/3)
```

математически корректна. Её instantaneous elasticity относительно pure trend равна

```text
φ = L³ / (p³ + L³)
```

а 30-day finite difference в `phiAt` является хорошей численной аппроксимацией. Ошибка находится не в calculus, а в identification.

Profile fit, где при каждом фиксированном `L` заново оцениваются intercept и slope, даёт почти одинаковый historical RMSE:

| `L` | RMSE, dex |
|---:|---:|
| `$150k` | 0.2993 |
| `$581k` | 0.3016 |
| `$999k` | 0.30165 |
| `$100M` (практически no saturation) | 0.30166 |

Разница между `$657k` и практически бесконечным ceiling ничтожна на historical sample. Следовательно:

- данные не оценивают `L=657k`;
- exponent мягкости `3` не оценён;
- ±40% owner band — **sensitivity envelope**, не confidence/prediction interval;
- `W=1.61B`, `$13.6T` и `$8,447` не три подтверждающих факта: были выбраны первые два, третий является их quotient.

Это самая большая причина, по которой trajectories 2033–2040 нельзя трактовать как статистический прогноз.

## 5. Halving cycles

### 5.1 Что поддерживается

Исторические peaks/troughs действительно образуют повторяющуюся wave-like structure. Внешняя работа Baquero & Menezes сообщает, что Bitcoin-specific wave stability может превышать PL+AR(1) noise floor (`p=0.015` для заранее выбранного strict threshold), хотя результат не проходит Bonferroni threshold по семи сравниваемым series. Это аргумент в пользу «волны существуют», но не в пользу точной формы данного overlay.

### 5.2 Что fitted post hoc

В `EPOCHS` для H0–H4 вручную заданы halving, peak, trough и две амплитуды. Затем между этими выбранными nodes проведён cosine. Это реконструкция уже известных extrema, а не out-of-sample test. H4 peak и H4 trough особенно критичны: последний observation одновременно принят за окончательный trough и используется для projection.

При сравнении с embedded monthly closes cycle overlay не улучшает RMSE: `0.303 dex` у trend против `0.319 dex` у trend+cycle. Это не обязательно опровергает cycles — nodes взяты по intramonth extremes, а `OBS` содержит approximate monthly closes. Но это означает, что **текущий набор данных вообще не позволяет честно оценить заявленную cycle layer**. Нельзя калибровать на intramonth highs/lows и score-ить по monthly closes.

### 5.3 Euphoria decay

Ряд `1.03, 0.81, 0.46, 0.06` монотонен. При exchangeability вероятность одного заранее указанного строгого порядка равна `1/4! = 4.17%`, но это оптимистическая граница: extrema, trend и эпохи выбирались после просмотра истории.

Exponential fit четырёх точек даёт ratio около `0.403` на цикл, но 95% iid interval `0.113–1.435` включает ratio `1` — отсутствие decay. Sliders `0.50…0.67` являются разумными scenarios, но не confidence interval.

### 5.4 Panic decay и `ζ`

Panic observations `−0.28, −0.24, −0.38, −0.37` не показывают decay. H5 panic slider полностью prior-driven.

Coupling `ζ = d_e + (1-d_e)φ` не добавляет числовой constant, но добавляет **functional-form assumption**. Более того, `d_e` используется одновременно:

- для интерполяции будущей euphoria amplitude;
- как доля cycle, способная существовать без trend headroom.

Эти два смысла не тождественны эмпирически. Их равенство — сильная гипотеза, а не следствие определения.

## 6. Falsification и uncertainty

Публичные falsification criteria — хорошая практика, но сейчас они не образуют proper statistical test:

- thresholds (`±0.5 dex`, два года, `$58k`, `−0.16 dex`) не получены из заранее calibrated predictive distribution;
- некоторые критерии проверяют одну calibration node, а не всю модель;
- observation «внутри band» не подтверждает unique mechanism: тот же диапазон могут давать альтернативные trends;
- показанная band меняет только owner ceiling и исключает uncertainty slope, intercept, origin, saturation shape, cycle timing, price data и regime risk.

В интерфейсе следует постоянно называть её **scenario/sensitivity band**, не uncertainty band и не predictive interval.

## 7. Data и engineering audit

### Data provenance

- `OBS` собран из нескольких approximate public sources и не имеет отдельного CSV с `date/source/field/timezone/retrieved_at`.
- Ранние monthly prices округлены грубо, поздние — до cents; единая методика отсутствует.
- `ADR` назван month-end, но последняя точка относится к 23 мая 2026 года; она сопоставлена с May close price, то есть timestamps различаются.
- Coin Metrics repository публикует community archive под `CC BY-NC 4.0`; это необходимо явно отразить рядом с embedded derivative data.

### Licensing

- README говорит «Text and model — CC BY 4.0», но файл `LICENSE` содержит **CC0 1.0**. Это прямое противоречие.
- Chart.js header сохраняет MIT notice, но отдельный dependency license отсутствует.
- В repository нет текста SIL OFL для bundled IBM Plex fonts.
- Лицензия исходных данных должна быть отделена от лицензии model/code/text.

### Maintainability

- English и Russian pages дублируют всё JavaScript core. Это создаёт риск silent drift.
- Model/data/UI находятся в двух больших HTML files; unit tests и CI отсутствуют.
- Constants не имеют machine-readable provenance или estimated-vs-assumed metadata.

## 8. Приоритет исправлений

### P0 — исправить claims, не меняя математику

1. Заменить «5.69 measured on full current series» на «external reference estimate on a specified window»; показать current full-sample `5.603`.
2. Переименовать Metcalfe block в descriptive co-trend check; убрать смысл независимой causal validation.
3. Показывать HAC uncertainty и residual autocorrelation; не выводить IID `±0.030` как обычный interval.
4. Везде назвать blue band sensitivity/scenario envelope.
5. Явно маркировать H5 values как conditional scenario nodes, не point forecasts.
6. Исправить `LICENSE`/README mismatch и добавить лицензии data/fonts.

### P1 — сделать проект воспроизводимым

1. Вынести price и address data в CSV с полным provenance.
2. Вынести единое mathematical core в `model.js`; обе локализации должны импортировать его.
3. Добавить automated tests против независимой реализации.
4. Добавить walk-forward dashboard по горизонтам 1/3/6/12/18/24 месяца.
5. Добавить saturation profile plot, показывающий, что `L` historical data не идентифицирует.
6. Использовать один consistent series: monthly close для fit либо daily high/low для extrema и scoring.

### P2 — превратить scenarios в statistical model

1. До получения H5 observations preregister node timing, estimator и loss function.
2. Оценивать distribution параметров, а не четыре hand-picked presets.
3. Сравнить halving-cosine с PL+AR(1), generic periodic, sigmoid-wave и no-cycle baselines out of sample.
4. Разделить два параметра, сейчас объединённых в `d_e`: euphoria decay и fraction of cycle independent of headroom.
5. Оценивать ceiling по внешней beneficial-owner/adoption/wealth model либо честно оставить его pure scenario axis.

## 9. Финальная классификация

**Статистически наиболее защищено:** parsimonious power-law envelope на истории и его относительная 12–24-месячная forecast utility.

**Правдоподобно, но не доказано:** наличие некоторой multi-wave структуры; maturation/euphoria compression как qualitative hypothesis.

**Essentially curve-fitting / scenario engineering:** конкретные H0–H4 cosine nodes, decay endpoints, H5 peak/trough, saturation shape/exponent, owner ceiling, terminal holding, `ζ` coupling и coherence colours.

Это не делает проект бесполезным. Напротив, после корректировки claims он может стать очень хорошим инструментом **scenario analysis with falsifiable bookkeeping**. Главная необходимая правка — чётко отделить то, что estimated from data, от того, что assumed by construction.

## Источники для независимой проверки

- Carlos Baquero & Raquel Menezes, [Bitcoin's Power Law: Weak Structure, Strong Forecasts](https://arxiv.org/abs/2605.21316), 2026.
- Giovanni Santostasi & Stephen Perrenod, [A Mechanistic Derivation of the Bitcoin Price Power Law](https://doi.org/10.5281/zenodo.19387099), 2026.
- Coin Metrics, [community data archive](https://github.com/coinmetrics/data) and its stated `CC BY-NC 4.0` data licence.
