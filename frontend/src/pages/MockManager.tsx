import React from 'react';
import { Card, Empty, Typography } from 'antd';

const { Title, Paragraph } = Typography;

const MockManager: React.FC = () => {
  return (
    <Card>
      <Empty
        description={
          <span>
            <Title level={4}>Mock 服务</Title>
            <Paragraph type="secondary">
              Mock 服务功能正在开发中，敬请期待。
            </Paragraph>
            <Paragraph type="secondary">
              将支持 Mock 规则配置、录制回放等功能。
            </Paragraph>
          </span>
        }
      />
    </Card>
  );
};

export default MockManager;
