import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Progress, Tag, Space, Button, List, Typography, Alert } from 'antd';
import { ArrowLeftOutlined, StopOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { executionApi } from '../api/execution';
import type { WebSocketMessage, ExecutionRecord } from '../types';

const { Text } = Typography;

const MAX_LOG_ENTRIES = 1000;

const LogEntry = React.memo<{ log: string; index: number }>(({ log, index }) => (
  <Text
    key={index}
    style={{
      color: log.includes('ERROR') ? '#ff4d4f' : log.includes('WARN') ? '#faad14' : '#d4d4d4',
      display: 'block',
      fontSize: 12,
      fontFamily: 'monospace',
    }}
  >
    {log}
  </Text>
));

const ExecutionConsole: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [execution, setExecution] = useState<Partial<ExecutionRecord> | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [status, setStatus] = useState('running');
  const wsRef = useRef<WebSocket | null>(null);
  const stopRef = useRef<(() => Promise<void>) | null>(null);

  const handleStop = useCallback(async () => {
    try {
      await executionApi.stop(id!);
      setStatus('stopped');
    } catch (e) {
      // handled
    }
  }, [id]);

  stopRef.current = handleStop;

  useEffect(() => {
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = API_BASE_URL ? new URL(API_BASE_URL).host : window.location.host;
    const wsUrl = `${wsProtocol}//${wsHost}/ws/execution/${id}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const msg: WebSocketMessage = JSON.parse(event.data);
      switch (msg.type) {
        case 'progress':
          setExecution(prev => ({
            ...prev,
            progress: msg.progress,
            current_step: msg.current_step,
            total_steps: msg.total_steps,
          }));
          break;
        case 'result':
          setExecution(prev => ({ ...prev, result: msg.result, status: msg.result?.passed ? 'passed' : 'failed' }));
          setStatus(msg.result?.passed ? 'passed' : 'failed');
          break;
        case 'log':
          setLogs(prev => {
            const newLogs = [...prev, `[${msg.level?.toUpperCase()}] ${msg.message}`];
            return newLogs.length > MAX_LOG_ENTRIES ? newLogs.slice(newLogs.length - MAX_LOG_ENTRIES) : newLogs;
          });
          break;
        case 'status':
          setStatus(msg.status || 'completed');
          break;
      }
    };

    ws.onerror = () => {
      setLogs(prev => [...prev, '[ERROR] WebSocket 连接错误']);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };

    return () => {
      wsRef.current?.close();
    };
  }, [id]);

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/tests')}>返回</Button>
      </div>

      <Card title="执行控制台" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Tag color={status === 'passed' ? 'success' : status === 'failed' ? 'error' : status === 'stopped' ? 'warning' : 'processing'}>
              {status === 'passed' ? '通过' : status === 'failed' ? '失败' : status === 'stopped' ? '已停止' : '执行中'}
            </Tag>
            <span style={{ marginLeft: 16 }}>
              步骤: {execution?.current_step || 0} / {execution?.total_steps || 0}
            </span>
          </div>

          <Progress
            percent={Math.round(execution?.progress || 0)}
            status={status === 'passed' ? 'success' : status === 'failed' ? 'exception' : 'active'}
          />

          {status === 'running' && (
            <Button danger icon={<StopOutlined />} onClick={handleStop}>停止执行</Button>
          )}

          {execution?.result && (
            <Alert
              message={execution.result.passed ? '测试通过' : '测试失败'}
              description={
                <Space direction="vertical">
                  <span>总步骤: {execution.result.total_steps} | 通过: {execution.result.passed_steps} | 失败: {execution.result.failed_steps}</span>
                  <span>总耗时: {execution.result.total_time?.toFixed(3)}s</span>
                  {execution.result.error_message && <span style={{ color: 'red' }}>错误: {execution.result.error_message}</span>}
                </Space>
              }
              type={execution.result.passed ? 'success' : 'error'}
              showIcon
            />
          )}
        </Space>
      </Card>

      <Card title="执行日志">
        <div style={{ height: 400, overflow: 'auto', background: '#1e1e1e', padding: 12, borderRadius: 4 }}>
          {logs.map((log, i) => (
            <LogEntry key={i} log={log} index={i} />
          ))}
          {logs.length === 0 && <div style={{ color: '#666', textAlign: 'center', padding: 40 }}>等待日志输出...</div>}
        </div>
      </Card>

      {execution?.result?.step_results && (
        <Card title="步骤详情" style={{ marginTop: 16 }}>
          <List
            dataSource={execution.result.step_results}
            renderItem={(step: any) => (
              <List.Item>
                <Space>
                  {step.passed ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : <CloseCircleOutlined style={{ color: '#ff4d4f' }} />}
                  <Text strong>{step.name}</Text>
                  <Tag color={step.passed ? 'success' : 'error'}>{step.status_code}</Tag>
                  <Text type="secondary">{step.response_time?.toFixed(3)}s</Text>
                  {step.error && <Text type="danger">{step.error}</Text>}
                </Space>
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  );
};

export default ExecutionConsole;
