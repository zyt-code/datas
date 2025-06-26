import React, { useRef, useEffect } from 'react';
import { Editor } from '@monaco-editor/react';
import { Box } from '@mui/material';

interface SqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
}

const SqlEditor: React.FC<SqlEditorProps> = ({ value, onChange, readOnly = false }) => {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    
    // 配置SQL语言支持
    monaco.languages.registerCompletionItemProvider('sql', {
      provideCompletionItems: (model: any, position: any) => {
        const suggestions = [
          {
            label: 'SELECT',
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: 'SELECT ',
            documentation: 'SELECT statement'
          },
          {
            label: 'FROM',
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: 'FROM ',
            documentation: 'FROM clause'
          },
          {
            label: 'WHERE',
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: 'WHERE ',
            documentation: 'WHERE clause'
          },
          {
            label: 'INSERT',
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: 'INSERT INTO ',
            documentation: 'INSERT statement'
          },
          {
            label: 'UPDATE',
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: 'UPDATE ',
            documentation: 'UPDATE statement'
          },
          {
            label: 'DELETE',
            kind: monaco.languages.CompletionItemKind.Keyword,
            insertText: 'DELETE FROM ',
            documentation: 'DELETE statement'
          },
          {
            label: 'CREATE TABLE',
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: 'CREATE TABLE ${1:table_name} (\n\t${2:column_name} ${3:data_type}\n);',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: 'Create table template'
          }
        ];
        return { suggestions };
      }
    });

    // 设置编辑器快捷键
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      // 触发查询执行
      const executeEvent = new CustomEvent('executeQuery', {
        detail: { query: editor.getValue() }
      });
      window.dispatchEvent(executeEvent);
    });

    // 设置编辑器选项
    editor.updateOptions({
      fontSize: 13,
      fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
      lineHeight: 18,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      automaticLayout: true,
      suggestOnTriggerCharacters: true,
      quickSuggestions: true,
      tabSize: 2,
      insertSpaces: true,
    });
  };

  const handleEditorChange = (value: string | undefined) => {
    onChange(value || '');
  };

  return (
    <Box sx={{ height: '100%', width: '100%' }}>
      <Editor
        height="100%"
        defaultLanguage="sql"
        value={value}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        theme="vs-dark"
        options={{
          readOnly,
          fontSize: 13,
          fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
          lineHeight: 18,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          wordWrap: 'on',
          automaticLayout: true,
          suggestOnTriggerCharacters: true,
          quickSuggestions: true,
          tabSize: 2,
          insertSpaces: true,
          contextmenu: true,
          selectOnLineNumbers: true,
          roundedSelection: false,
          cursorStyle: 'line',
          cursorBlinking: 'blink',
          folding: true,
          foldingHighlight: true,
          showFoldingControls: 'mouseover',
          matchBrackets: 'always',
          renderLineHighlight: 'line',
          renderWhitespace: 'selection',
        }}
      />
    </Box>
  );
};

export default SqlEditor;