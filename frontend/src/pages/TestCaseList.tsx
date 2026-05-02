import React, { useState, useEffect } from 'react';
import { Table, Button, Tag, Space, Popconfirm, message } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { testApi } from '../api/tests';
import { executionApi } from '../api/execution';
import type { TestCase } from '../types';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';

const TestCaseList: React.FC = () => {
  const navigate = useNavigate();
  const [tests, setTests] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { loadTests(); }, []);

  const loadTests = async () => {
    setLoading(true);
    try {
      const data = await testApi.list();
      setTests(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleRun = async (testId: string) => {
    try {
      const result = await executionApi.run(testId);
      message.success('测试执行已启动');
      navigate(`/execution/${result.execution_id}`);
    } catch (e) {
      // handled
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await testApi.delete(id);
      message.success('测试用例已删除');
      loadTests();
    } catch (e) {
      // handled
    }
  };

  const columns = [
    { title: '用例名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    {
      title: '步骤数', dataIndex: 'steps', key: 'steps',
      render: (steps: any[]) => steps?.length || 0,
    },
    {
      title: '最近结果', dataIndex: 'last_result', key: 'last_result',
      render: (result: any) => result ? (
        <Tag color={result.passed ? 'success' : 'error'}>
          {result.passed ? '通过' : '失败'}
        </Tag>
      ) : <Tag color="default">未执行</Tag>,
    },
    {
      title: '更新时间', dataIndex: 'updated_at', key: 'updated_at',
      render: (t: string) => dayjs(t).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作', key: 'action',
      render: (_: any, record: TestCase) => (
        <Space>
          <Button type="link" icon={<PlayCircleOutlined />} size="small" onClick={() => handleRun(record.id)}>运行</Button>
          <Button type="link" icon={<EditOutlined />} size="small" onClick={() => navigate(`/tests/${record.id}`)}>编辑</Button>
          <Popconfirm title="确定删除此用例？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />} size="small">删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/tests/new')}>
          创建测试用例
        </Button>
      </div>
      <Table columns={columns} dataSource={tests} rowKey="id" loading={loading} />
    </div>
  );
};

export default TestCaseList;
