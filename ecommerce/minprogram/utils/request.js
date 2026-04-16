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
      timeout = 8000  // 8秒超时
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

    // 额外的超时控制
    const timeoutHandle = setTimeout(() => {
      reject(new Error('请求超时，请检查网络'));
    }, timeout);

    wx.request({
      url: `${app.globalData.apiBaseUrl}${url}`,
      method,
      data,
      header: finalHeader,
      timeout: timeout,
      success(res) {
        clearTimeout(timeoutHandle);
        if (res.statusCode === 401) {
          // token过期，清除并跳转到登录
          wx.removeStorageSync('token');
          wx.redirectTo({
            url: '/pages/login/login'
          });
          reject(new Error('未授权，请重新登录'));
        } else if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(new Error(res.data.message || '请求失败'));
        }
      },
      fail(err) {
        clearTimeout(timeoutHandle);
        console.error('Request fail:', err);
        reject(err);
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
