import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Alert,
} from '@mui/material';

interface ConnectionDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (connectionData: ConnectionData) => void;
  connection?: ConnectionData | null;
}

interface ConnectionData {
  name: string;
  type: string;
  host: string;
  port: number;
  database?: string;
  username?: string;
  password?: string;
}

const ConnectionDialog: React.FC<ConnectionDialogProps> = ({ open, onClose, onSave, connection }) => {
  const [formData, setFormData] = useState<ConnectionData>({
    name: '',
    type: 'mysql',
    host: 'localhost',
    port: 3306,
    database: '',
    username: '',
    password: '',
  });
  const [error, setError] = useState<string>('');
  const [testing, setTesting] = useState(false);

  // Initialize form data when editing a connection
  useEffect(() => {
    if (connection) {
      setFormData(connection);
    } else {
      setFormData({
        name: '',
        type: 'mysql',
        host: 'localhost',
        port: 3306,
        database: '',
        username: '',
        password: '',
      });
    }
    setError('');
  }, [connection, open]);

  const handleInputChange = (field: keyof ConnectionData) => (event: any) => {
    const value = field === 'port' ? parseInt(event.target.value) || 0 : event.target.value;
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  // MySQL only - no type change needed

  const handleTestConnection = async () => {
    setTesting(true);
    setError('');

    try {
      const result = await window.electronAPI.testConnection(formData);
      if (result.success) {
        setError('');
        alert('Connection successful!');
      } else {
        setError(result.error || 'Connection failed');
      }
    } catch (err) {
      setError('Failed to test connection');
    } finally {
      setTesting(false);
    }
  };

  const handleSave = () => {
    if (!formData.name.trim()) {
      setError('Connection name is required');
      return;
    }
    if (!formData.host.trim()) {
      setError('Host is required');
      return;
    }

    onSave(formData);
    handleClose();
  };

  const handleClose = () => {
    setFormData({
      name: '',
      type: 'mysql',
      host: 'localhost',
      port: 3306,
      database: '',
      username: '',
      password: '',
    });
    setError('');
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          backgroundColor: 'background.paper',
          backgroundImage: 'none',
        }
      }}
    >
      <DialogTitle>
        <Typography variant="h6" sx={{ fontSize: 16, fontWeight: 600 }}>
          {connection ? 'Edit Database Connection' : 'New Database Connection'}
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
          {error && (
            <Alert severity="error" sx={{ fontSize: 12 }}>
              {error}
            </Alert>
          )}

          <TextField
            label="Connection Name"
            value={formData.name}
            onChange={handleInputChange('name')}
            fullWidth
            size="small"
            required
          />

          {/* Fixed to MySQL only */}
          <TextField
            label="Database Type"
            value="MySQL"
            fullWidth
            size="small"
            disabled
            sx={{ '& .MuiInputBase-input': { color: 'text.secondary' } }}
          />

          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              label="Host"
              value={formData.host}
              onChange={handleInputChange('host')}
              fullWidth
              size="small"
              required
            />
            <TextField
              label="Port"
              type="number"
              value={formData.port}
              onChange={handleInputChange('port')}
              size="small"
              sx={{ minWidth: 100 }}
            />
          </Box>

          <TextField
            label="Database"
            value={formData.database}
            onChange={handleInputChange('database')}
            fullWidth
            size="small"
            helperText="Leave empty for default database"
          />

          <TextField
            label="Username"
            value={formData.username}
            onChange={handleInputChange('username')}
            fullWidth
            size="small"
          />

          <TextField
            label="Password"
            type="password"
            value={formData.password}
            onChange={handleInputChange('password')}
            fullWidth
            size="small"
          />
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button
          onClick={handleTestConnection}
          disabled={testing || !formData.host.trim()}
          variant="outlined"
          size="small"
        >
          {testing ? 'Testing...' : 'Test Connection'}
        </Button>
        <Button onClick={handleClose} size="small">
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          size="small"
          disabled={!formData.name.trim() || !formData.host.trim()}
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConnectionDialog;