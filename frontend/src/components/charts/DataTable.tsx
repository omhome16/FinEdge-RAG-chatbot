interface DataTableProps {
    title: string;
    headers: string[];
    rows: string[][];
    highlightRows?: number[];
}

export function DataTable({ title, headers, rows, highlightRows = [] }: DataTableProps) {
    return (
        <div className="glass-card p-6 overflow-hidden">
            <h3 className="text-lg font-semibold text-primary mb-4">{title}</h3>
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-custom">
                            {headers.map((header, index) => (
                                <th
                                    key={index}
                                    className="text-left py-3 px-4 text-secondary font-medium"
                                >
                                    {header}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((row, rowIndex) => (
                            <tr
                                key={rowIndex}
                                className={`border-b border-custom/50 transition-colors ${highlightRows.includes(rowIndex)
                                        ? 'bg-indigo-500/10'
                                        : 'hover:bg-tertiary/50'
                                    }`}
                            >
                                {row.map((cell, cellIndex) => (
                                    <td
                                        key={cellIndex}
                                        className="py-3 px-4 text-primary"
                                    >
                                        {cell}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
