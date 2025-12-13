import React from 'react';
import { FileText, CheckCircle } from 'lucide-react';

interface DocumentsListProps {
    documents: string[];
}

export const DocumentsList: React.FC<DocumentsListProps> = ({ documents }) => {
    if (documents.length === 0) {
        return (
            <div className="text-center p-8 bg-gray-50 rounded-xl border border-gray-100">
                <p className="text-gray-500">No documents indexed yet.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-4 border-b border-gray-50 flex items-center justify-between bg-gray-50/50">
                <h3 className="font-semibold text-gray-800">Indexed Documents</h3>
                <span className="text-xs font-medium bg-blue-100 text-blue-700 px-2 py-1 rounded-full">{documents.length} Files</span>
            </div>
            <div className="divide-y divide-gray-50">
                {documents.map((doc, idx) => (
                    <div key={idx} className="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                        <div className="flex items-center">
                            <div className="p-2 bg-blue-50 rounded-lg mr-3">
                                <FileText className="w-5 h-5 text-blue-600" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-900">{doc}</p>
                                <div className="flex items-center mt-1">
                                    <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                                    <p className="text-xs text-green-600">Active in Vector Store</p>
                                </div>
                            </div>
                        </div>
                        {/* Future: Add delete button */}
                    </div>
                ))}
            </div>
        </div>
    );
};
