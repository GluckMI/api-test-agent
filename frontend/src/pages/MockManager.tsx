import React from 'react';
import {
  Card,
  Alert,
  Timeline,
  Tag,
  List,
  Row,
  Col,
  Typography,
  Badge,
  Empty,
} from 'antd';

const { Text } = Typography;

interface PlannedFeature {
  name: string;
  description: string;
  status: '开发中' | '规划中';
}

const plannedFeatures: PlannedFeature[] = [
  { name: 'API 响应模拟', description: '自定义模拟 API 响应数据，支持多种格式', status: '开发中' },
  { name: '延迟模拟', description: '模拟网络延迟，测试超时处理逻辑', status: '规划中' },
  { name: '请求匹配规则', description: '灵活的请求匹配策略，支持路径、参数、请求体匹配', status: '规划中' },
  { name: 'Mock 服务管理', description: '创建、启动、停止和管理多个 Mock 服务实例', status: '规划中' },
];

const developmentTimeline = [
  { content: '基础 Mock 响应功能', estimatedTime: 'Q2 2026' },
  { content: '请求匹配规则引擎', estimatedTime: 'Q2 2026' },
  { content: '延迟模拟与动态响应', estimatedTime: 'Q3 2026' },
  { content: '多服务管理与配置导入', estimatedTime: 'Q3 2026' },
];

const MockManager: React.FC = () => {
  return (
    <div>
      <Alert
        message={
          <span>
            <Badge status="processing" />
            <Text strong style={{ marginLeft: 8 }}>开发中</Text>
          </span>
        }
        description="Mock 服务模块正在积极开发中，预计 Q2-Q3 2026 陆续发布核心功能。"
        type="info"
        showIcon={false}
        style={{ marginBottom: 24 }}
      />

      <Row gutter={[16, 16]}>
        <Col span={16}>
          <Card title="功能预览" bordered={false}>
            <List
              itemLayout="horizontal"
              dataSource={plannedFeatures}
              renderItem={(feature) => (
                <List.Item>
                  <List.Item.Meta
                    title={
                      <span>
                        {feature.name}
                        <Tag
                          color={feature.status === '开发中' ? 'blue' : 'default'}
                          style={{ marginLeft: 8 }}
                        >
                          {feature.status}
                        </Tag>
                      </span>
                    }
                    description={feature.description}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        <Col span={8}>
          <Card title="开发进度" bordered={false}>
            <Timeline
              items={developmentTimeline.map((item) => ({
                color: 'blue',
                children: (
                  <div>
                    <div>{item.content}</div>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {item.estimatedTime}
                    </Text>
                  </div>
                ),
              }))}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 16 }} bordered={false}>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <div>
              <Text type="secondary">
                当前暂无可用的 Mock 服务，请等待功能上线后使用。
              </Text>
            </div>
          }
        />
      </Card>
    </div>
  );
};

export default MockManager;
