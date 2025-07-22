import { useTranslate } from '@/hooks/common-hooks';
import {
  DeleteOutlined,
  DownloadOutlined,
  FileOutlined,
  InboxOutlined,
  ReloadOutlined,
  SearchOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import {
  Button,
  Card,
  Input,
  Modal,
  Pagination,
  Popconfirm,
  Progress,
  Space,
  Table,
  Tag,
  Upload,
  message,
} from 'antd';
import type { UploadFile } from 'antd/es/upload/interface';
import React, { useEffect, useState } from 'react';
import styles from './index.less';

const { Dragger } = Upload;

interface FileData {
  id: string;
  name: string;
  size: number;
  type: string;
  kb_id?: string;
  location?: string;
  create_time?: string;
  status?: 'uploading' | 'success' | 'error';
  percent?: number;
}

const FileManagementPage = () => {
  const { t } = useTranslate('setting');
  const [loading, setLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [fileData, setFileData] = useState<FileData[]>([]);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [uploadFileList, setUploadFileList] = useState<UploadFile[]>([]);
  const [searchValue, setSearchValue] = useState('');

  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });

  // 模拟文件数据
  const mockFiles: FileData[] = [
    {
      id: '1',
      name: 'document.pdf',
      size: 2048576,
      type: 'application/pdf',
      create_time: '2024-01-01 10:00:00',
      status: 'success',
    },
    {
      id: '2',
      name: 'presentation.pptx',
      size: 5242880,
      type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      create_time: '2024-01-02 10:00:00',
      status: 'success',
    },
    {
      id: '3',
      name: 'spreadsheet.xlsx',
      size: 1024000,
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      create_time: '2024-01-03 10:00:00',
      status: 'success',
    },
    {
      id: '4',
      name: 'image.jpg',
      size: 512000,
      type: 'image/jpeg',
      create_time: '2024-01-04 10:00:00',
      status: 'success',
    },
    {
      id: '5',
      name: 'textfile.txt',
      size: 10240,
      type: 'text/plain',
      create_time: '2024-01-05 10:00:00',
      status: 'success',
    },
  ];

  useEffect(() => {
    loadFileData();
  }, [pagination.current, pagination.pageSize, searchValue]);

  const loadFileData = async () => {
    setLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));

      let filteredFiles = mockFiles;
      if (searchValue) {
        filteredFiles = mockFiles.filter((file) =>
          file.name.toLowerCase().includes(searchValue.toLowerCase()),
        );
      }

      setFileData(filteredFiles);
      setPagination((prev) => ({ ...prev, total: filteredFiles.length }));
    } catch (error) {
      message.error('加载文件列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPagination((prev) => ({ ...prev, current: 1 }));
    loadFileData();
  };

  const handleReset = () => {
    setSearchValue('');
    setPagination((prev) => ({ ...prev, current: 1 }));
    loadFileData();
  };

  const handleUpload = () => {
    setUploadFileList([]);
    setUploadModalVisible(true);
  };

  const handleUploadSubmit = async () => {
    if (uploadFileList.length === 0) {
      message.warning('请选择要上传的文件');
      return;
    }

    setUploadLoading(true);
    try {
      // 模拟上传过程
      for (let i = 0; i < uploadFileList.length; i++) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }

      message.success(`成功上传 ${uploadFileList.length} 个文件`);
      setUploadModalVisible(false);
      loadFileData();
    } catch (error) {
      message.error('文件上传失败');
    } finally {
      setUploadLoading(false);
    }
  };

  const handleDownload = async (file: FileData) => {
    try {
      // 模拟下载
      message.loading({ content: '正在准备下载...', key: 'download' });
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // 创建模拟下载
      const url = URL.createObjectURL(
        new Blob(['Mock file content'], { type: file.type }),
      );
      const link = document.createElement('a');
      link.href = url;
      link.download = file.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      message.success({
        content: `文件 "${file.name}" 下载成功`,
        key: 'download',
      });
    } catch (error) {
      message.error({ content: '文件下载失败', key: 'download' });
    }
  };

  const handleDeleteFile = async (fileId: string) => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setFileData(fileData.filter((file) => file.id !== fileId));
      message.success('删除成功');
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的文件');
      return;
    }

    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      setFileData(
        fileData.filter((file) => !selectedRowKeys.includes(file.id)),
      );
      setSelectedRowKeys([]);
      message.success(`成功删除 ${selectedRowKeys.length} 个文件`);
    } catch (error) {
      message.error('批量删除失败');
    }
  };

  const formatFileSize = (size: number): string => {
    if (size < 1024) {
      return `${size} B`;
    } else if (size < 1024 * 1024) {
      return `${(size / 1024).toFixed(2)} KB`;
    } else if (size < 1024 * 1024 * 1024) {
      return `${(size / (1024 * 1024)).toFixed(2)} MB`;
    } else {
      return `${(size / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    }
  };

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('image')) return '🖼️';
    if (type.includes('video')) return '🎬';
    if (type.includes('audio')) return '🎵';
    if (type.includes('text')) return '📝';
    if (type.includes('spreadsheet') || type.includes('excel')) return '📊';
    if (type.includes('presentation') || type.includes('powerpoint'))
      return '📽️';
    if (type.includes('word') || type.includes('document')) return '📝';
    return '📎';
  };

  const getFileType = (type: string): string => {
    const typeMap: { [key: string]: string } = {
      'application/pdf': 'PDF',
      'image/jpeg': 'JPEG',
      'image/png': 'PNG',
      'text/plain': 'TXT',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        'XLSX',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        'PPTX',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        'DOCX',
    };
    return typeMap[type] || type.split('/')[1]?.toUpperCase() || 'UNKNOWN';
  };

  const columns = [
    {
      title: '序号',
      key: 'index',
      width: 80,
      render: (_: any, __: any, index: number) => (
        <span>
          {(pagination.current - 1) * pagination.pageSize + index + 1}
        </span>
      ),
    },
    {
      title: '文件名',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: FileData) => (
        <Space>
          <span style={{ fontSize: '16px' }}>{getFileIcon(record.type)}</span>
          <span>{text}</span>
          {record.status === 'uploading' && (
            <Progress percent={record.percent || 0} size="small" />
          )}
        </Space>
      ),
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      width: 120,
      render: (size: number) => <span>{formatFileSize(size)}</span>,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type: string) => <Tag color="blue">{getFileType(type)}</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right' as const,
      width: 180,
      render: (_: any, record: FileData) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<DownloadOutlined />}
            onClick={() => handleDownload(record)}
          >
            下载
          </Button>
          <Popconfirm
            title={`确定要删除文件 "${record.name}" 吗？`}
            onConfirm={() => handleDeleteFile(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const uploadProps = {
    name: 'files',
    multiple: true,
    fileList: uploadFileList,
    beforeUpload: () => false, // 阻止自动上传
    onChange: (info: any) => {
      setUploadFileList(info.fileList);
    },
    onDrop: (e: any) => {
      console.log('Dropped files', e.dataTransfer.files);
    },
  };

  const handleTableChange = (page: number, pageSize: number) => {
    setPagination((prev) => ({ ...prev, current: page, pageSize }));
  };

  return (
    <div className={styles.fileManagementWrapper}>
      {/* 搜索区域 */}
      <Card className={styles.searchCard} size="small">
        <Space>
          <Input
            placeholder="请输入文件名搜索"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            style={{ width: 250 }}
            allowClear
          />
          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
            loading={loading}
          >
            搜索
          </Button>
          <Button icon={<ReloadOutlined />} onClick={handleReset}>
            重置
          </Button>
        </Space>
      </Card>

      {/* 文件列表 */}
      <Card className={styles.tableCard}>
        <div className={styles.tableHeader}>
          <Space>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={handleUpload}
            >
              上传文件
            </Button>
            <Popconfirm
              title={`确定删除选中的 ${selectedRowKeys.length} 个文件吗？`}
              onConfirm={handleBatchDelete}
              disabled={selectedRowKeys.length === 0}
            >
              <Button
                danger
                icon={<DeleteOutlined />}
                disabled={selectedRowKeys.length === 0}
              >
                批量删除
              </Button>
            </Popconfirm>
          </Space>
          <Button icon={<ReloadOutlined />} onClick={loadFileData}>
            刷新
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={fileData}
          rowKey="id"
          loading={loading}
          pagination={false}
          scroll={{ x: 1000 }}
          rowSelection={{
            selectedRowKeys,
            onChange: (selectedRowKeys: React.Key[]) =>
              setSelectedRowKeys(selectedRowKeys as string[]),
          }}
        />

        <div className={styles.paginationWrapper}>
          <Pagination
            current={pagination.current}
            pageSize={pagination.pageSize}
            total={pagination.total}
            onChange={handleTableChange}
            showSizeChanger
            showQuickJumper
            showTotal={(total, range) =>
              `第 ${range[0]}-${range[1]} 条/共 ${total} 条`
            }
          />
        </div>
      </Card>

      {/* 上传文件模态框 */}
      <Modal
        title="上传文件"
        open={uploadModalVisible}
        onOk={handleUploadSubmit}
        onCancel={() => setUploadModalVisible(false)}
        confirmLoading={uploadLoading}
        width={600}
        destroyOnClose
      >
        <div className={styles.uploadWrapper}>
          <Dragger {...uploadProps}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
            <p className="ant-upload-hint">
              支持单个或批量上传，支持多种文件格式
            </p>
          </Dragger>

          {uploadFileList.length > 0 && (
            <div className={styles.uploadFileList}>
              <div className={styles.uploadFileListTitle}>
                已选择文件 ({uploadFileList.length})
              </div>
              {uploadFileList.map((file, index) => (
                <div key={index} className={styles.uploadFileItem}>
                  <FileOutlined />
                  <span className={styles.fileName}>{file.name}</span>
                  <span className={styles.fileSize}>
                    {file.size ? formatFileSize(file.size) : '-'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default FileManagementPage;
