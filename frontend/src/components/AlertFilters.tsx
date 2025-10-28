import { Search, Filter, X } from 'lucide-react';
import { Card } from './Card';

interface AlertFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  severity: string;
  onSeverityChange: (value: string) => void;
  status: string;
  onStatusChange: (value: string) => void;
  onReset: () => void;
}

export const AlertFilters = ({
  search,
  onSearchChange,
  severity,
  onSeverityChange,
  status,
  onStatusChange,
  onReset,
}: AlertFiltersProps) => {
  const hasActiveFilters = search || severity !== 'all' || status !== 'all';

  return (
    <Card>
      <div className="flex items-center gap-2 mb-4">
        <Filter className="w-5 h-5 text-primary-600" />
        <h3 className="font-semibold text-gray-900 dark:text-white">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={onReset}
            className="ml-auto text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white flex items-center gap-1"
          >
            <X className="w-4 h-4" />
            Clear
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search alerts..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
          />
        </div>

        {/* Severity Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Severity
          </label>
          <select
            value={severity}
            onChange={(e) => onSeverityChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Status
          </label>
          <select
            value={status}
            onChange={(e) => onStatusChange(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
          >
            <option value="all">All Statuses</option>
            <option value="open">Open</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>
    </Card>
  );
};
