import { useState } from "react";

import { Alert, Button, Card, Input, Select } from "../../../shared/ui";
import { useSync } from "../hooks/useSync";

export function SyncPage() {
  const [mode, setMode] = useState<"strict" | "full">("strict");
  const [limitPerProvider, setLimitPerProvider] = useState(500);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [dateError, setDateError] = useState<string | null>(null);
  const syncMutation = useSync();

  const buildDateRangePayload = () => {
    if (!startDate && !endDate) return {};

    if (!startDate || !endDate) {
      setDateError("Merci de renseigner a la fois la date de debut et la date de fin.");
      return null;
    }

    if (endDate < startDate) {
      setDateError("La date de fin doit etre superieure ou egale a la date de debut.");
      return null;
    }

    setDateError(null);

    return {
      from_date: `${startDate}T00:00:00`,
      to_date: `${endDate}T23:59:59`,
    };
  };

  const onSync = () => {
    const dateRange = buildDateRangePayload();
    if (!dateRange) return;

    syncMutation.mutate({
      providers: ["gmail", "outlook"],
      limit_per_provider: limitPerProvider,
      mode,
      ...dateRange,
    });
  };

  return (
    <main className="space-y-6 p-6">
      <h1 className="text-2xl font-bold text-slate-900">Synchronisation</h1>
      <Card className="max-w-xl space-y-4">
        <label className="block text-sm font-medium text-slate-700" htmlFor="sync-mode">
          Mode de sync
        </label>
        <Select id="sync-mode" value={mode} onChange={(event) => setMode(event.target.value as "strict" | "full")}>
          <option value="full">full</option>
          <option value="strict">strict</option>
        </Select>
        <div className="space-y-2">
          <label className="block text-sm font-medium text-slate-700" htmlFor="sync-limit">
            Limite par provider
          </label>
          <Input
            id="sync-limit"
            type="number"
            min={1}
            max={5000}
            value={limitPerProvider}
            onChange={(event) => {
              const parsed = Number(event.target.value);
              if (!Number.isFinite(parsed)) return;
              const bounded = Math.max(1, Math.min(5000, Math.trunc(parsed)));
              setLimitPerProvider(bounded);
            }}
          />
          <p className="text-xs text-slate-500">Augmente cette valeur pour couvrir des periodes plus longues.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-700" htmlFor="sync-start-date">
              Date de debut
            </label>
            <Input
              id="sync-start-date"
              type="date"
              value={startDate}
              onChange={(event) => {
                setStartDate(event.target.value);
                if (dateError) setDateError(null);
              }}
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-slate-700" htmlFor="sync-end-date">
              Date de fin
            </label>
            <Input
              id="sync-end-date"
              type="date"
              value={endDate}
              onChange={(event) => {
                setEndDate(event.target.value);
                if (dateError) setDateError(null);
              }}
            />
          </div>
        </div>
        <p className="text-xs text-slate-500">Laisse vide pour synchroniser sans filtre de dates.</p>
        <Button onClick={onSync} isLoading={syncMutation.isPending}>
          Sync Now
        </Button>
        {dateError ? <Alert variant="error">{dateError}</Alert> : null}
        {syncMutation.mappedError ? <Alert variant="error">{syncMutation.mappedError.message}</Alert> : null}
        {syncMutation.data ? (
          <Alert variant="success">
            Sync terminee: fetched={syncMutation.data.fetched}, filtered={syncMutation.data.filtered}, inserted={syncMutation.data.inserted}, duplicates={syncMutation.data.duplicates}
          </Alert>
        ) : null}
      </Card>
    </main>
  );
}
