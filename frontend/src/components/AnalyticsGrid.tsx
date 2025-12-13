import { ArrowUpRight, ArrowDownRight } from 'lucide-react';


interface Metric {
    label: string;
    value: string | number;
    growth?: string;
}

interface AnalyticsData {
    company_name: string;
    fiscal_period: string;
    metrics: Metric[];
    summary: string;
}

export const AnalyticsGrid: React.FC<{ data: AnalyticsData | null; loading: boolean }> = ({ data, loading }) => {
    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
                {[1, 2, 3, 4].map(i => (
                    <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>
                ))}
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-2xl font-bold text-gray-900">{data.company_name}</h2>
                    <p className="text-gray-500">{data.fiscal_period}</p>
                </div>
                <div className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
                    AI Generated Analysis
                </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Executive Summary</h4>
                <p className="text-gray-800 leading-relaxed">{data.summary}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {data.metrics.map((metric, idx) => (
                    <div key={idx} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-500">{metric.label}</p>
                            <p className="text-2xl font-bold text-gray-900 mt-2">{metric.value}</p>
                        </div>
                        {metric.growth && (
                            <div className="mt-4 flex items-center text-sm">
                                {metric.growth.includes('-') ? (
                                    <ArrowDownRight className="w-4 h-4 text-red-500 mr-1" />
                                ) : (
                                    <ArrowUpRight className="w-4 h-4 text-green-500 mr-1" />
                                )}
                                <span className={metric.growth.includes('-') ? 'text-red-500' : 'text-green-500'}>
                                    {metric.growth}
                                </span>
                                <span className="text-gray-400 ml-1">vs last period</span>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};
