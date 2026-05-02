import React, { useState, useEffect } from 'react';
import { Table, Button, Modal, Form, Input, Space, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import { projectApi } from '../api/projects';
import type { Project, ProjectCreate } from '../types';
import { useNavigate } from 'react-router-dom';
import dayjs from 'dayjs';

const ProjectList: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [form] = Form.useForm();

  useEffect(() => { loadProjects(); }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await projectApi.list();
      setProjects(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      if (editingProject) {
        await projectApi.update(editingProject.id, values);
        message.success('项目更新成功');
      } else {
        await projectApi.create(values as ProjectCreate);
        message.success('项目创建成功');
      }
      setModalOpen(false);
      setEditingProject(null);
      form.resetFields();
      loadProjects();
    } catch (e) {
      // handled by interceptor
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await projectApi.delete(id);
      message.success('项目已删除');
      loadProjects();
    } catch (e) {
      // handled
    }
  };

  const handleEdit = (record: Project) => {
    setEditingProject(record);
    form.setFieldsValue(record);
    setModalOpen(true);
  };

  const columns = [
    { title: '项目名称', dataIndex: 'name', key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    { title: 'Base URL', dataIndex: 'base_url', key: 'base_url', ellipsis: true },
    { title: '用例数', dataIndex: 'test_count', key: 'test_count' },
    {
      title: '创建时间', dataIndex: 'created_at', key: 'created_at',
      render: (t: string) => dayjs(t).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作', key: 'action',
      render: (_: any, record: Project) => (
        <Space>
          <Button type="link" icon={<EyeOutlined />} size="small" onClick={() => navigate(`/tests`)}>查看用例</Button>
          <Button type="link" icon={<EditOutlined />} size="small" onClick={() => handleEdit(record)}>编辑</Button>
          <Popconfirm title="确定删除此项目？" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger icon={<DeleteOutlined />} size="small">删除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditingProject(null); form.resetFields(); setModalOpen(true); }}>
          创建项目
        </Button>
      </div>
      <Table columns={columns} dataSource={projects} rowKey="id" loading={loading} />
      <Modal
        title={editingProject ? '编辑项目' : '创建项目'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => { setModalOpen(false); setEditingProject(null); }}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="项目名称" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item name="base_url" label="Base URL">
            <Input placeholder="https://api.example.com" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ProjectList;
