import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, theme } from 'antd';
import {
  DashboardOutlined,
  FolderOpenOutlined,
  FileTextOutlined,
  BarChartOutlined,
  CloudServerOutlined,
  CodeOutlined,
} from '@ant-design/icons';

const { Sider, Content, Header } = Layout;

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '仪表盘' },
  { key: '/projects', icon: <FolderOpenOutlined />, label: '项目管理' },
  { key: '/tests', icon: <FileTextOutlined />, label: '测试用例' },
  { key: '/reports', icon: <BarChartOutlined />, label: '测试报告' },
  { key: '/environments', icon: <CloudServerOutlined />, label: '环境管理' },
  { key: '/mock', icon: <CodeOutlined />, label: 'Mock 服务' },
];

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} theme="dark">
        <div style={{
          height: 32,
          margin: '16px 8px',
          background: 'rgba(255,255,255,0.2)',
          borderRadius: 6,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontWeight: 'bold',
          fontSize: collapsed ? 14 : 16,
          cursor: 'pointer',
        }} onClick={() => navigate('/')}>
          {collapsed ? 'ATA' : 'API Test Agent'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 24px', background: colorBgContainer, display: 'flex', alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: 18 }}>
            {menuItems.find(i => i.key === location.pathname)?.label || 'API Test Agent'}
          </h2>
        </Header>
        <Content style={{ margin: '16px', padding: 24, background: colorBgContainer, borderRadius: borderRadiusLG, overflow: 'auto' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
