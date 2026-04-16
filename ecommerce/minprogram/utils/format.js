// 格式化工具

/**
 * 格式化价格
 */
export function formatPrice(price) {
  if (typeof price !== 'number') {
    price = parseFloat(price) || 0;
  }
  return `¥${price.toFixed(2)}`;
}

/**
 * 格式化日期
 */
export function formatDate(timestamp, format = 'YYYY-MM-DD HH:mm:ss') {
  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}

/**
 * 格式化订单状态
 */
export function formatOrderStatus(status) {
  const statusMap = {
    'pending': '待支付',
    'paid': '待发货',
    'shipped': '待收货',
    'delivered': '已收货',
    'completed': '已完成',
    'cancelled': '已取消'
  };
  return statusMap[status] || status;
}

/**
 * 格式化支付方式
 */
export function formatPaymentMethod(method) {
  const methodMap = {
    'wechat_pay': '微信支付',
    'alipay': '支付宝',
    'balance': '余额支付'
  };
  return methodMap[method] || method;
}

/**
 * 生成订单号
 */
export function generateOrderNumber() {
  const timestamp = Date.now();
  const random = Math.floor(Math.random() * 10000);
  return `${timestamp}${random}`;
}

/**
 * 计算购物车总价
 */
export function calculateCartTotal(cart) {
  return cart.reduce((total, item) => {
    return total + (item.price * item.quantity);
  }, 0);
}
