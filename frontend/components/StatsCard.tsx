export default function StatsCard({ title, value, description }: { title: string, value: string | number, description?: string }) {
  return (
    <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
      <div className="absolute top-0 right-0 -mr-8 -mt-8 w-24 h-24 rounded-full bg-gradient-to-br from-blue-50 to-blue-100 opacity-50 group-hover:scale-150 transition-transform duration-500"></div>
      <h3 className="text-sm font-semibold text-gray-500 tracking-wide uppercase mb-2 relative z-10">{title}</h3>
      <p className="text-4xl font-bold text-gray-900 tracking-tight relative z-10">{value}</p>
      {description && <p className="text-sm text-gray-400 mt-2 font-medium relative z-10">{description}</p>}
    </div>
  );
}
