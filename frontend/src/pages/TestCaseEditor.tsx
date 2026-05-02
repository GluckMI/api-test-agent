import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Space, Select, message, Tabs, Row, Col, Table } from 'antd';
import { SaveOutlined, ArrowLeftOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { testApi } from '../api/tests';
import { executionApi } from '../api/execution';
import type { TestCaseCreate, TestStepConfig } from '../types';
import { projectApi } from '../api/projects';
import yaml from 'js-yaml';

const { TextArea } = Input;

const TestCaseEditor: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isNew = !id || id === 'new';
  const [form] = Form.useForm();
  const [steps, setSteps] = useState<TestStepConfig[]>([{ name: '', method: 'GET', endpoint: '', params: {}, headers: {}, assertions: [], extract: {} }]);
  const [yamlContent, setYamlContent] = useState('');
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [formValues, setFormValues] = useState<{ name?: string; description?: string; project_id?: string }>({});

  useEffect(() => {
    loadProjects();
    if (!isNew && id) {
      loadTest(id);
    }
  }, [id, isNew]);

  useEffect(() => {
    try {
      const data: Record<string, any> = { name: formValues.name || '', description: formValues.description || '', steps: steps };
      const generated = yaml.dump(data, { indent: 2, lineWidth: -1, noRefs: true, sortKeys: false });
      setYamlContent(generated.trim());
    } catch (e) {
      setYamlContent('# YAML 生成错误');
    }
  }, [steps, formValues]);

  const loadProjects = async () => {
    try { setProjects(await projectApi.list()); } catch (e) { /* */ }
  };

  const loadTest = async (testId: string) => {
    setLoading(true);
    try {
      const data = await testApi.get(testId);
      form.setFieldsValue({ name: data.name, description: data.description, project_id: data.project_id });
      setFormValues({ name: data.name, description: data.description, project_id: data.project_id });
      setSteps(data.steps || []);
    } catch (e) {
      message.error('加载失败');
    } finally {
      setLoading(false);
    }
  };

  const handleStepChange = (index: number, field: string, value: any) => {
    const newSteps = [...steps];
    newSteps[index] = { ...newSteps[index], [field]: value };
    setSteps(newSteps);
  };

  const addStep = () => {
    setSteps([...steps, { name: '', method: 'GET', endpoint: '', params: {}, headers: {}, assertions: [], extract: {} }]);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      const data: TestCaseCreate = { ...values, steps };
      if (isNew) {
        const result = await testApi.create(data);
        message.success('测试用例创建成功');
        navigate(`/tests/${result.id}`);
      } else {
        await testApi.update(id!, data);
        message.success('测试用例更新成功');
      }
    } catch (e) {
      // handled
    }
  };

  const handleRun = async () => {
    if (isNew) {
      message.warning('请先保存测试用例');
      return;
    }
    try {
      const result = await executionApi.run(id!);
      message.success('测试执行已启动');
      navigate(`/execution/${result.execution_id}`);
    } catch (e) { /* */ }
  };

  const stepColumns = [
    { title: '名称', dataIndex: 'name', key: 'name', render: (v: string, _: any, i: number) => <Input value={v} onChange={e => handleStepChange(i, 'name', e.target.value)} placeholder="步骤名称" /> },
    { title: '方法', dataIndex: 'method', key: 'method', render: (v: string, _: any, i: number) => <Select value={v} onChange={val => handleStepChange(i, 'method', val)} style={{ width: 100 }} options={[{ value: 'GET' }, { value: 'POST' }, { value: 'PUT' }, { value: 'DELETE' }, { value: 'PATCH' }]} /> },
    { title: '端点', dataIndex: 'endpoint', key: 'endpoint', render: (v: string, _: any, i: number) => <Input value={v} onChange={e => handleStepChange(i, 'endpoint', e.target.value)} placeholder="/api/path" /> },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/tests')}>返回</Button>
          <span style={{ fontSize: 16, fontWeight: 500 }}>{isNew ? '创建测试用例' : '编辑测试用例'}</span>
        </Space>
        <Space>
          {!isNew && <Button type="primary" icon={<PlayCircleOutlined />} onClick={handleRun}>运行</Button>}
          <Button type="primary" icon={<SaveOutlined />} onClick={handleSave} loading={loading}>保存</Button>
        </Space>
      </div>

      <Tabs
        defaultActiveKey="form"
        items={[
          {
            key: 'form',
            label: '表单编辑',
            children: (
              <Row gutter={16}>
                <Col span={16}>
                  <Form form={form} layout="vertical" onValuesChange={(_, values) => setFormValues(values)}>
                    <Form.Item name="name" label="用例名称" rules={[{ required: true }]}>
                      <Input />
                    </Form.Item>
                    <Form.Item name="description" label="描述">
                      <TextArea rows={2} />
                    </Form.Item>
                    <Form.Item name="project_id" label="所属项目">
                      <Select placeholder="选择项目" allowClear options={projects.map(p => ({ label: p.name, value: p.id }))} />
                    </Form.Item>
                  </Form>
                  <Card title="测试步骤" extra={<Button type="primary" size="small" onClick={addStep}>添加步骤</Button>}>
                    <Table dataSource={steps} columns={stepColumns} rowKey={(_, i) => String(i)} pagination={false} size="small" />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card title="提示" size="small">
                    <ul style={{ paddingLeft: 20, color: '#666', fontSize: 13 }}>
                      <li>方法支持 GET, POST, PUT, DELETE, PATCH</li>
                      <li>端点填写相对路径，如 /api/users</li>
                      <li>变量使用 $&#123;var&#125; 格式引用</li>
                    </ul>
                  </Card>
                </Col>
              </Row>
            ),
          },
          {
            key: 'yaml',
            label: 'YAML 预览',
            children: (
              <div style={{
                height: 600,
                backgroundColor: '#1e1e1e',
                borderRadius: 6,
                padding: 16,
                overflow: 'auto',
                fontFamily: "'Cascadia Code', 'Fira Code', Consolas, Monaco, monospace",
                fontSize: 13,
                lineHeight: 1.6,
                color: '#d4d4d4',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
              }}>
                {yamlContent || '# 在左侧表单中填写信息，YAML 将在此预览'}
              </div>
            ),
          },
        ]}
      />
    </div>
  );
};

export default TestCaseEditor;