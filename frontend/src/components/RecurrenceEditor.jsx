import { useState, useEffect } from 'react';

export default function RecurrenceEditor({ value, onChange }) {
  const [frequency, setFrequency] = useState('DAILY');
  const [interval, setInterval] = useState(1);
  const [weekdays, setWeekdays] = useState([]);
  const [monthDay, setMonthDay] = useState(1);
  const [endType, setEndType] = useState('NEVER');
  const [count, setCount] = useState(10);
  const [until, setUntil] = useState('');

  const weekdayOptions = [
    { value: 'MO', label: 'L' },
    { value: 'TU', label: 'M' },
    { value: 'WE', label: 'X' },
    { value: 'TH', label: 'J' },
    { value: 'FR', label: 'V' },
    { value: 'SA', label: 'S' },
    { value: 'SU', label: 'D' }
  ];

  // Parse existing RRULE
  useEffect(() => {
    if (value) {
      try {
        const parts = value.split(';');
        parts.forEach(part => {
          const [key, val] = part.split('=');
          
          if (key === 'FREQ') {
            setFrequency(val);
          } else if (key === 'INTERVAL') {
            setInterval(parseInt(val));
          } else if (key === 'BYDAY') {
            setWeekdays(val.split(','));
          } else if (key === 'BYMONTHDAY') {
            setMonthDay(parseInt(val));
          } else if (key === 'COUNT') {
            setEndType('COUNT');
            setCount(parseInt(val));
          } else if (key === 'UNTIL') {
            setEndType('UNTIL');
            setUntil(val);
          }
        });
      } catch (error) {
        console.error('Error parsing RRULE:', error);
      }
    }
  }, [value]);

  // Generate RRULE string
  useEffect(() => {
    const parts = [`FREQ=${frequency}`];

    if (interval > 1) {
      parts.push(`INTERVAL=${interval}`);
    }

    if (frequency === 'WEEKLY' && weekdays.length > 0) {
      parts.push(`BYDAY=${weekdays.join(',')}`);
    }

    if (frequency === 'MONTHLY' && monthDay > 0) {
      parts.push(`BYMONTHDAY=${monthDay}`);
    }

    if (endType === 'COUNT' && count > 0) {
      parts.push(`COUNT=${count}`);
    } else if (endType === 'UNTIL' && until) {
      // Convert date to RRULE format: YYYYMMDDTHHMMSSZ
      const date = new Date(until);
      const formatted = date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
      parts.push(`UNTIL=${formatted}`);
    }

    const rrule = parts.join(';');
    onChange(rrule);
  }, [frequency, interval, weekdays, monthDay, endType, count, until, onChange]);

  const toggleWeekday = (day) => {
    setWeekdays(prev =>
      prev.includes(day)
        ? prev.filter(d => d !== day)
        : [...prev, day].sort((a, b) => {
            const order = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];
            return order.indexOf(a) - order.indexOf(b);
          })
    );
  };

  return (
    <div className="space-y-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <h3 className="font-semibold text-gray-700">Configuración de Repetición</h3>

      {/* Frequency */}
      <div>
        <label className="text-sm font-medium text-gray-700 mb-2 block">
          Repetir cada:
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            min="1"
            value={interval}
            onChange={(e) => setInterval(parseInt(e.target.value) || 1)}
            className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <select
            value={frequency}
            onChange={(e) => setFrequency(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="DAILY">Día(s)</option>
            <option value="WEEKLY">Semana(s)</option>
            <option value="MONTHLY">Mes(es)</option>
            <option value="YEARLY">Año(s)</option>
          </select>
        </div>
      </div>

      {/* Weekly: Days of week */}
      {frequency === 'WEEKLY' && (
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">
            Días de la semana:
          </label>
          <div className="flex gap-2">
            {weekdayOptions.map(({ value, label }) => (
              <button
                key={value}
                type="button"
                onClick={() => toggleWeekday(value)}
                className={`w-10 h-10 rounded-full font-medium transition-colors ${
                  weekdays.includes(value)
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Monthly: Day of month */}
      {frequency === 'MONTHLY' && (
        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">
            Día del mes:
          </label>
          <input
            type="number"
            min="1"
            max="31"
            value={monthDay}
            onChange={(e) => setMonthDay(parseInt(e.target.value) || 1)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      )}

      {/* End Type */}
      <div>
        <label className="text-sm font-medium text-gray-700 mb-2 block">
          Termina:
        </label>
        <div className="space-y-3">
          {/* Never */}
          <label className="flex items-center gap-2">
            <input
              type="radio"
              value="NEVER"
              checked={endType === 'NEVER'}
              onChange={(e) => setEndType(e.target.value)}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Nunca</span>
          </label>

          {/* After N occurrences */}
          <label className="flex items-center gap-2">
            <input
              type="radio"
              value="COUNT"
              checked={endType === 'COUNT'}
              onChange={(e) => setEndType(e.target.value)}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Después de</span>
            <input
              type="number"
              min="1"
              value={count}
              onChange={(e) => {
                setCount(parseInt(e.target.value) || 1);
                setEndType('COUNT');
              }}
              className="w-20 px-3 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <span className="text-sm text-gray-700">repeticiones</span>
          </label>

          {/* Until date */}
          <label className="flex items-center gap-2">
            <input
              type="radio"
              value="UNTIL"
              checked={endType === 'UNTIL'}
              onChange={(e) => setEndType(e.target.value)}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Hasta</span>
            <input
              type="date"
              value={until}
              onChange={(e) => {
                setUntil(e.target.value);
                setEndType('UNTIL');
              }}
              className="px-3 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </label>
        </div>
      </div>

      {/* Preview */}
      <div className="pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-500 font-mono">
          RRULE: {value || 'Ninguna'}
        </p>
      </div>
    </div>
  );
}
