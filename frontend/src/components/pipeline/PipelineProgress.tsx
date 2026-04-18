import { Check, Loader2 } from 'lucide-react';
import { PipelineStep } from '../../types';

interface PipelineProgressProps {
  steps: PipelineStep[];
}

export default function PipelineProgress({ steps }: PipelineProgressProps) {
  const completedCount = steps.filter((s) => s.status === 'complete').length;
  const progressPct = (completedCount / steps.length) * 100;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Campaign Pipeline</h3>
          <p className="text-xs text-gray-500 mt-0.5">
            {completedCount === steps.length
              ? 'All steps completed successfully'
              : `Step ${Math.min(completedCount + 1, steps.length)} of ${steps.length} running`}
          </p>
        </div>
        <span className="text-sm font-semibold text-blue-700">
          {Math.round(progressPct)}%
        </span>
      </div>

      <div className="relative mb-6">
        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-600 rounded-full transition-all duration-700 ease-in-out"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
        {steps.map((step, idx) => (
          <StepBadge key={step.id} step={step} index={idx} />
        ))}
      </div>
    </div>
  );
}

interface StepBadgeProps {
  step: PipelineStep;
  index: number;
}

function StepBadge({ step, index }: StepBadgeProps) {
  const isComplete = step.status === 'complete';
  const isActive = step.status === 'active';
  const isIdle = step.status === 'idle';

  return (
    <div className="flex flex-col items-center gap-2 text-center">
      <div
        className={`w-9 h-9 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-500 ${
          isComplete
            ? 'bg-blue-600 text-white shadow-sm shadow-blue-200'
            : isActive
            ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-600 ring-offset-1'
            : 'bg-gray-100 text-gray-400'
        }`}
      >
        {isComplete ? (
          <Check size={14} strokeWidth={2.5} />
        ) : isActive ? (
          <Loader2 size={14} className="animate-spin" />
        ) : (
          <span>{index + 1}</span>
        )}
      </div>
      <span
        className={`text-[10px] font-medium leading-tight ${
          isComplete
            ? 'text-blue-700'
            : isActive
            ? 'text-gray-900'
            : 'text-gray-400'
        }`}
      >
        {step.label}
      </span>
    </div>
  );
}
