import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Statistic, Tag, Table, Button, Space, Row, Col, Alert, Spin } from 'antd';
import { ArrowLeftOutlined, DownloadOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { reportApi } from '../api/reports';
import type { TestReport } from '../types';

const ReportDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState<TestReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) loadReport(id);
  }, [id]);

  const loadReport = async (reportId: string) => {
    setLoading(true);
    try {
      const data = await reportApi.get(reportId);
      setReport(data);
    } catch (e) {
      // handled
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: string) => {
    try {
      const data = await reportApi.export(id!, format);
      const blob = new Blob([typeof data === 'string' ? data : JSON.stringify(data)], { type: format === 'markdown' ? 'text/markdown' : 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${id}.${format === 'json' ? 'json' : 'md'}`;
      a.click();
    } catch (e) {
      // handled
    }
  };

  const stepColumns = [
    { title: '步骤', dataIndex: 'name', key: 'name' },
    { title: '方法', dataIndex: 'method', key: 'method' },
    {
      title: '状态', dataIndex: 'passed', key: 'passed',
      render: (p: boolean) => p ? <Tag color="success">通过</Tag> : <Tag color="error">失败</Tag>,
    },
    { title: '状态码', dataIndex: 'status_code', key: 'status_code' },
    { title: '耗时(s)', dataIndex: 'response_time', key: 'response_time', render: (t: number) => t?.toFixed(3) },
    { title: '断言', dataIndex: 'assertions', key: 'assertions', render: (a: any[]) => `${a?.length || 0} 个断言` },
    { title: '错误', dataIndex: 'error', key: 'error', render: (e: string) => e ? <span style={{ color: 'red' }}>{e}</span> : '-' },
  ];

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!report) return <Alert message="报告不存在" type="error" />;

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/reports')}>返回</Button>
        <Space>
          <Button icon={<DownloadOutlined />} onClick={() => handleExport('json')}>导出 JSON</Button>
          <Button icon={<DownloadOutlined />} onClick={() => handleExport('markdown')}>导出 Markdown</Button>
        </Space>
      </div>

      <Alert
        message={report.status === 'PASS' ? '测试通过' : '测试失败'}
        type={report.status === 'PASS' ? 'success' : 'error'}
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={6}><Card><Statistic title="总用例数" value={report.total_tests} /></Card></Col>
        <Col span={6}><Card><Statistic title="通过" value={report.passed_tests} valueStyle={{ color: '#3f8600' }} prefix={<CheckCircleOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="失败" value={report.failed_tests} valueStyle={{ color: '#cf1322' }} prefix={<CloseCircleOutlined />} /></Card></Col>
        <Col span={6}><Card><Statistic title="总耗时" value={report.total_time} suffix="s" precision={3} /></Card></Col>
      </Row>

      <Card title="测试步骤结果">
        <Table columns={stepColumns} dataSource={report.test_results} rowKey={(_, i) => String(i)} pagination={false} size="small" />
      </Card>

      {report.error_messages && (
        <Card title="错误信息" style={{ marginTop: 16 }}>
          <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>{JSON.stringify(report.error_messages, null, 2)}</pre>
        </Card>
      )}
    </div>
  );
};

export default ReportDetail;
