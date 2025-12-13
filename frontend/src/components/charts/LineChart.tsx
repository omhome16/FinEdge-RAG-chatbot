import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface LineChartData {
    [key: string]: string | number;
}

interface LineChartProps {
    title: string;
    data: LineChartData[];
    xKey: string;
    yKeys: string[];
    colors?: string[];
}

const defaultColors = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

export function LineChartComponent({ title, data, xKey, yKeys, colors = defaultColors }: LineChartProps) {
    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-primary mb-4">{title}</h3>
            <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.2)" />
                        <XAxis
                            dataKey={xKey}
                            tick={{ fill: 'rgb(var(--text-secondary))', fontSize: 12 }}
                            axisLine={{ stroke: 'rgba(148, 163, 184, 0.3)' }}
                        />
                        <YAxis
                            tick={{ fill: 'rgb(var(--text-secondary))', fontSize: 12 }}
                            axisLine={{ stroke: 'rgba(148, 163, 184, 0.3)' }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'var(--glass-bg)',
                                backdropFilter: 'blur(12px)',
                                border: '1px solid var(--glass-border)',
                                borderRadius: '0.75rem',
                                boxShadow: 'var(--glass-shadow)',
                            }}
                            labelStyle={{ color: 'rgb(var(--text-primary))' }}
                        />
                        <Legend />
                        {yKeys.map((key, index) => (
                            <Line
                                key={key}
                                type="monotone"
                                dataKey={key}
                                stroke={colors[index % colors.length]}
                                strokeWidth={2}
                                dot={{ fill: colors[index % colors.length], strokeWidth: 2, r: 4 }}
                                activeDot={{ r: 6, strokeWidth: 2 }}
                            />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
