import React, { useState } from 'react';
import {
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  Storage as StorageIcon,
  Circle as CircleIcon,
  PlayArrow as ConnectIcon,
  Stop as DisconnectIcon,
  Tab as ConsoleIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

interface Connection {
  id: string;
  name: string;
  host: string;
  port: number;
  database?: string;
}

interface ConnectionItemProps {
  connection: Connection;
  isSelected: boolean;
  isConnected: boolean;
  onSelect: (connectionId: string) => void;
  onConnect: (connectionId: string) => void;
  onNewConsole: (connectionId: string) => void;
  onEdit: (connectionId: string) => void;
  onDelete: (connectionId: string) => void;
}

const ConnectionItem: React.FC<ConnectionItemProps> = ({
  connection,
  isSelected,
  isConnected,
  onSelect,
  onConnect,
  onNewConsole,
  onEdit,
  onDelete,
}) => {
  const [contextMenu, setContextMenu] = useState<{
    mouseX: number;
    mouseY: number;
  } | null>(null);

  const handleContextMenu = (event: React.MouseEvent) => {
    event.preventDefault();
    setContextMenu(
      contextMenu === null
        ? {
          mouseX: event.clientX + 2,
          mouseY: event.clientY - 6,
        }
        : null,
    );
  };

  const handleClose = () => {
    setContextMenu(null);
  };

  const handleDoubleClick = () => {
    onConnect(connection.id);
  };

  const handleMenuAction = (action: () => void) => {
    action();
    handleClose();
  };

  return (
    <>
      <ListItem disablePadding>
        <ListItemButton
          selected={isSelected}
          onClick={() => onSelect(connection.id)}
          onDoubleClick={handleDoubleClick}
          onContextMenu={handleContextMenu}
          sx={{
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          }}
        >
          <ListItemIcon sx={{ minWidth: 36 }}>
            <CircleIcon
              fontSize="small"
              sx={{
                color: isConnected ? 'success.main' : 'grey.400',
                fontSize: 10,
              }}
            />
          </ListItemIcon>
          <ListItemText
            primary={connection.name}
            secondary={`${connection.host}:${connection.port}`}
            primaryTypographyProps={{
              fontSize: 13,
              color: isConnected ? 'text.primary' : 'grey.500',
            }}
            secondaryTypographyProps={{
              fontSize: 11,
              color: isConnected ? 'text.secondary' : 'grey.400',
            }}
          />
        </ListItemButton>
      </ListItem>

      <Menu
        open={contextMenu !== null}
        onClose={handleClose}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu !== null
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
        slotProps={{
          paper: {
            sx: {
              minWidth: 180,
            },
          },
        }}
      >
        <MenuItem
          onClick={() => handleMenuAction(() => onConnect(connection.id))}
        >
          <ListItemIcon>
            {isConnected ? (
              <DisconnectIcon fontSize="small" />
            ) : (
              <ConnectIcon fontSize="small" />
            )}
          </ListItemIcon>
          <ListItemText>{isConnected ? 'Disconnect' : 'Connect'}</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleMenuAction(() => onNewConsole(connection.id))}>
          <ListItemIcon>
            <ConsoleIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>New SQL Console</ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => handleMenuAction(() => onEdit(connection.id))}>
          <ListItemIcon>
            <EditIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Edit Connection</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleMenuAction(() => onDelete(connection.id))}>
          <ListItemIcon>
            <DeleteIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Delete Connection</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
};

export default ConnectionItem;