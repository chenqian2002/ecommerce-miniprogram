// 网络请求工具库
const app = getApp();

/**
 * 封装网络请求
 */
export function request(options) {
  return new Promise((resolve, reject) => {
    const {
      url,
      method = 'GET',
      data = {},
      header = {},
      timeout = 15000  // 15秒超时
    } = options;

    // 获取token
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
                if (res.statusCode === 401) {
          wx.removeStorageSync('token');
          wx.reLaunch({
            url: '/pages/login/login'
          });
          reject(new Error('未授权，请重新登录'));
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

