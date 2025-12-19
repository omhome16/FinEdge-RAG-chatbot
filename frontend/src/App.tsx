import { useState, useEffect } from 'react';
import {
  Upload, MessageSquare, FileText, Sparkles,
  ArrowRight, Github, Command, Moon, Sun,
  BarChart2, Activity, Eye
} from 'lucide-react';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { MetricCard, BarChartComponent, LineChartComponent, PieChartComponent, DataTable } from './components/charts';
import PDFViewer from './components/PDFViewer';
import {
  uploadFile,
  chatWithBot,
  getDocuments,
  clearAllDocuments,
  getDocumentAnalytics,
  type DocumentInfo,
  type AnalyticsResponse,
  type Citation
} from './api';

// ============ Components ============

function ThemeToggleBtn() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg text-primary hover:bg-secondary transition-colors"
      aria-label="Toggle theme"
    >
      {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
    </button>
  );
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
}

function AppContent() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'analytics' | 'chat'>('upload');

  // PDF Viewer state
  const [pdfViewerOpen, setPdfViewerOpen] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<string>('');
  const [loadingAnalytics, setLoadingAnalytics] = useState<string | null>(null);

  // Analytics filter state
  const [selectedYear, setSelectedYear] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (err) {
      console.log('No documents yet');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadFile(file);
      await fetchDocuments();
      if (response.analytics) {
        setAnalytics(response.analytics);
        setActiveTab('analytics');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isChatting) return;
    const userMessage = inputMessage.trim();
    setInputMessage('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsChatting(true);
    setError(null);

    try {
      const response = await chatWithBot(userMessage);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.answer,
        citations: response.citations
      }]);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Chat failed');
    } finally {
      setIsChatting(false);
    }
  };

  const handleClearAll = async () => {
    if (!confirm('Are you sure you want to delete all documents?')) return;
    try {
      await clearAllDocuments();
      setDocuments([]);
      setAnalytics(null);
      setMessages([]);
    } catch (err) {
      console.error('Failed to clear');
    }
  };

  // Load analytics for a specific document
  const handleViewAnalytics = async (docId: string) => {
    setLoadingAnalytics(docId);
    try {
      const docAnalytics = await getDocumentAnalytics(docId);
      setAnalytics(docAnalytics);
      setActiveTab('analytics');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analytics');
    } finally {
      setLoadingAnalytics(null);
    }
  };

  // Handle citation click to open PDF viewer
  const handleCitationClick = (citation: Citation) => {
    if (citation.doc_id) {
      setSelectedCitation(citation);
      setSelectedDocId(citation.doc_id);
      setPdfViewerOpen(true);
    }
  };

  const renderChart = (chart: any, index: number) => {
    // Inject vibrant colors if not present
    const colors = chart.colors || ['#3b82f6', '#8b5cf6', '#f43f5e', '#10b981', '#f59e0b'];

    switch (chart.chart_type) {
      case 'bar':
        return <BarChartComponent key={index} title={chart.title} data={chart.data} xKey={chart.x_key} yKeys={chart.y_keys} colors={colors} />;
      case 'line':
        return <LineChartComponent key={index} title={chart.title} data={chart.data} xKey={chart.x_key} yKeys={chart.y_keys} colors={colors} />;
      case 'pie':
        return <PieChartComponent key={index} title={chart.title} data={chart.data} colors={colors} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen mesh-bg text-primary">
      {/* Navbar */}
      <nav className="glass sticky top-0 flex items-center justify-between px-6 py-4 mb-8">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 flex items-center justify-center bg-primary text-secondary rounded-lg border border-strong">
            <span className="font-bold font-mono">F</span>
          </div>
          <span className="font-bold text-lg tracking-tight">FinEdge</span>
        </div>
        <div className="flex items-center gap-4">
          {documents.length > 0 && (
            <span className="text-xs font-mono px-3 py-1 rounded-full border border-subtle bg-secondary text-secondary hidden md:block">
              {documents.length} FILES INDEXED
            </span>
          )}
          <a href="https://github.com/omhome16" target="_blank" className="text-secondary hover:text-primary transition-colors">
            <Github className="w-5 h-5" />
          </a>
          <div className="h-4 w-px bg-border-subtle" />
          <ThemeToggleBtn />
        </div>
      </nav>

      {/* Main Container */}
      <main className="max-w-6xl mx-auto px-6 pb-20">

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-10">
          <div className="glass-card p-1 flex items-center gap-1 bg-secondary/50">
            {[
              { id: 'upload', label: 'Ingest', icon: Upload },
              { id: 'analytics', label: 'Intelligence', icon: Activity },
              { id: 'chat', label: 'RAG Chat', icon: MessageSquare },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                  ? 'bg-primary text-secondary shadow-sm'
                  : 'text-secondary hover:text-primary hover:bg-tertiary'
                  }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* content Area */}
        <div className="animate-float-in">

          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-500/5 border border-red-500/20 text-red-500 flex items-center gap-2 text-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
              {error}
            </div>
          )}

          {activeTab === 'upload' && (
            <div className="space-y-8">
              <div className="text-center space-y-2 mb-8">
                <h1 className="text-4xl font-bold tracking-tighter">Document Ingestion</h1>
                <p className="text-secondary opacity-80">Upload financial reports for deep analysis.</p>
              </div>

              <div className="glass-card p-12 max-w-2xl mx-auto border-dashed border-2 border-subtle hover:border-strong transition-colors cursor-pointer group relative overflow-hidden">
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.xlsx,.xls"
                  onChange={handleFileUpload}
                  disabled={isUploading}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div className="flex flex-col items-center gap-4 relative z-0">
                  <div className="p-4 rounded-full bg-secondary group-hover:scale-110 transition-transform duration-300">
                    <Upload className="w-8 h-8 text-primary" />
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-medium">Drop document here</p>
                    <p className="text-sm text-secondary mt-1">PDF, Word, Excel supported</p>
                    <p className="text-xs text-amber-500 mt-2 font-medium">Note: File size must be less than 120KB, due to processing limitations</p>
                  </div>
                </div>
                {isUploading && (
                  <div className="absolute inset-0 bg-primary/80 backdrop-blur-sm flex items-center justify-center z-20">
                    <div className="flex flex-col items-center gap-2">
                      <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                      <span className="text-sm font-mono animate-pulse">PROCESSING...</span>
                    </div>
                  </div>
                )}
              </div>

              {documents.length > 0 && (
                <div className="max-w-2xl mx-auto mt-12">
                  <div className="flex items-center justify-between mb-4 border-b border-subtle pb-2">
                    <h3 className="font-mono text-sm text-secondary">INDEXED_FILES</h3>
                    <button onClick={handleClearAll} className="text-xs text-red-500 hover:underline">CLEAR ALL</button>
                  </div>
                  <div className="space-y-2">
                    {documents.map((doc) => (
                      <div key={doc.doc_id} className="flex items-center justify-between p-4 glass-card bg-secondary/30 hover:bg-secondary/50">
                        <div className="flex items-center gap-3">
                          <FileText className="w-4 h-4 text-secondary" />
                          <span className="text-sm font-medium truncate max-w-[200px]">{doc.filename}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <button
                            onClick={() => handleViewAnalytics(doc.doc_id)}
                            disabled={loadingAnalytics === doc.doc_id}
                            className="doc-analytics-btn"
                          >
                            {loadingAnalytics === doc.doc_id ? (
                              <span className="animate-spin">⏳</span>
                            ) : (
                              <>
                                <Eye className="w-3 h-3" />
                                <span>View Analytics</span>
                              </>
                            )}
                          </button>
                          <div className="flex items-center gap-3 text-xs text-secondary font-mono">
                            <span>{doc.total_pages} PGS</span>
                            <span>•</span>
                            <span>{doc.total_tables} TBLS</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'analytics' && (
            <div>
              {analytics ? (
                <div className="space-y-8">
                  {/* Executive Summary */}
                  <div className="glass-card p-8 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4 opacity-5">
                      <Sparkles className="w-32 h-32" />
                    </div>
                    <div className="relative z-10">
                      <span className="inline-block px-3 py-1 rounded-full border border-subtle text-xs font-mono mb-4 text-secondary">
                        AI_GENERATED_INSIGHTS
                      </span>
                      <h2 className="text-2xl font-bold mb-4">{analytics.document_type}</h2>
                      <p className="text-lg leading-relaxed opacity-90">{analytics.summary}</p>
                    </div>
                  </div>

                  {/* Table Breakdown Summary */}
                  {analytics.table_breakdown && analytics.table_breakdown.total_count > 0 && (
                    <div className="glass-card p-6">
                      <h3 className="text-sm font-mono text-secondary mb-4">TABLE ANALYSIS BREAKDOWN</h3>
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <div className="text-center p-3 rounded-lg bg-primary/10 border border-primary/30">
                          <div className="text-2xl font-bold text-primary">{analytics.table_breakdown.total_count}</div>
                          <div className="text-xs text-secondary">Total Tables</div>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-green-500/10 border border-green-500/30">
                          <div className="text-2xl font-bold text-green-500">{analytics.table_breakdown.primary_count}</div>
                          <div className="text-xs text-secondary">Primary</div>
                          <div className="text-[10px] opacity-60">Core Financial</div>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
                          <div className="text-2xl font-bold text-blue-500">{analytics.table_breakdown.secondary_count}</div>
                          <div className="text-xs text-secondary">Secondary</div>
                          <div className="text-[10px] opacity-60">Supporting Data</div>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-gray-500/10 border border-gray-500/30">
                          <div className="text-2xl font-bold text-gray-400">{analytics.table_breakdown.reference_count}</div>
                          <div className="text-xs text-secondary">Reference</div>
                          <div className="text-[10px] opacity-60">Notes/Disclosures</div>
                        </div>
                        <div className="text-center p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
                          <div className="text-2xl font-bold text-purple-500">{analytics.table_breakdown.analyzed_count}</div>
                          <div className="text-xs text-secondary">Analyzed</div>
                          <div className="text-[10px] opacity-60">For Dashboard</div>
                        </div>
                      </div>
                      <div className="mt-4 h-2 bg-secondary rounded-full overflow-hidden flex">
                        <div
                          className="bg-green-500"
                          style={{ width: `${(analytics.table_breakdown.primary_count / analytics.table_breakdown.total_count) * 100}%` }}
                        />
                        <div
                          className="bg-blue-500"
                          style={{ width: `${(analytics.table_breakdown.secondary_count / analytics.table_breakdown.total_count) * 100}%` }}
                        />
                        <div
                          className="bg-gray-500"
                          style={{ width: `${(analytics.table_breakdown.reference_count / analytics.table_breakdown.total_count) * 100}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Dynamic Filters */}
                  {analytics.available_filters && (
                    Object.values(analytics.available_filters).some(arr => arr && arr.length > 0) && (
                      <div className="glass-card p-4 flex flex-wrap items-center gap-4">
                        <span className="text-xs font-mono text-secondary">FILTERS:</span>

                        {analytics.available_filters.years?.length > 0 && (
                          <div className="flex items-center gap-2">
                            <label className="text-sm text-secondary">Year:</label>
                            <select
                              value={selectedYear}
                              onChange={(e) => setSelectedYear(e.target.value)}
                              className="px-3 py-1.5 rounded-lg bg-secondary border border-subtle text-sm focus:outline-none focus:border-primary"
                            >
                              <option value="all">All Years</option>
                              {analytics.available_filters.years.map(year => (
                                <option key={year} value={year}>{year}</option>
                              ))}
                            </select>
                          </div>
                        )}

                        {analytics.available_filters.categories?.length > 0 && (
                          <div className="flex items-center gap-2">
                            <label className="text-sm text-secondary">Category:</label>
                            <select
                              value={selectedCategory}
                              onChange={(e) => setSelectedCategory(e.target.value)}
                              className="px-3 py-1.5 rounded-lg bg-secondary border border-subtle text-sm focus:outline-none focus:border-primary"
                            >
                              <option value="all">All Categories</option>
                              {analytics.available_filters.categories.map(cat => (
                                <option key={cat} value={cat}>{cat}</option>
                              ))}
                            </select>
                          </div>
                        )}

                        {analytics.available_filters.quarters?.length > 0 && (
                          <div className="text-xs text-secondary">
                            Quarters: {analytics.available_filters.quarters.join(', ')}
                          </div>
                        )}

                        {(selectedYear !== 'all' || selectedCategory !== 'all') && (
                          <button
                            onClick={() => { setSelectedYear('all'); setSelectedCategory('all'); }}
                            className="text-xs text-red-500 hover:underline"
                          >
                            Clear Filters
                          </button>
                        )}
                      </div>
                    )
                  )}

                  {/* Key Metrics */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {analytics.metrics.map((metric, i) => (
                      <MetricCard key={i} {...metric} />
                    ))}
                  </div>

                  {/* Charts Grid */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {analytics.charts.map((chart, i) => renderChart(chart, i))}
                  </div>

                  {/* Tables */}
                  <div className="space-y-6">
                    {analytics.tables.map((table, i) => (
                      <DataTable key={i} {...table} />
                    ))}
                  </div>

                  {/* Key Insights List */}
                  <div className="glass-card p-8">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                      <Command className="w-5 h-5" />
                      Strategic Takeaways
                    </h3>
                    <div className="grid gap-4">
                      {analytics.key_insights.map((insight, i) => (
                        <div key={i} className="flex gap-4 p-4 rounded-lg bg-secondary/50 border border-transparent hover:border-border-subtle transition-colors">
                          <div className="w-6 h-6 rounded-full bg-primary text-secondary flex items-center justify-center flex-shrink-0 text-xs font-mono border border-subtle">
                            {i + 1}
                          </div>
                          <p className="opacity-90">{insight}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center p-20 glass-card">
                  <div className="bg-secondary p-6 rounded-full mb-6 animate-pulse-glow">
                    <BarChart2 className="w-10 h-10 opacity-50" />
                  </div>
                  <h3 className="text-xl font-medium mb-2">No Intelligence Data</h3>
                  <p className="text-secondary text-sm">Upload a document to generate analytics.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="glass-card h-[calc(100vh-14rem)] flex flex-col relative overflow-hidden">
              {/* Decorative background blur */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary rounded-full blur-[100px] -z-10 opacity-50" />

              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center opacity-60">
                    <MessageSquare className="w-12 h-12 mb-4 opacity-50" />
                    <p className="text-lg">Financial Assistant Ready</p>
                  </div>
                ) : (
                  messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[85%] p-5 rounded-2xl ${msg.role === 'user'
                        ? 'bg-primary text-secondary border border-strong'
                        : 'glass border border-subtle'
                        }`}>
                        <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                        {msg.citations && msg.citations.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-dashed border-subtle">
                            <p className="text-[10px] font-mono uppercase tracking-wider opacity-60 mb-2">Sources:</p>
                            <div className="flex flex-wrap gap-2">
                              {msg.citations.map((c, j) => (
                                <button
                                  key={j}
                                  onClick={() => handleCitationClick(c)}
                                  className="px-2 py-1 text-[10px] rounded border border-subtle bg-secondary/50 font-mono flex items-center gap-1 hover:bg-secondary hover:border-primary cursor-pointer transition-colors"
                                  title={`Click to view: ${c.text_snippet}`}
                                >
                                  <FileText className="w-3 h-3" />
                                  {c.source.split('/').pop()} : P{c.page_number}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
                {isChatting && (
                  <div className="flex justify-start">
                    <div className="px-4 py-3 rounded-2xl glass flex items-center gap-1">
                      <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                      <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                      <span className="w-1.5 h-1.5 bg-current rounded-full animate-bounce"></span>
                    </div>
                  </div>
                )}
              </div>

              <div className="p-4 glass border-t border-subtle">
                <div className="relative">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Ask specific questions about the financials..."
                    className="w-full pl-6 pr-14 py-4 rounded-xl bg-secondary/50 border border-subtle focus:border-strong focus:bg-primary transition-all outline-none"
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isChatting}
                    className="absolute right-2 top-2 p-2 rounded-lg bg-primary text-secondary hover:opacity-90 disabled:opacity-50 transition-all"
                  >
                    <ArrowRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* PDF Viewer Sidebar */}
      <PDFViewer
        isOpen={pdfViewerOpen}
        onClose={() => setPdfViewerOpen(false)}
        citation={selectedCitation}
        docId={selectedDocId}
      />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
