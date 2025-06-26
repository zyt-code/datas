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
  id?: string;
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
  const [success, setSuccess] = useState<string>('');
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
    setSuccess('');
  }, [connection, open]);

  const handleInputChange = (field: keyof ConnectionData) => (event: any) => {
    const value = field === 'port' ? parseInt(event.target.value) || 0 : event.target.value;
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
    setSuccess('');
  };

  // MySQL only - no type change needed

  const handleTestConnection = async () => {
    setTesting(true);
    setError('');
    setSuccess('');

    try {
      const result = await window.electronAPI.testConnection(formData);
      if (result.success) {
        setSuccess('连接成功!');
        setError('');
      } else {
        setError(result.error || 'Connection failed');
        setSuccess('');
      }
    } catch (err) {
      setError('Failed to test connection');
      setSuccess('');
    } finally {
      setTesting(false);
    }
  };

  const handleSave = () => {
    if (!formData.host.trim()) {
      setError('Host is required');
      return;
    }

    // Auto-generate connection name if empty
    const finalFormData = { ...formData };
    if (!finalFormData.name.trim()) {
      finalFormData.name = `${finalFormData.username || 'user'}@${finalFormData.host}:${finalFormData.port}`;
    }

    console.log('ConnectionDialog - handleSave called with formData:', finalFormData);
    console.log('ConnectionDialog - original connection prop:', connection);
    onSave(finalFormData);
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
    setSuccess('');
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
          {success && (
            <Alert severity="success" sx={{ fontSize: 12 }}>
              {success}
            </Alert>
          )}

          <TextField
            label="Connection Name"
            value={formData.name}
            onChange={handleInputChange('name')}
            fullWidth
            size="small"
            helperText="Leave empty to auto-generate: username@host:port"
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
          disabled={!formData.host.trim()}
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConnectionDialog;