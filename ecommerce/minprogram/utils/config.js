// utils/config.js
// 统一管理接口地址，后续上线时只需要改这里
export const API_BASE_URL = 'http://127.0.0.1:8000/api';
export const UPLOAD_BASE_URL = 'http://127.0.0.1:8000';
export const CUSTOMER_SERVICE_WECHAT = 'kefu888888';
export const CUSTOMER_SERVICE_QR_CODE = '/images/kefu-qrcode.png';

// 开发模式：开启后微信登录会跳过真实微信验证（用 test_code）
export const DEV_MODE = true;
