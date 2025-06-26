import React, { useState, useMemo } from 'react';
import { QueryResultsUtils, FormattedCell } from '../utils/QueryResultsUtils';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Button,
  Chip,
  Tooltip,
  Menu,
  MenuItem,
  TablePagination,
  Alert,
} from '@mui/material';
import {
  Info as InfoIcon,
  Search as SearchIcon,
  GetApp as ExportIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

interface ResultsPanelProps {
  results: any;
  onRefresh?: () => void;
  onClose?: () => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
      style={{ height: '100%' }}
    >
      {value === index && (
        <Box sx={{ height: '100%' }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const ResultsPanel: React.FC<ResultsPanelProps> = ({ results, onRefresh, onClose }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(100);
  const [exportMenuAnchor, setExportMenuAnchor] = useState<null | HTMLElement>(null);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };



  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(0); // Reset to first page when searching
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleExportClick = (event: React.MouseEvent<HTMLElement>) => {
    setExportMenuAnchor(event.currentTarget);
  };

  const handleExportClose = () => {
    setExportMenuAnchor(null);
  };

  const exportToCSV = () => {
    try {
      const exportData = {
        ...results,
        rows: filteredRows
      };
      QueryResultsUtils.exportToCSV(exportData);
      handleExportClose();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const exportToJSON = () => {
    try {
      const exportData = {
        ...results,
        rows: filteredRows
      };
      QueryResultsUtils.exportToJSON(exportData);
      handleExportClose();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const exportToExcel = () => {
    try {
      const exportData = {
        ...results,
        rows: filteredRows
      };
      QueryResultsUtils.exportToExcel(exportData);
      handleExportClose();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Filter and paginate data
  const filteredRows = useMemo(() => {
    if (!results?.rows) return [];
    return QueryResultsUtils.filterRows(results.rows, searchTerm);
  }, [results?.rows, searchTerm]);

  const paginatedRows = useMemo(() => {
    return QueryResultsUtils.paginateRows(filteredRows, page, rowsPerPage);
  }, [filteredRows, page, rowsPerPage]);

  // Get query statistics
  const queryStats = useMemo(() => {
    return QueryResultsUtils.analyzeResults(results);
  }, [results]);

  if (!results) {
    return null;
  }

  const hasError = results.error;
  const hasData = results.rows && results.rows.length > 0;
  const executionTime = results.executionTime || 0;
  const rowCount = results.rows ? results.rows.length : 0;

  return (
    <Paper
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderTop: 1,
        borderColor: 'divider',
        backgroundColor: 'background.paper',
        borderRadius: 0,
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          px: 2,
          py: 1,
          borderBottom: 1,
          borderColor: 'divider',
          backgroundColor: 'background.default',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {onRefresh && (
            <Tooltip title="Refresh">
              <IconButton size="small" onClick={onRefresh}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          )}

          <Typography variant="subtitle2" sx={{ fontSize: 13, fontWeight: 600 }}>
            Query Results
          </Typography>

          {hasError ? (
            <Chip
              icon={<ErrorIcon />}
              label="Error"
              color="error"
              size="small"
              sx={{ fontSize: 11 }}
            />
          ) : hasData ? (
            <Chip
              icon={<SuccessIcon />}
              label={`${rowCount} rows`}
              color="success"
              size="small"
              sx={{ fontSize: 11 }}
            />
          ) : (
            <Chip
              icon={<InfoIcon />}
              label="No data"
              color="info"
              size="small"
              sx={{ fontSize: 11 }}
            />
          )}

          {executionTime > 0 && (
            <Typography variant="caption" color="text.secondary">
              {executionTime}ms
            </Typography>
          )}
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {hasData && (
            <>
              <TextField
                size="small"
                placeholder="Search..."
                value={searchTerm}
                onChange={handleSearchChange}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
                sx={{ width: 200 }}
              />
              <Tooltip title="Export data">
                <IconButton size="small" onClick={handleExportClick}>
                  <ExportIcon />
                </IconButton>
              </Tooltip>
              <Menu
                anchorEl={exportMenuAnchor}
                open={Boolean(exportMenuAnchor)}
                onClose={handleExportClose}
              >
                <MenuItem onClick={exportToCSV}>Export as CSV</MenuItem>
                <MenuItem onClick={exportToJSON}>Export as JSON</MenuItem>
                <MenuItem onClick={exportToExcel}>Export as Excel</MenuItem>
              </Menu>
            </>
          )}

          {onClose && (
            <Tooltip title="Close">
              <IconButton size="small" onClick={onClose}>
                <CloseIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </Box>

      {/* Content */}
      <Box sx={{ flexGrow: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
          {hasError ? (
            <Box sx={{ p: 2 }}>
              <Alert severity="error" sx={{ fontSize: 12 }}>
                <Typography variant="body2" component="pre" sx={{ fontSize: 12, fontFamily: 'monospace' }}>
                  {results.error}
                </Typography>
              </Alert>
            </Box>
          ) : (
            <>
              {/* Tabs */}
              <Box sx={{ flexShrink: 0 }}>
                <Tabs
                  value={activeTab}
                  onChange={handleTabChange}
                  sx={{ borderBottom: 1, borderColor: 'divider', minHeight: 36 }}
                >
                  <Tab label="Data" sx={{ fontSize: 12, minHeight: 36 }} />
                  <Tab label="Messages" sx={{ fontSize: 12, minHeight: 36 }} />
                </Tabs>
              </Box>

              {/* Tab Content */}
              <Box sx={{ flexGrow: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>

              {/* Data Tab */}
              <TabPanel value={activeTab} index={0}>
                {hasData ? (
                  <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <TableContainer sx={{ 
                      flexGrow: 1, 
                      overflow: 'auto', 
                      height: 0,
                      '&::-webkit-scrollbar': {
                        width: '8px',
                        height: '8px',
                      },
                      '&::-webkit-scrollbar-track': {
                        backgroundColor: 'rgba(0,0,0,0.1)',
                        borderRadius: '4px',
                      },
                      '&::-webkit-scrollbar-thumb': {
                        backgroundColor: 'rgba(0,0,0,0.3)',
                        borderRadius: '4px',
                        '&:hover': {
                          backgroundColor: 'rgba(0,0,0,0.5)',
                        },
                      },
                    }}>
                    <Table stickyHeader size="small">
                      <TableHead>
                        <TableRow>
                          {results.columns?.map((column: string, index: number) => (
                            <TableCell
                              key={index}
                              sx={{
                                fontSize: 12,
                                fontWeight: 600,
                                backgroundColor: 'background.default',
                                borderBottom: 1,
                                borderColor: 'divider',
                                textAlign: 'center',
                              }}
                            >
                              {column}
                            </TableCell>
                          ))}
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {paginatedRows.map((row: any[], rowIndex: number) => (
                          <TableRow
                            key={rowIndex}
                            hover
                            sx={{
                              '&:nth-of-type(odd)': {
                                backgroundColor: 'action.hover',
                              },
                            }}
                          >
                            {row.map((cell: any, cellIndex: number) => {
                              const formattedCell = QueryResultsUtils.formatCell(cell);
                              return (
                                <TableCell
                                  key={cellIndex}
                                  sx={{
                                    fontSize: 11,
                                    fontFamily: formattedCell.type === 'number' ? 'monospace' : 'inherit',
                                    maxWidth: 200,
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    whiteSpace: 'nowrap',
                                    textAlign: 'center',
                                    color: formattedCell.isNull ? 'text.secondary' : 'text.primary',
                                    fontStyle: formattedCell.isNull ? 'italic' : 'normal',
                                  }}
                                  title={formattedCell.displayValue} // Show full value on hover
                                >
                                  {formattedCell.displayValue}
                                </TableCell>
                              );
                            })}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    </TableContainer>
                    <TablePagination
                      component="div"
                      count={filteredRows.length}
                      page={page}
                      onPageChange={handleChangePage}
                      rowsPerPage={rowsPerPage}
                      onRowsPerPageChange={handleChangeRowsPerPage}
                      rowsPerPageOptions={[25, 50, 100, 250]}
                      sx={{ borderTop: 1, borderColor: 'divider', flexShrink: 0 }}
                    />
                  </Box>
                ) : (
                  <Box
                    sx={{
                      flexGrow: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexDirection: 'column',
                      gap: 1,
                    }}
                  >
                    <InfoIcon color="action" />
                    <Typography variant="body2" color="text.secondary">
                      No data to display
                    </Typography>
                  </Box>
                )}
              </TabPanel>

              {/* Messages Tab */}
              <TabPanel value={activeTab} index={1}>
                <Box sx={{ p: 2, flexGrow: 1, minHeight: 0, overflow: 'auto' }}>
                  {results.executionMetadata ? (
                    <Typography
                      variant="body2"
                      component="pre"
                      sx={{
                        fontSize: 11,
                        fontFamily: 'monospace',
                        whiteSpace: 'pre-wrap',
                        color: 'text.primary',
                        lineHeight: 1.6,
                      }}
                    >
                      {`[${results.executionMetadata.timestamp}] ${results.executionMetadata.database}> ${results.executionMetadata.originalQuery}`}
                      {"\n"}
                      {`[${results.executionMetadata.timestamp}] ${rowCount > 0 ? `${rowCount} row${rowCount > 1 ? 's' : ''} retrieved` : 'Query executed successfully'} starting from 1 in ${results.executionMetadata.endTime - results.executionMetadata.startTime} ms (execution: ${executionTime || (results.executionMetadata.endTime - results.executionMetadata.startTime)} ms, fetching: ${Math.max(0, (results.executionMetadata.endTime - results.executionMetadata.startTime) - (executionTime || 0))} ms)`}
                    </Typography>
                  ) : results.messages ? (
                    <Typography
                      variant="body2"
                      component="pre"
                      sx={{
                        fontSize: 11,
                        fontFamily: 'monospace',
                        whiteSpace: 'pre-wrap',
                        color: 'text.secondary',
                      }}
                    >
                      {results.messages}
                    </Typography>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Query executed successfully
                      {rowCount > 0 && ` - ${rowCount} rows affected`}
                      {executionTime > 0 && ` (${executionTime}ms)`}
                    </Typography>
                  )}
                </Box>
              </TabPanel>
              </Box>
            </>
          )}
      </Box>
    </Paper>
  );
};

export default ResultsPanel;