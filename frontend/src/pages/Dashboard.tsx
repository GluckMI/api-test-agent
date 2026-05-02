import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Table, Tag } from 'antd';
import {
  FileTextOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import { reportApi } from '../api/reports';
import { projectApi } from '../api/projects';
import { testApi } from '../api/tests';
import { useNavigate } from 'react-router-dom';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalTests: 0,
    totalProjects: 0,
    passRate: 0,
    totalReports: 0,
  });
  const [reports, setReports] = useState<any[]>([]);
  const [trendData, setTrendData] = useState<any[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [projects, tests, reportStats, recentReports] = await Promise.all([
        projectApi.list(),
        testApi.list(),
        reportApi.getStats().catch(() => ({ total_reports: 0, avg_pass_rate: 0, pass_rate_trend: [] })),
        reportApi.list(undefined, 5).catch(() => []),
      ]);
      setStats({
        totalProjects: projects.length,
        totalTests: tests.length,
        passRate: reportStats.avg_pass_rate || 0,
        totalReports: reportStats.total_reports || 0,
      });
      setTrendData(reportStats.pass_rate_trend || []);
      setReports(recentReports);
    } catch (e) {
      console.error(e);
    }
  };

  const chartOption = {
    tooltip: { trigger: 'axis' as const },
    xAxis: {
      type: 'category' as const,
      data: trendData.map((d: any) => dayjs(d.executed_at).format('MM-DD HH:mm')),
    },
    yAxis: { type: 'value' as const, min: 0, max: 100, axisLabel: { formatter: '{value}%' } },
    series: [{
      name: '通过率',
      type: 'line' as const,
      data: trendData.map((d: any) => d.pass_rate),
      smooth: true,
      areaStyle: { opacity: 0.3 },
      itemStyle: { color: '#1890ff' },
    }],
    grid: { left: 50, right: 20, top: 30, bottom: 30 },
  };

  const columns = [
    { title: '测试名称', dataIndex: 'test_name', key: 'test_name' },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'PASS' ? 'success' : 'error'}>{status}</Tag>
      ),
    },
    {
      title: '通过率',
      dataIndex: 'pass_rate',
      key: 'pass_rate',
      render: (rate: number) => `${rate.toFixed(1)}%`,
    },
    {
      title: '耗时',
      dataIndex: 'total_time',
      key: 'total_time',
      render: (t: number) => `${t.toFixed(2)}s`,
    },
    {
      title: '执行时间',
      dataIndex: 'executed_at',
      key: 'executed_at',
      render: (t: string) => dayjs(t).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: any) => (
        <a onClick={() => navigate(`/reports/${record.id}`)}>查看详情</a>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="项目数量" value={stats.totalProjects} prefix={<FileTextOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="测试用例" value={stats.totalTests} prefix={<FileTextOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="平均通过率" value={stats.passRate} suffix="%" precision={1}
              valueStyle={{ color: stats.passRate >= 80 ? '#3f8600' : stats.passRate >= 50 ? '#faad14' : '#cf1322' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="执行次数" value={stats.totalReports} prefix={<RocketOutlined />} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={16}>
          <Card title="通过率趋势">
            {trendData.length > 0 ? (
              <ReactECharts option={chartOption} style={{ height: 300 }} />
            ) : (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>暂无数据</div>
            )}
          </Card>
        </Col>
        <Col span={8}>
          <Card title="最近执行">
            <div style={{ maxHeight: 300, overflow: 'auto' }}>
              {reports.map((r) => (
                <div key={r.id} style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0', cursor: 'pointer' }}
                  onClick={() => navigate(`/reports/${r.id}`)}>
                  <div style={{ fontWeight: 500 }}>{r.test_name}</div>
                  <Tag color={r.status === 'PASS' ? 'success' : 'error'}>{r.status}</Tag>
                  <span style={{ marginLeft: 8, color: '#999', fontSize: 12 }}>
                    {dayjs(r.executed_at).format('MM-DD HH:mm')}
                  </span>
                </div>
              ))}
              {reports.length === 0 && <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>暂无数据</div>}
            </div>
          </Card>
        </Col>
      </Row>

      <Card title="执行历史" style={{ marginTop: 16 }}>
        <Table
          columns={columns}
          dataSource={reports}
          rowKey="id"
          size="small"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

export default Dashboard;
