// 网络请求工具库
const app = getApp();

/**
 * 底层请求，不做重试
 */
function rawRequest(options) {
  return new Promise((resolve, reject) => {
    const {
      url,
      method = 'GET',
      data = {},
      header = {},
      timeout = 15000
    } = options;

    const token = wx.getStorageSync('token');
    const finalHeader = {
      'Content-Type': 'application/json',
      ...header
    };

    if (token) {
      finalHeader['Authorization'] = `Bearer ${token}`;
    }

    wx.request({
      url: `${app.globalData.apiBaseUrl}${url}`,
      method,
      data,
      header: finalHeader,
      timeout,
      success(res) {
        if (res.statusCode === 401 || res.statusCode === 403) {
          const hasToken = !!wx.getStorageSync('token');
          const raw = res.data || {};
          const message = raw.detail || raw.message || (res.statusCode === 403 ? '无权限' : '未登录');

          if (res.statusCode === 401 && hasToken) {
            wx.clearStorageSync();
            wx.reLaunch({ url: '/pages/login/login' });
          }
          reject(new Error(message));
        } else if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          const raw = res.data;
          const message = raw?.message || raw?.detail || raw?.error || `请求失败(${res.statusCode})`;
          const error = new Error(message);
          error.statusCode = res.statusCode;
          error.response = raw;
          reject(error);
        }
      },
      fail(err) {
        console.error('Request fail:', err);
        const error = new Error(err.errMsg || '网络请求失败');
        error.original = err;
        if (err.errMsg && err.errMsg.includes('timeout')) {
          error.message = '请求超时，请检查网络或稍后重试';
        }
        reject(error);
      }
    });
  });
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function isRetryableError(error) {
  if (!error) return false;
  const msg = (error.message || '').toLowerCase();
  if (msg.includes('timeout') || msg.includes('网络') || msg.includes('network') || msg.includes('fail')) return true;
  if (error.statusCode && error.statusCode >= 500) return true;
  return false;
}

/**
 * 封装网络请求，支持自动重试
 * options.maxRetries: 最大重试次数，默认 2
 * options.retryDelay: 重试间隔毫秒数，默认 1000
 */
export function request(options) {
  const { maxRetries = 2, retryDelay = 1000, ...rawOptions } = options || {};

  function attempt(retriesLeft) {
    return rawRequest(rawOptions).catch(error => {
      if (retriesLeft > 0 && isRetryableError(error)) {
        console.warn(`[Request] 请求失败，剩余重试 ${retriesLeft} 次:`, error.message);
        return delay(retryDelay).then(() => attempt(retriesLeft - 1));
      }
      throw error;
    });
  }

  return attempt(maxRetries);
}

/**
 * GET 请求
 */
export function get(url, data = {}) {
  return request({
    url,
    method: 'GET',
    data
  });
}

/**
 * POST 请求
 */
export function post(url, data = {}) {
  return request({
    url,
    method: 'POST',
    data
  });
}

/**
 * PUT 请求
 */
export function put(url, data = {}) {
  return request({
    url,
    method: 'PUT',
    data
  });
}

/**
 * DELETE 请求
 */
export function del(url, data = {}) {
  return request({
    url,
    method: 'DELETE',
    data
  });
}

/**
 * 防重复提交锁（防止短时间内重复调用）
 */
const _pendingLocks = {};

export function withLock(key, fn) {
  if (_pendingLocks[key]) return Promise.resolve();
  _pendingLocks[key] = true;
  return fn().finally(() => {
    setTimeout(() => { _pendingLocks[key] = false; }, 1500);
  });
}

