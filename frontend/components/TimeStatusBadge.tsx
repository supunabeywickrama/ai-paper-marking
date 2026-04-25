import { CheckCircle, Clock, XCircle } from 'lucide-react';

const config = {
  ON_TIME: { label: 'On Time', icon: CheckCircle, cls: 'bg-green-100 text-green-800' },
  LATE_ACCEPTED: { label: 'Late', icon: Clock, cls: 'bg-amber-100 text-amber-800' },
  REJECTED: { label: 'Rejected', icon: XCircle, cls: 'bg-red-100 text-red-800' },
} as const;

type Status = keyof typeof config;

export default function TimeStatusBadge({ status }: { status: string }) {
  const cfg = config[status as Status] ?? config.REJECTED;
  const Icon = cfg.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${cfg.cls}`}>
      <Icon size={12} />
      {cfg.label}
    </span>
  );
}
