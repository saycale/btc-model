# Forecast ledger

This is a versioned register of conditional claims made before their target dates.
It is deliberately separate from the model UI so that historical settings cannot
be silently rewritten after an outcome is known.

The machine-readable entries are in [`data/forecast-ledger.json`](data/forecast-ledger.json).
Each entry records the source date, all slider values, its status, target and the
fact that a scenario output is not a probability forecast. Append a new entry;
do not revise an open one except to correct a documented data error.

Russian readers: журнал фиксирует условия сценария до целевой даты. Открытую
запись нельзя переписывать задним числом — только добавить исправление с причиной.
