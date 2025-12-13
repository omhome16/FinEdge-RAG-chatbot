import axios from 'axios';

export const api = axios.create({
    baseURL: 'http://localhost:8000',
});

// Types
export interface DocumentInfo {
    doc_id: string;
    filename: string;
    file_type: string;
    total_pages: number;
    total_chunks: number;
    total_tables: number;
}

export interface Citation {
    source: string;
    page_number: number;
    text_snippet: string;
    doc_id?: string;
    chunk_type?: string;
    bbox?: number[];  // [x0, y0, x1, y1] for PDF highlighting
}

export interface ChatResponse {
    answer: string;
    citations: Citation[];
    sources: string[];
    tables: any[];
    is_financial_query: boolean;
}

export interface MetricData {
    label: string;
    value: string;
    change?: string;
    change_type?: 'positive' | 'negative' | 'neutral';
    icon?: string;
}

export interface ChartData {
    chart_type: 'bar' | 'line' | 'pie' | 'area';
    title: string;
    data: Record<string, any>[];
    x_key: string;
    y_keys: string[];
    colors?: string[];
}

export interface TableData {
    title: string;
    headers: string[];
    rows: string[][];
    highlight_rows?: number[];
    sortable?: boolean;
}

export interface AvailableFilters {
    years: string[];
    categories: string[];
    quarters: string[];
    departments: string[];
}

export interface TableBreakdown {
    primary_count: number;
    secondary_count: number;
    reference_count: number;
    total_count: number;
    analyzed_count: number;
}

export interface AnalyticsResponse {
    document_type: string;
    summary: string;
    metrics: MetricData[];
    charts: ChartData[];
    tables: TableData[];
    key_insights: string[];
    available_filters?: AvailableFilters;
    raw_tables?: any[];
    table_breakdown?: TableBreakdown;
}

export interface UploadResponse {
    filename: string;
    doc_id: string;
    status: string;
    pages: number;
    chunks: number;
    tables: number;
    analytics?: AnalyticsResponse;
}

// API Functions
export const uploadFile = async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const chatWithBot = async (query: string): Promise<ChatResponse> => {
    const response = await api.post('/chat', { query });
    return response.data;
};

export const getAnalytics = async (): Promise<AnalyticsResponse> => {
    const response = await api.get('/analyze');
    return response.data;
};

// Get analytics for a specific document (from cache)
export const getDocumentAnalytics = async (docId: string): Promise<AnalyticsResponse> => {
    const response = await api.get(`/analyze/${docId}`);
    return response.data;
};

// Get PDF URL for viewer - uses the backend PDF serving endpoint
export const getPdfUrl = (docId: string): string => {
    return `${API_BASE_URL}/pdf/${docId}`;
};

export const getDocuments = async (): Promise<DocumentInfo[]> => {
    const response = await api.get('/documents');
    return response.data;
};

export const clearAllDocuments = async () => {
    const response = await api.delete('/documents');
    return response.data;
};

export const clearChatHistory = async () => {
    const response = await api.post('/chat/clear');
    return response.data;
};

export const getHealth = async () => {
    const response = await api.get('/health');
    return response.data;
};

