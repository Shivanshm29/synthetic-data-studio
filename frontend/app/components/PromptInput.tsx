"use client";

interface PromptInputProps {
  value: string;
  onChange: (value: string) => void;
  onExampleClick: (example: string) => void;
  disabled?: boolean;
}

const EXAMPLES = [
  "100 users with name, email, age, and city",
  "Employee HR dataset with salaries and departments",
  "E-commerce orders with products and prices",
];

export default function PromptInput({
  value,
  onChange,
  onExampleClick,
  disabled,
}: PromptInputProps) {
  return (
    <div className="flex flex-col gap-3">
      <div className="glass rounded-xl glow-border transition-all duration-300">
        <textarea
          id="prompt-input"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={"Describe the synthetic dataset you want to generate...\n\nExample: Generate 500 employee records with names, emails,\ndepartments, salaries, and performance ratings"}
          disabled={disabled}
          rows={4}
          className="w-full bg-transparent px-5 py-4 text-foreground placeholder-text-muted resize-none outline-none text-sm leading-relaxed disabled:opacity-50"
        />
        <div className="flex items-center justify-between px-5 py-2 border-t border-border text-xs text-text-muted">
          <span>Supports multiline descriptions</span>
          <span>{value.length} characters</span>
        </div>
      </div>

      {!value && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-text-muted">Try:</span>
          {EXAMPLES.map((example) => (
            <button
              key={example}
              onClick={() => onExampleClick(example)}
              className="text-xs px-3 py-1.5 rounded-full bg-surface border border-border text-text-secondary hover:text-foreground hover:border-accent/50 transition-all duration-200 cursor-pointer"
            >
              {example}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
