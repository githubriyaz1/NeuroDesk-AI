import React from 'react';

const TECH_OPTIONS = [
  { name: 'React', category: 'frontend' },
  { name: 'Next.js', category: 'frontend' },
  { name: 'Vue', category: 'frontend' },
  { name: 'Angular', category: 'frontend' },
  { name: 'Flutter', category: 'frontend' },
  { name: 'React Native', category: 'frontend' },
  { name: 'FastAPI', category: 'backend' },
  { name: 'Node.js', category: 'backend' },
  { name: 'Express', category: 'backend' },
  { name: 'Spring Boot', category: 'backend' },
  { name: 'ASP.NET', category: 'backend' },
  { name: 'Django', category: 'backend' },
  { name: 'Flask', category: 'backend' },
  { name: 'Laravel', category: 'backend' },
  { name: 'PostgreSQL', category: 'database' },
  { name: 'MongoDB', category: 'database' },
  { name: 'MySQL', category: 'database' },
  { name: 'Redis', category: 'database' },
  { name: 'Docker', category: 'devops' },
  { name: 'Kubernetes', category: 'devops' },
];

export default function TechnologySelector({ selected = [], onChange }) {
  const toggleTech = (name) => {
    if (selected.includes(name)) {
      onChange(selected.filter((t) => t !== name));
    } else {
      onChange([...selected, name]);
    }
  };

  return (
    <div className="space-y-3">
      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider">
        Preferred Technology Stack
      </label>
      <div className="flex flex-wrap gap-2">
        {TECH_OPTIONS.map((t) => {
          const isSelected = selected.includes(t.name);
          return (
            <button
              key={t.name}
              type="button"
              onClick={() => toggleTech(t.name)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                isSelected
                  ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300 shadow-sm shadow-cyan-500/20'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
              }`}
            >
              {t.name}
            </button>
          );
        })}
      </div>
    </div>
  );
}
