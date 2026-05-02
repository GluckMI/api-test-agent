import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import ProjectList from './pages/ProjectList';
import TestCaseList from './pages/TestCaseList';
import TestCaseEditor from './pages/TestCaseEditor';
import ExecutionConsole from './pages/ExecutionConsole';
import ReportList from './pages/ReportList';
import ReportDetail from './pages/ReportDetail';
import EnvironmentManager from './pages/EnvironmentManager';
import MockManager from './pages/MockManager';

const AppRoutes: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="projects" element={<ProjectList />} />
          <Route path="tests" element={<TestCaseList />} />
          <Route path="tests/:id" element={<TestCaseEditor />} />
          <Route path="tests/new" element={<TestCaseEditor />} />
          <Route path="execution/:id" element={<ExecutionConsole />} />
          <Route path="reports" element={<ReportList />} />
          <Route path="reports/:id" element={<ReportDetail />} />
          <Route path="environments" element={<EnvironmentManager />} />
          <Route path="mock" element={<MockManager />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default AppRoutes;
