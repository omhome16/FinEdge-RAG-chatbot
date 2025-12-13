"""
FinEdge Analytics Engine v2.0
AI-driven analytics generation based on document content.
Dynamically determines what charts, tables, and metrics to display.
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


# ============ Table Categorization System ============

class TableCategorizer:
    """
    Categorizes financial tables into priority tiers for smart analytics.
    
    Categories:
    - PRIMARY: Core financial statements (Income Statement, Balance Sheet, Cash Flow)
    - SECONDARY: Important supporting data (Segment Revenue, Geographic, Key Metrics)
    - REFERENCE: Notes, disclosures, and supplementary information
    """
    
    # Keywords that indicate PRIMARY tables (core financial statements)
    PRIMARY_KEYWORDS = [
        'income statement', 'profit and loss', 'p&l', 'statement of operations',
        'balance sheet', 'statement of financial position', 'assets and liabilities',
        'cash flow', 'statement of cash flows', 'cash flows from',
        'comprehensive income', 'shareholders equity', 'stockholders equity',
        'statement of changes', 'consolidated statement', 'financial highlights',
        'revenue', 'net income', 'gross profit', 'operating income', 'ebitda',
        'total assets', 'total liabilities', 'total equity', 'earnings per share'
    ]
    
    # Keywords that indicate SECONDARY tables (important supporting data)
    SECONDARY_KEYWORDS = [
        'segment', 'geographic', 'region', 'business unit', 'division',
        'quarterly', 'q1', 'q2', 'q3', 'q4', 'year over year', 'yoy',
        'ratio', 'margin', 'growth', 'comparison', 'breakdown',
        'revenue by', 'sales by', 'cost by', 'expense by',
        'key metrics', 'kpi', 'performance', 'summary',
        'product', 'service', 'customer', 'market'
    ]
    
    # Keywords that indicate REFERENCE tables (notes and disclosures)
    REFERENCE_KEYWORDS = [
        'note', 'footnote', 'disclosure', 'accounting policy', 'policies',
        'schedule', 'supplementary', 'additional', 'appendix',
        'tax', 'deferred', 'contingent', 'commitment', 'lease',
        'related party', 'fair value', 'derivative', 'hedge',
        'pension', 'benefit', 'stock option', 'compensation'
    ]
    
    @classmethod
    def categorize_table(cls, table: Dict) -> str:
        """Categorize a single table based on its caption and content."""
        caption = table.get('caption', '').lower()
        markdown = table.get('markdown', '').lower()
        combined_text = f"{caption} {markdown[:500]}"  # Check caption + start of content
        
        # Check for PRIMARY keywords first (highest priority)
        for keyword in cls.PRIMARY_KEYWORDS:
            if keyword in combined_text:
                return 'PRIMARY'
        
        # Check for SECONDARY keywords
        for keyword in cls.SECONDARY_KEYWORDS:
            if keyword in combined_text:
                return 'SECONDARY'
        
        # Check for REFERENCE keywords
        for keyword in cls.REFERENCE_KEYWORDS:
            if keyword in combined_text:
                return 'REFERENCE'
        
        # Default to REFERENCE if no keywords match
        return 'REFERENCE'
    
    @classmethod
    def categorize_tables(cls, tables: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize all tables and return grouped by category."""
        categorized = {
            'PRIMARY': [],
            'SECONDARY': [],
            'REFERENCE': []
        }
        
        for table in tables:
            category = cls.categorize_table(table)
            categorized[category].append(table)
        
        return categorized
    
    @classmethod
    def get_priority_tables(cls, tables: List[Dict], max_primary: int = 10, max_secondary: int = 10) -> Tuple[List[Dict], Dict[str, int]]:
        """
        Get priority-ordered tables for analytics.
        Returns: (selected_tables, breakdown_counts)
        """
        categorized = cls.categorize_tables(tables)
        
        # Select tables by priority
        selected = []
        selected.extend(categorized['PRIMARY'][:max_primary])
        selected.extend(categorized['SECONDARY'][:max_secondary])
        
        # Create breakdown summary
        breakdown = {
            'primary_count': len(categorized['PRIMARY']),
            'secondary_count': len(categorized['SECONDARY']),
            'reference_count': len(categorized['REFERENCE']),
            'total_count': len(tables),
            'analyzed_count': len(selected)
        }
        
        return selected, breakdown


@dataclass
class MetricCard:
    """A single metric/KPI card."""
    label: str
    value: str
    change: Optional[str] = None
    change_type: Optional[str] = None  # "positive", "negative", "neutral"
    icon: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ChartData:
    """Data for a chart visualization."""
    chart_type: str  # "bar", "line", "pie", "area"
    title: str
    data: List[Dict[str, Any]]
    x_key: str
    y_keys: List[str]
    colors: Optional[List[str]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TableDisplay:
    """A table for display."""
    title: str
    headers: List[str]
    rows: List[List[str]]
    highlight_rows: Optional[List[int]] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AnalyticsResult:
    """Complete analytics result for a document."""
    document_type: str
    summary: str
    metrics: List[MetricCard]
    charts: List[ChartData]
    tables: List[TableDisplay]
    key_insights: List[str]
    available_filters: Dict[str, List[str]] = field(default_factory=dict)
    raw_tables: List[Dict] = field(default_factory=list)
    table_breakdown: Dict[str, int] = field(default_factory=dict)  # NEW: Table category counts
    
    def to_dict(self) -> Dict:
        return {
            "document_type": self.document_type,
            "summary": self.summary,
            "metrics": [m.to_dict() for m in self.metrics],
            "charts": [c.to_dict() for c in self.charts],
            "tables": [t.to_dict() for t in self.tables],
            "key_insights": self.key_insights,
            "available_filters": self.available_filters,
            "raw_tables": self.raw_tables,
            "table_breakdown": self.table_breakdown
        }


class AnalyticsEngine:
    """
    AI-powered analytics engine that analyzes documents and generates
    appropriate visualizations based on content.
    """
    
    ANALYSIS_PROMPT = """You are a senior financial analyst AI. Analyze the following document content and generate COMPREHENSIVE analytics.

DOCUMENT CONTENT:
{content}

TABLES FOUND:
{tables}

NUMBER OF TABLES IN DOCUMENT: {table_count}

Generate a DETAILED analytics response in the following JSON format:
{{
    "document_type": "financial_statement" | "annual_report" | "quarterly_report" | "invoice" | "contract" | "balance_sheet" | "income_statement" | "cash_flow" | "spreadsheet" | "other",
    "summary": "Detailed executive summary (4-6 sentences covering key findings, trends, and notable data points)",
    "available_filters": {{
        "years": ["2023", "2024"],
        "categories": ["Revenue", "Expenses", "Assets"],
        "quarters": ["Q1", "Q2", "Q3", "Q4"],
        "departments": []
    }},
    "metrics": [
        {{
            "label": "Metric name",
            "value": "Value with units (e.g., $1.2M, 15%, 3.5x)",
            "change": "+15% YoY" or null,
            "change_type": "positive" | "negative" | "neutral" | null,
            "icon": "dollar" | "chart" | "trending-up" | "trending-down" | "file-text" | "calendar" | "percent" | "users",
            "year": "2024" or null,
            "category": "Revenue" or null
        }}
    ],
    "charts": [
        {{
            "chart_type": "bar" | "line" | "pie" | "area",
            "title": "Chart title",
            "data": [
                {{"name": "Category", "value": 100, "year": "2023"}},
                {{"name": "Category 2", "value": 200, "year": "2024"}}
            ],
            "x_key": "name",
            "y_keys": ["value"],
            "colors": ["#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#F43F5E"]
        }}
    ],
    "tables": [
        {{
            "title": "Table title",
            "headers": ["Column 1", "Column 2", "Column 3"],
            "rows": [["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"]],
            "highlight_rows": [0],
            "sortable": true
        }}
    ],
    "key_insights": [
        "Detailed insight 1 with specific data points and context",
        "Detailed insight 2 explaining trends or changes",
        "Insight 3 about risks or opportunities",
        "Insight 4 with comparative analysis",
        "Insight 5 with recommendations or implications"
    ]
}}

ENHANCED ANALYSIS RULES:
1. Generate 4-8 metrics covering ALL key financial indicators found
2. Generate 2-4 charts that visualize different aspects of the data
3. ONLY include tables that were provided above - do NOT create placeholders for tables you don't have content for
4. If a table has no content provided, do NOT include it in your response
5. Extract and list ALL years/dates found in the document for filtering
6. Identify categories/departments for filtering (Revenue, Expenses, Assets, Liabilities, etc.)
7. For financial statements: include revenue, costs, profit margins, growth rates, ratios
8. For balance sheets: include assets, liabilities, equity, liquidity ratios
9. For income statements: include gross profit, operating income, net income, EPS
10. Add year/category metadata to metrics and chart data for filtering
11. Make tables sortable when they contain numerical data
12. Calculate and show YoY (Year over Year) changes where data is available
13. Identify trends, anomalies, and noteworthy patterns
14. Include both absolute values and percentages where relevant

Return ONLY the JSON object, no markdown formatting."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.1
        )
    
    def analyze_document(
        self, 
        content: str, 
        tables: List[Dict] = None,
        max_content_length: int = 40000
    ) -> AnalyticsResult:
        """
        Analyze document content and generate appropriate analytics.
        Uses smart table prioritization to focus on important tables.
        
        Args:
            content: The document text content
            tables: List of extracted tables in dict format
            max_content_length: Maximum characters to analyze
            
        Returns:
            AnalyticsResult with charts, metrics, insights, and table breakdown
        """
        # Truncate content if too long
        truncated_content = content[:max_content_length]
        if len(content) > max_content_length:
            truncated_content += f"\n\n[Content truncated - {len(content) - max_content_length} more characters]"
        
        # Use smart table prioritization
        table_breakdown = {}
        tables_text = "None found"
        table_count = len(tables) if tables else 0
        
        if tables:
            # Get priority tables using TableCategorizer
            priority_tables, table_breakdown = TableCategorizer.get_priority_tables(
                tables, 
                max_primary=10, 
                max_secondary=10
            )
            
            # Only include tables that have actual content
            tables_with_content = [
                t for t in priority_tables 
                if t.get('markdown') and len(t.get('markdown', '').strip()) > 10
            ]
            
            tables_text = "\n\n".join([
                f"Table {i+1} ({TableCategorizer.categorize_table(t)}): {t.get('caption', 'Untitled')}\n{t.get('markdown', '')}"
                for i, t in enumerate(tables_with_content)
            ])
            
            # Add summary for context
            tables_text = f"""TABLES SUMMARY:
- Total tables in document: {table_breakdown['total_count']}
- Primary (Core Financial): {table_breakdown['primary_count']}
- Secondary (Supporting Data): {table_breakdown['secondary_count']}  
- Reference (Notes/Disclosures): {table_breakdown['reference_count']}
- Tables included for analysis: {table_breakdown['analyzed_count']}

INCLUDED TABLES (Priority-selected):
{tables_text}

Note: Only analyze the tables shown above. Do not reference or create placeholders for tables not included."""
        
        prompt = self.ANALYSIS_PROMPT.format(
            content=truncated_content,
            tables=tables_text,
            table_count=table_count
        )
        
        try:
            response = self.llm.invoke(prompt)
            result_json = self._parse_json_response(response.content)
            return self._create_analytics_result(result_json, tables or [], table_breakdown)
        except Exception as e:
            print(f"Analytics generation error: {e}")
            return self._create_fallback_result(str(e), tables or [])
    
    def analyze_for_streaming(
        self, 
        content: str, 
        tables: List[Dict] = None,
        chunk_size: int = 10000
    ):
        """
        Generator that yields analytics in chunks for large documents.
        Useful for showing progress on very large files.
        """
        # For now, just analyze the full content
        # Can be enhanced to process in stages
        yield {"status": "analyzing", "progress": 0}
        
        result = self.analyze_document(content, tables)
        
        yield {"status": "complete", "progress": 100, "result": result.to_dict()}
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from LLM response, handling common issues."""
        # Clean up response
        content = response.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        return json.loads(content.strip())
    
    def _create_analytics_result(self, data: Dict, raw_tables: List[Dict] = None, table_breakdown: Dict[str, int] = None) -> AnalyticsResult:
        """Convert parsed JSON to AnalyticsResult object."""
        metrics = [
            MetricCard(
                label=m.get("label", ""),
                value=m.get("value", ""),
                change=m.get("change"),
                change_type=m.get("change_type"),
                icon=m.get("icon")
            )
            for m in data.get("metrics", [])
        ]
        
        charts = [
            ChartData(
                chart_type=c.get("chart_type", "bar"),
                title=c.get("title", ""),
                data=c.get("data", []),
                x_key=c.get("x_key", "name"),
                y_keys=c.get("y_keys", ["value"]),
                colors=c.get("colors")
            )
            for c in data.get("charts", [])
        ]
        
        tables = [
            TableDisplay(
                title=t.get("title", ""),
                headers=t.get("headers", []),
                rows=t.get("rows", []),
                highlight_rows=t.get("highlight_rows")
            )
            for t in data.get("tables", [])
        ]
        
        # Extract available filters from LLM response
        available_filters = data.get("available_filters", {
            "years": [],
            "categories": [],
            "quarters": [],
            "departments": []
        })
        
        return AnalyticsResult(
            document_type=data.get("document_type", "unknown"),
            summary=data.get("summary", ""),
            metrics=metrics,
            charts=charts,
            tables=tables,
            key_insights=data.get("key_insights", []),
            available_filters=available_filters,
            raw_tables=raw_tables or [],
            table_breakdown=table_breakdown
        )
    
    def _create_fallback_result(self, error: str, raw_tables: List[Dict] = None, table_breakdown: Dict[str, int] = None) -> AnalyticsResult:
        """Create a fallback result when analysis fails."""
        return AnalyticsResult(
            document_type="unknown",
            summary=f"Unable to fully analyze document: {error}",
            metrics=[
                MetricCard(
                    label="Document Processed",
                    value="Yes",
                    icon="file-text"
                )
            ],
            charts=[],
            tables=[],
            key_insights=["Document was processed but detailed analytics could not be generated."],
            available_filters={"years": [], "categories": [], "quarters": [], "departments": []},
            raw_tables=raw_tables or [],
            table_breakdown=table_breakdown or {}
        )


# Singleton instance
analytics_engine = AnalyticsEngine()


def analyze_document(content: str, tables: List[Dict] = None) -> Dict:
    """Convenience function to analyze a document."""
    result = analytics_engine.analyze_document(content, tables)
    return result.to_dict()
