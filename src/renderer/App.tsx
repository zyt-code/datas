import React, { useState, useEffect } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Divider,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Button,
  Tab,
  Tabs,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip,
  Alert,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Storage as StorageIcon,
  AccountTree as SchemaIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Close as CloseIcon,
  Menu as MenuIcon,
  Storage as DatabaseIcon,
} from '@mui/icons-material';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import ConnectionDialog from './components/ConnectionDialog';
import ConnectionItem from './components/ConnectionItem';
import SqlEditor from './components/SqlEditor';
import ResultsPanel from './components/ResultsPanel';

const SIDEBAR_WIDTH = 300;

interface Tab {
  id: string;
  title: string;
  content: string;
  isActive: boolean;
}

interface Connection {
  id: string;
  name: string;
  type: string;
  host: string;
  port: number;
  database?: string;
  username?: string;
  password?: string;
  createdAt: string;
  updatedAt: string;
}

const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [connectedConnections, setConnectedConnections] = useState<Set<string>>(new Set());
  const [activeConnection, setActiveConnection] = useState<string | null>(null);
  const [databases, setDatabases] = useState<string[]>([]);
  const [selectedDatabase, setSelectedDatabase] = useState<string>('');
  const [connectionDialogOpen, setConnectionDialogOpen] = useState(false);
  const [editingConnection, setEditingConnection] = useState<Connection | null>(null);
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [queryResults, setQueryResults] = useState<any>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);
  const [showResultsPanel, setShowResultsPanel] = useState(false);
  const [heartbeatIntervals, setHeartbeatIntervals] = useState<Map<string, NodeJS.Timeout>>(new Map());

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      const result = await window.electronAPI.getConnections();
      setConnections(result.map(conn => ({
        ...conn,
        username: conn.username || '',
        password: conn.password || ''
      })));
    } catch (error) {
      console.error('Failed to load connections:', error);
    }
  };

  const handleNewConnection = () => {
    setEditingConnection(null);
    setConnectionDialogOpen(true);
  };

  const handleConnectionSave = async (connectionData: any) => {
    try {
      await window.electronAPI.saveConnection(connectionData);
      await loadConnections();
      setConnectionDialogOpen(false);
      setEditingConnection(null);
    } catch (error) {
      console.error('Failed to save connection:', error);
    }
  };

  const handleConnectionSelect = (connectionId: string) => {
    setActiveConnection(connectionId);
  };

  const handleConnectionConnect = async (connectionId: string) => {
    try {
      const result = await window.electronAPI.connectToDatabase(connectionId);

      if (result) {
        setConnectedConnections(prev => new Set([...prev, connectionId]));

        // Load databases for this connection
        await loadDatabases(connectionId);

        // Start heartbeat
        startHeartbeat(connectionId);

        // Set as active connection if none is selected
        if (!activeConnection) {
          setActiveConnection(connectionId);
        }
      } else {
        console.error('Failed to connect to database');
      }
    } catch (error) {
      console.error('Connection failed:', error);
    }
  };

  const loadDatabases = async (connectionId: string) => {
    try {
      const result = await window.electronAPI.getDatabases(connectionId);

      if (result && result.success) {
        setDatabases(result.databases || []);
      } else {
        console.error('Failed to load databases:', result?.error);
      }
    } catch (error) {
      console.error('Failed to load databases:', error);
    }
  };

  const startHeartbeat = (connectionId: string) => {
    // Clear existing interval if any
    const existingInterval = heartbeatIntervals.get(connectionId);
    if (existingInterval) {
      clearInterval(existingInterval);
    }

    // Start new heartbeat
    const interval = setInterval(async () => {
      try {
        const result = await window.electronAPI.checkConnection(connectionId);
        if (!result) {
          // Connection lost
          setConnectedConnections(prev => {
            const newSet = new Set(prev);
            newSet.delete(connectionId);
            return newSet;
          });

          // Clear heartbeat
          setHeartbeatIntervals(prev => {
            const newMap = new Map(prev);
            const interval = newMap.get(connectionId);
            if (interval) {
              clearInterval(interval);
              newMap.delete(connectionId);
            }
            return newMap;
          });

          // Reset active connection if this was it
          if (activeConnection === connectionId) {
            setActiveConnection(null);
            setDatabases([]);
            setSelectedDatabase('');
          }
        }
      } catch (error) {
        console.error('Heartbeat failed:', error);
      }
    }, 30000); // Check every 30 seconds

    setHeartbeatIntervals(prev => new Map(prev.set(connectionId, interval)));
  };

  const handleConnectionDisconnect = async (connectionId: string) => {
    try {
      await window.electronAPI.disconnectFromDatabase(connectionId);
      setConnectedConnections(prev => {
        const newSet = new Set(prev);
        newSet.delete(connectionId);
        return newSet;
      });

      // Clear heartbeat
      const interval = heartbeatIntervals.get(connectionId);
      if (interval) {
        clearInterval(interval);
        setHeartbeatIntervals(prev => {
          const newMap = new Map(prev);
          newMap.delete(connectionId);
          return newMap;
        });
      }

      // Reset active connection if this was it
      if (activeConnection === connectionId) {
        setActiveConnection(null);
        setDatabases([]);
        setSelectedDatabase('');
      }
    } catch (error) {
      console.error('Failed to disconnect:', error);
    }
  };

  const handleActiveConnectionChange = async (connectionId: string) => {
    setActiveConnection(connectionId);
    setSelectedDatabase('');

    // Load databases for the selected connection
    if (connectedConnections.has(connectionId)) {
      await loadDatabases(connectionId);
    } else {
      setDatabases([]);
    }
  };

  const handleNewConsole = (connectionId: string) => {
    const newTab: Tab = {
      id: `tab-${Date.now()}`,
      title: 'New Console',
      content: '',
      isActive: true
    };

    setTabs(prev => [...prev.map(tab => ({ ...tab, isActive: false })), newTab]);
    setActiveTab(newTab.id);
    setShowWelcome(false);
  };

  const handleEditConnection = (connectionId: string) => {
    const connection = connections.find(c => c.id === connectionId);
    if (connection) {
      setEditingConnection(connection);
      setConnectionDialogOpen(true);
    }
  };

  const handleDeleteConnection = async (connectionId: string) => {
    try {
      await window.electronAPI.deleteConnection(connectionId);
      await loadConnections();

      // Reset active connection if this was it
      if (activeConnection === connectionId) {
        setActiveConnection(null);
      }
      setConnectedConnections(prev => {
        const newSet = new Set(prev);
        newSet.delete(connectionId);
        return newSet;
      });
    } catch (error) {
      console.error('Failed to delete connection:', error);
    }
  };

  const handleNewTab = () => {
    const newTab: Tab = {
      id: `tab-${Date.now()}`,
      title: 'New Console',
      content: '',
      isActive: true
    };

    setTabs(prev => [...prev.map(tab => ({ ...tab, isActive: false })), newTab]);
    setActiveTab(newTab.id);
    setShowWelcome(false);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    setActiveTab(newValue);
  };

  const handleTabClose = (tabId: string) => {
    const newTabs = tabs.filter(tab => tab.id !== tabId);
    setTabs(newTabs);
    if (activeTab === tabId) {
      if (newTabs.length > 0) {
        setActiveTab(newTabs[newTabs.length - 1].id);
      } else {
        setActiveTab(null);
        setShowWelcome(true);
      }
    }
  };

  const handleQueryExecute = async (query: string) => {
    if (!activeConnection) {
      console.error('No active connection');
      return;
    }

    setIsExecuting(true);
    const startTime = Date.now();
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);

    try {
      let queryToExecute = query;

      // Add USE database statement if a database is selected
      if (selectedDatabase && selectedDatabase.trim()) {
        queryToExecute = `USE \`${selectedDatabase}\`;\n${query}`;
      }

      const result = await window.electronAPI.executeQuery(activeConnection, queryToExecute);

      // Add execution metadata to result
      const enhancedResult = {
        ...result,
        executionMetadata: {
          timestamp,
          database: selectedDatabase || 'No database selected',
          originalQuery: query,
          executedQuery: queryToExecute,
          startTime,
          endTime: Date.now()
        }
      };

      setQueryResults(enhancedResult);
      setShowResultsPanel(true);
    } catch (error) {
      console.error('Query execution failed:', error);
      setQueryResults({
        error: 'Query execution failed',
        message: error,
        executionMetadata: {
          timestamp,
          database: selectedDatabase || 'No database selected',
          originalQuery: query,
          startTime,
          endTime: Date.now()
        }
      });
      setShowResultsPanel(true);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleEditorChange = (value: string) => {
    if (activeTab) {
      setTabs(prev => prev.map(tab =>
        tab.id === activeTab ? { ...tab, content: value } : tab
      ));
    }
  };

  const handleCloseResultsPanel = () => {
    setShowResultsPanel(false);
  };

  const handleRefreshResults = () => {
    if (activeTabData?.content) {
      handleQueryExecute(activeTabData.content);
    }
  };

  const activeTabData = tabs.find(tab => tab.id === activeTab);

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Sidebar */}
      <Drawer
        variant="persistent"
        anchor="left"
        open={sidebarOpen}
        sx={{
          width: sidebarOpen ? SIDEBAR_WIDTH : 0,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: SIDEBAR_WIDTH,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            Connections
          </Typography>
        </Toolbar>
        <Divider />
        <List>
          <ListItem disablePadding>
            <ListItemButton onClick={handleNewConnection}>
              <ListItemIcon>
                <AddIcon />
              </ListItemIcon>
              <ListItemText primary="Add Connection" />
            </ListItemButton>
          </ListItem>
        </List>
        <Divider />
        <List>
          {connections.map((connection) => (
            <ConnectionItem
              key={connection.id}
              connection={connection}
              isSelected={activeConnection === connection.id}
              isConnected={connectedConnections.has(connection.id)}
              onSelect={handleActiveConnectionChange}
              onConnect={handleConnectionConnect}
              onNewConsole={handleNewConsole}
              onEdit={(id) => {
                const conn = connections.find(c => c.id === id);
                if (conn) {
                  setEditingConnection(conn);
                  setConnectionDialogOpen(true);
                }
              }}
              onDelete={handleDeleteConnection}
            />
          ))}
        </List>
      </Drawer>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* App Bar */}
        <AppBar position="static" color="default" elevation={1}>
          <Toolbar variant="dense">
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              DataGrip Lite
            </Typography>
          </Toolbar>
        </AppBar>

        {/* Editor Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', minHeight: 48, display: 'flex', alignItems: 'center' }}>
          {tabs.length > 0 && (
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
            >
              {tabs.map((tab) => (
                <Tab
                  key={tab.id}
                  value={tab.id}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {tab.title}
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleTabClose(tab.id);
                        }}
                        sx={{
                          width: 16,
                          height: 16,
                          '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.1)' }
                        }}
                      >
                        <CloseIcon sx={{ fontSize: 12 }} />
                      </IconButton>
                    </Box>
                  }
                />
              ))}
            </Tabs>
          )}

          <Button
            startIcon={<AddIcon />}
            onClick={handleNewTab}
            size="small"
            sx={{ ml: 'auto', mr: 1 }}
          >
          </Button>
        </Box>

        {/* Main Content Area */}
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          {showWelcome && tabs.length === 0 ? (
            <Box sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              gap: 2
            }}>
              <Typography variant="h4" color="text.secondary">
                Welcome to DataGrip Lite
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Create a new SQL console to get started
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleNewTab}
              >
                New SQL Console
              </Button>
            </Box>
          ) : activeTabData ? (
            <>
              {/* Connection and Database Selection */}
              <Box sx={{
                p: 1,
                borderBottom: 1,
                borderColor: 'divider',
                display: 'flex',
                alignItems: 'center',
                gap: 2
              }}>
                <FormControl size="small" sx={{ minWidth: 200 }}>
                  <InputLabel>Connection</InputLabel>
                  <Select
                    value={activeConnection || ''}
                    onChange={(e) => handleActiveConnectionChange(e.target.value)}
                    label="Connection"
                  >
                    {connections.map((conn) => (
                      <MenuItem key={conn.id} value={conn.id}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip
                            size="small"
                            color={connectedConnections.has(conn.id) ? 'success' : 'default'}
                            sx={{ width: 8, height: 8, '& .MuiChip-label': { display: 'none' } }}
                          />
                          {conn.name}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControl size="small" sx={{ minWidth: 150 }}>
                  <InputLabel>Database</InputLabel>
                  <Select
                    value={selectedDatabase}
                    onChange={(e) => setSelectedDatabase(e.target.value)}
                    label="Database"
                    disabled={!activeConnection || databases.length === 0}
                  >
                    {databases.map((db) => (
                      <MenuItem key={db} value={db}>
                        {db}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <Button
                  variant="contained"
                  startIcon={isExecuting ? <StopIcon /> : <PlayIcon />}
                  onClick={() => {
                    if (isExecuting) {
                      // TODO: Implement query cancellation
                    } else {
                      handleQueryExecute(activeTabData.content);
                    }
                  }}
                  disabled={!activeConnection || isExecuting}
                >
                  {isExecuting ? 'Stop' : 'Execute'}
                </Button>
              </Box>

              {/* Resizable Panels */}
              <Box sx={{
                flexGrow: 1,
                height: 'calc(100vh - 112px)', // 减去AppBar和Tabs的高度
                display: 'flex',
                flexDirection: 'column'
              }}>
                {showResultsPanel && queryResults ? (
                  <PanelGroup direction="vertical" style={{ height: '100%' }}>
                    {/* SQL Editor Panel */}
                    <Panel defaultSize={60} minSize={30}>
                      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                        <SqlEditor
                          value={activeTabData.content}
                          onChange={handleEditorChange}
                        />
                      </Box>
                    </Panel>

                    {/* Resize Handle */}
                    <PanelResizeHandle>
                      <Box sx={{
                        height: '4px',
                        backgroundColor: 'divider',
                        cursor: 'row-resize',
                        '&:hover': {
                          backgroundColor: 'primary.main',
                        },
                        transition: 'background-color 0.2s'
                      }} />
                    </PanelResizeHandle>

                    {/* Results Panel */}
                    <Panel defaultSize={40} minSize={20}>
                      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                        <ResultsPanel
                          results={queryResults}
                          onRefresh={handleRefreshResults}
                          onClose={handleCloseResultsPanel}
                        />
                      </Box>
                    </Panel>
                  </PanelGroup>
                ) : (
                  <Box sx={{ height: '100%' }}>
                    <SqlEditor
                      value={activeTabData.content}
                      onChange={handleEditorChange}
                    />
                  </Box>
                )}
              </Box>
            </>
          ) : null}
        </Box>
      </Box>

      {/* Connection Dialog */}
      <ConnectionDialog
        open={connectionDialogOpen}
        onClose={() => {
          setConnectionDialogOpen(false);
          setEditingConnection(null);
        }}
        onSave={handleConnectionSave}
        connection={editingConnection ? {
          name: editingConnection.name,
          type: editingConnection.type,
          host: editingConnection.host,
          port: editingConnection.port,
          database: editingConnection.database,
          username: editingConnection.username,
          password: editingConnection.password
        } : null}
      />
    </Box>
  );
};

export default App;