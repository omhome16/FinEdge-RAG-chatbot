import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface PieChartData {
    name: string;
    value: number;
}

interface PieChartProps {
    title: string;
    data: PieChartData[];
    colors?: string[];
}

const defaultColors = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#14b8a6', '#f43f5e'];

export function PieChartComponent({ title, data, colors = defaultColors }: PieChartProps) {
    return (
        <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-primary mb-4">{title}</h3>
            <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                            labelLine={{ stroke: 'rgb(var(--text-muted))' }}
                        >
                            {data.map((_, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={colors[index % colors.length]}
                                    stroke="transparent"
                                />
                            ))}
                        </Pie>
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
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
