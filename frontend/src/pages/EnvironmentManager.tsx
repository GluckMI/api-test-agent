import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Space, message, Popconfirm, Tag, Switch } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { environmentApi } from '../api/environments';
import type { Environment } from '../types';
import dayjs from 'dayjs';

const EnvironmentManager: React.FC = () => {
  const [envs, setEnvs] = useState<Environment[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingEnv, setEditingEnv] = useState<Environment | null>(null);
  const [form] = Form.useForm();

  useEffect(() => { loadEnvs(); }, []);

  const loadEnvs = async () => {
    setLoading(true);
    try {
      const data = await environmentApi.list();
      setEnvs(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingEnv) {
        await environmentApi.update(editingEnv.id, values);
        message.success('环境更新成功');
      } else {
        await environmentApi.create(values);
        message.success('环境创建成功');
      }
      setModalOpen(false);
      setEditingEnv(null);
      form.resetFields();
      loadEnvs();
    } catch (e) { /* */ }
  };

  const handleDelete = async (id: string) => {
    try {
      await environmentApi.delete(id);
      message.success('环境已删除');
      loadEnvs();
    } catch (e) { /* */ }
  };

  const handleEdit = (record: Environment) => {
    setEditingEnv(record);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const columns = [
    { title: '环境名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description' },
    { title: 'Base URL', dataIndex: 'base_url', key: 'base_url', ellipsis: true },
    {
      title: '默认', dataIndex: 'is_default', key: 'is_default',
      render: (v: boolean) => v ? <Tag color="success">是</Tag> : <Tag>否</Tag>,
    },
    {
      title: '更新时间', dataIndex: 'updated_at', key: 'updated_at',
      render: (t: string) => dayjs(t).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作', key: 'action',
      render: (_: any, record: Environment) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} size="small" onClick={() => handleEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />} size="small">删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingEnv(null); form.resetFields(); setModalOpen(true); }}>
          创建环境
        </Button>
      </div>
      <Table columns={columns} dataSource={envs} rowKey="id" loading={loading} />
      <Modal
        title={editingEnv ? '编辑环境' : '创建环境'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => { setModalOpen(false); setEditingEnv(null); }}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="环境名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={2} />
          </Form.Item>
          <Form.Item name="base_url" label="Base URL" rules={[{ required: true }]}>
            <Input placeholder="https://api.example.com" />
          </Form.Item>
          <Form.Item name="is_default" label="设为默认" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default EnvironmentManager;
