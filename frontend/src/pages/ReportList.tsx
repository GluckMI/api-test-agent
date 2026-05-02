import React, { useState, useEffect } from 'react';
import { Table, Button, Tag, Space, Popconfirm, message } from 'antd';
import { EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import { reportApi } from '../api/reports';
import type { ReportSummary } from '../types';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';

const ReportList: React.FC = () => {
  const navigate = useNavigate();
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { loadReports(); }, []);

  const loadReports = async () => {
    setLoading(true);
    try {
      const data = await reportApi.list();
      setReports(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await reportApi.delete(id);
      message.success('报告已删除');
      loadReports();
    } catch (e) { /* */ }
  };

  const columns = [
    { title: '测试名称', dataIndex: 'test_name', key: 'test_name' },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (s: string) => <Tag color={s === 'PASS' ? 'success' : 'error'}>{s}</Tag>,
    },
    {
      title: '通过率', dataIndex: 'pass_rate', key: 'pass_rate',
      render: (r: number) => `${r.toFixed(1)}%`,
    },
    { title: '用例数', dataIndex: 'total_tests', key: 'total_tests',
      render: (_: number, r: ReportSummary) => `总:${r.total_tests} 通过:${r.passed_tests} 失败:${r.failed_tests}`,
    },
    { title: '耗时', dataIndex: 'total_time', key: 'total_time', render: (t: number) => `${t.toFixed(2)}s` },
    { title: '执行时间', dataIndex: 'executed_at', key: 'executed_at', render: (t: string) => dayjs(t).format('YYYY-MM-DD HH:mm:ss') },
    {
      title: '操作', key: 'action',
      render: (_: any, record: ReportSummary) => (
        <Space>
          <Button type="link" icon={<EyeOutlined />} size="small" onClick={() => navigate(`/reports/${record.id}`)}>详情</Button>
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />} size="small">删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Table columns={columns} dataSource={reports} rowKey="id" loading={loading} />
    </div>
  );
};

export default ReportList;
