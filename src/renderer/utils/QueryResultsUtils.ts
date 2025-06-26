export interface QueryResultStats {
  totalRows: number;
  totalColumns: number;
  executionTime: number;
  hasError: boolean;
  errorMessage?: string;
  dataTypes: { [column: string]: string };
}

export interface FormattedCell {
  value: any;
  displayValue: string;
  type: 'string' | 'number' | 'boolean' | 'date' | 'null' | 'object';
  isNull: boolean;
}

export class QueryResultsUtils {
  /**
   * Analyze query results and return statistics
   */
  static analyzeResults(results: any): QueryResultStats {
    const stats: QueryResultStats = {
      totalRows: 0,
      totalColumns: 0,
      executionTime: results?.executionTime || 0,
      hasError: Boolean(results?.error),
      errorMessage: results?.error,
      dataTypes: {}
    };

    if (results?.rows && results?.columns) {
      stats.totalRows = results.rows.length;
      stats.totalColumns = results.columns.length;

      // Analyze data types for each column
      if (results.rows.length > 0) {
        results.columns.forEach((column: string, index: number) => {
          const sampleValues = results.rows
            .slice(0, Math.min(100, results.rows.length))
            .map((row: any[]) => row[index])
            .filter((val: any) => val !== null && val !== undefined);

          stats.dataTypes[column] = this.inferDataType(sampleValues);
        });
      }
    }

    return stats;
  }

  /**
   * Format a cell value for display
   */
  static formatCell(value: any): FormattedCell {
    if (value === null || value === undefined) {
      return {
        value: null,
        displayValue: 'NULL',
        type: 'null',
        isNull: true
      };
    }

    const type = this.getValueType(value);
    let displayValue: string;

    switch (type) {
      case 'date':
        displayValue = new Date(value).toLocaleString();
        break;
      case 'boolean':
        displayValue = value ? 'TRUE' : 'FALSE';
        break;
      case 'number':
        displayValue = typeof value === 'number' ?
          (Number.isInteger(value) ? value.toString() : value.toFixed(6).replace(/\.?0+$/, '')) :
          String(value);
        break;
      case 'object':
        displayValue = JSON.stringify(value);
        break;
      default:
        displayValue = String(value);
    }

    return {
      value,
      displayValue,
      type,
      isNull: false
    };
  }

  /**
   * Export results to CSV format
   */
  static exportToCSV(results: any, filename?: string): void {
    if (!results?.rows || !results?.columns || results.rows.length === 0 || results.columns.length === 0) {
      throw new Error('No data to export');
    }

    const csvContent = [
      // Header row
      results.columns.map((col: string) => this.escapeCsvValue(col)).join(','),
      // Data rows
      ...results.rows.map((row: any[]) =>
        row.map(cell => {
          const formatted = this.formatCell(cell);
          return this.escapeCsvValue(formatted.displayValue);
        }).join(',')
      )
    ].join('\n');

    this.downloadFile(
      csvContent,
      filename || `query_results_${this.getTimestamp()}.csv`,
      'text/csv'
    );
  }

  /**
   * Export results to JSON format
   */
  static exportToJSON(results: any, filename?: string): void {
    if (!results?.rows || !results?.columns || results.rows.length === 0 || results.columns.length === 0) {
      throw new Error('No data to export');
    }

    const jsonData = results.rows.map((row: any[]) => {
      const obj: any = {};
      results.columns.forEach((col: string, index: number) => {
        obj[col] = row[index];
      });
      return obj;
    });

    const jsonContent = JSON.stringify({
      metadata: {
        exportedAt: new Date().toISOString(),
        totalRows: results.rows.length,
        totalColumns: results.columns.length,
        executionTime: results.executionTime
      },
      columns: results.columns,
      data: jsonData
    }, null, 2);

    this.downloadFile(
      jsonContent,
      filename || `query_results_${this.getTimestamp()}.json`,
      'application/json'
    );
  }

  /**
   * Export results to Excel format (TSV)
   */
  static exportToExcel(results: any, filename?: string): void {
    if (!results?.rows || !results?.columns || results.rows.length === 0 || results.columns.length === 0) {
      throw new Error('No data to export');
    }

    const tsvContent = [
      // Header row
      results.columns.join('\t'),
      // Data rows
      ...results.rows.map((row: any[]) =>
        row.map(cell => {
          const formatted = this.formatCell(cell);
          return formatted.displayValue.replace(/\t/g, ' ');
        }).join('\t')
      )
    ].join('\n');

    this.downloadFile(
      tsvContent,
      filename || `query_results_${this.getTimestamp()}.xlsx`,
      'application/vnd.ms-excel'
    );
  }

  /**
   * Filter rows based on search term
   */
  static filterRows(rows: any[][], searchTerm: string): any[][] {
    if (!searchTerm.trim()) return rows;

    const term = searchTerm.toLowerCase();
    return rows.filter(row =>
      row.some(cell => {
        const formatted = this.formatCell(cell);
        return formatted.displayValue.toLowerCase().includes(term);
      })
    );
  }

  /**
   * Sort rows by column
   */
  static sortRows(rows: any[][], columnIndex: number, direction: 'asc' | 'desc'): any[][] {
    return [...rows].sort((a, b) => {
      const aVal = a[columnIndex];
      const bVal = b[columnIndex];

      // Handle null values
      if (aVal === null || aVal === undefined) return direction === 'asc' ? 1 : -1;
      if (bVal === null || bVal === undefined) return direction === 'asc' ? -1 : 1;

      // Compare values
      if (aVal < bVal) return direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return direction === 'asc' ? 1 : -1;
      return 0;
    });
  }

  /**
   * Get paginated rows
   */
  static paginateRows(rows: any[][], page: number, rowsPerPage: number): any[][] {
    const startIndex = page * rowsPerPage;
    return rows.slice(startIndex, startIndex + rowsPerPage);
  }

  // Private helper methods
  private static inferDataType(values: any[]): string {
    if (values.length === 0) return 'unknown';

    const types = values.map(val => this.getValueType(val));
    const typeCount = types.reduce((acc, type) => {
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });

    // Return the most common type
    return Object.keys(typeCount).reduce((a, b) =>
      typeCount[a] > typeCount[b] ? a : b
    );
  }

  private static getValueType(value: any): 'string' | 'number' | 'boolean' | 'date' | 'object' {
    if (typeof value === 'boolean') return 'boolean';
    if (typeof value === 'number') return 'number';
    if (value instanceof Date) return 'date';
    if (typeof value === 'string') {
      // Check if it's a date string
      if (!isNaN(Date.parse(value)) && /\d{4}-\d{2}-\d{2}/.test(value)) {
        return 'date';
      }
      // Check if it's a number string
      if (!isNaN(Number(value)) && value.trim() !== '') {
        return 'number';
      }
      return 'string';
    }
    if (typeof value === 'object') return 'object';
    return 'string';
  }

  private static escapeCsvValue(value: string): string {
    if (value.includes(',') || value.includes('"') || value.includes('\n')) {
      return `"${value.replace(/"/g, '""')}"`;
    }
    return value;
  }

  private static downloadFile(content: string, filename: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  private static getTimestamp(): string {
    return new Date().toISOString().slice(0, 19).replace(/:/g, '-');
  }
}