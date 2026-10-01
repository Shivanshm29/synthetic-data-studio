"use client";

interface EmptyStateProps {
  onExampleClick: (example: string) => void;
}

const SUGGESTIONS = [
  {
    title: "HR Dataset",
    prompt:
      "Generate a realistic HR dataset with 1000 employees including names, emails, departments, job titles, salaries, years of experience, and performance ratings",
    icon: "\ud83d\udc65",
  },
  {
    title: "E-Commerce Orders",
    prompt:
      "Generate an e-commerce order dataset with order IDs, customer names, emails, product names, prices, quantities, and order dates",
    icon: "\ud83d\uded2",
  },
  {
    title: "Student Records",
    prompt:
      "Generate a university student dataset with student names, emails, majors, GPAs, enrollment dates, and graduation status",
    icon: "\ud83c\udf93",
  },
  {
    title: "IoT Sensor Data",
    prompt:
      "Generate IoT sensor readings with sensor IDs, timestamps, temperature, humidity, pressure, and battery levels",
    icon: "\ud83d\udce1",
  },
];

export default function EmptyState({ onExampleClick }: EmptyStateProps) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center py-16 animate-fade-in">
      <div className="relative mb-8">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-accent/20 to-purple-500/20 flex items-center justify-center border border-accent/10">
          <svg
            className="w-10 h-10 text-accent"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M13.125 12h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125M20.625 12c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5M12 14.625v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 14.625c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m0 0v1.5c0 .621-.504 1.125-1.125 1.125"
            />
          </svg>
        </div>
        <div className="absolute -inset-4 bg-accent/5 rounded-3xl blur-2xl -z-10" />
      </div>

      <h2 className="text-xl font-semibold text-foreground mb-2">
        Generate Your Dataset
      </h2>
      <p className="text-text-muted text-sm mb-8 max-w-md text-center">
        Describe the dataset you need in plain English. Our AI will generate
        realistic synthetic data matching your specifications.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion.title}
            onClick={() => onExampleClick(suggestion.prompt)}
            className="group glass rounded-xl p-4 text-left hover:border-accent/30 transition-all duration-300 cursor-pointer hover:bg-surface-hover"
            id={`suggestion-${suggestion.title.toLowerCase().replace(/\s+/g, "-")}`}
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">{suggestion.icon}</span>
              <div>
                <h3 className="text-sm font-medium text-foreground group-hover:text-accent transition-colors">
                  {suggestion.title}
                </h3>
                <p className="text-xs text-text-muted mt-1 line-clamp-2">
                  {suggestion.prompt}
                </p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
