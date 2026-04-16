// 本地存储工具

/**
 * 获取存储数据
 */
export function getStorage(key) {
  try {
    return wx.getStorageSync(key);
  } catch (e) {
    console.error('读取存储失败:', e);
    return null;
  }
}

/**
 * 设置存储数据
 */
export function setStorage(key, value) {
  try {
    wx.setStorageSync(key, value);
    return true;
  } catch (e) {
    console.error('写入存储失败:', e);
    return false;
  }
}

/**
 * 删除存储数据
 */
export function removeStorage(key) {
  try {
    wx.removeStorageSync(key);
    return true;
  } catch (e) {
    console.error('删除存储失败:', e);
    return false;
  }
}

/**
 * 清空所有存储
 */
export function clearStorage() {
  try {
    wx.clearStorageSync();
    return true;
  } catch (e) {
    console.error('清空存储失败:', e);
    return false;
  }
}

/**
 * 获取购物车
 */
export function getCart() {
  return getStorage('cart') || [];
}

/**
 * 保存购物车
 */
export function setCart(cart) {
  return setStorage('cart', cart);
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
  return getStorage('userInfo') || null;
}

/**
 * 保存用户信息
 */
export function setUserInfo(userInfo) {
  return setStorage('userInfo', userInfo);
}
