// pages/orders/orders.js
import { get, put } from '../../utils/request';
import { ensureLoggedIn } from '../../utils/auth';
import { CUSTOMER_SERVICE_WECHAT } from '../../utils/config';

const STATUS_TEXT = {
  pending: '待付款',
  paid: '待发货',
  shipped: '已发货',
  completed: '已完成',
  cancelled: '已取消'
};

Page({
  data: {
    orders: [],
    orderStatus: 'all',
        loading: false,
    skeletonOrders: [1, 2, 3],
    customerWechat: CUSTOMER_SERVICE_WECHAT,

    refundDialogVisible: false,
    refundOrder: null
  },

  onLoad() {
    if (!ensureLoggedIn()) return;
    this.loadPublicSettings();
    this.loadOrders();
  },

  onShow() {
    if (!ensureLoggedIn()) return;
    this.loadOrders();
  },

  onPullDownRefresh() {
    this.loadOrders(true);
  },

  loadPublicSettings() {
    get('/settings/public')
      .then(settings => {
        this.setData({
          customerWechat: settings.customer_service_wechat || CUSTOMER_SERVICE_WECHAT
        });
      })
      .catch(() => {});
  },

  switchTab(e) {
    const status = e.currentTarget.dataset.status;
    this.setData({ orderStatus: status });
    this.loadOrders();
  },

  loadOrders(fromPullDown = false) {
    this.setData({ loading: true });
    const customerWechat = this.data.customerWechat || CUSTOMER_SERVICE_WECHAT;

    get('/orders')
      .then(res => {
        let orders = Array.isArray(res) ? res : (res.data || []);
        if (this.data.orderStatus !== 'all') {
          orders = orders.filter(o => o.status === this.data.orderStatus);
        }

        orders = orders.map(o => ({
          ...o,
          order_no: o.order_number,
          status_text: STATUS_TEXT[o.status] || o.status,
          total_items: o.item_count || 0,
          total_amount: o.total_price || 0,
          items: o.items || [],
          shipping_text: o.status === 'shipped' ? '快递已发出，请注意查收' : '',
          service_note: ['paid', 'shipped', 'completed'].includes(o.status)
            ? `请务必添加客服微信 ${customerWechat}，客服会发送物流图片`
            : ''
        }));

        this.setData({ orders });
      })
      .catch(error => {
        console.error('Load orders error:', error);
        this.setData({ orders: [] });
        wx.showToast({ title: '加载失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ loading: false });
        if (fromPullDown) wx.stopPullDownRefresh();
      });
  },

  detailOrder(e) {
    const orderId = e.currentTarget.dataset.orderId;
    wx.navigateTo({ url: `/pages/order-detail/order-detail?orderId=${orderId}` });
  },

  payOrder(e) {
    const orderId = e.currentTarget.dataset.orderId;
    const customerWechat = this.data.customerWechat || CUSTOMER_SERVICE_WECHAT;
    wx.showModal({
      title: '立即支付',
      content: '是否确认支付该订单？',
      success: (res) => {
        if (!res.confirm) return;
        wx.showLoading({ title: '支付中...' });
        put(`/orders/${orderId}/pay`)
          .then(() => {
            wx.showModal({
              title: '支付成功',
              content: `请务必添加客服微信 ${customerWechat}，客服会发送物流图片。`,
              confirmText: '复制微信',
              cancelText: '稍后添加',
              success: (modalRes) => {
                if (modalRes.confirm) {
                  wx.setClipboardData({ data: customerWechat });
                }
              }
            });
            this.loadOrders();
          })
          .catch(error => {
            console.error('Pay order error:', error);
            wx.showToast({ title: error?.message || '支付失败', icon: 'none' });
          })
          .finally(() => wx.hideLoading());
      }
    });
  },

  confirmOrder(e) {
    const orderId = e.currentTarget.dataset.orderId;
    wx.showModal({
      title: '确认收货',
      content: '是否确认已收到商品？',
      success: (res) => {
        if (!res.confirm) return;
        wx.showLoading({ title: '处理中...' });
        put(`/orders/${orderId}/confirm`)
          .then(() => {
            wx.showToast({ title: '已确认收货', icon: 'success' });
            this.loadOrders();
          })
          .catch(error => {
            console.error('Confirm order error:', error);
            wx.showToast({ title: error?.message || '确认失败', icon: 'none' });
          })
          .finally(() => wx.hideLoading());
      }
    });
  },

  cancelOrder(e) {
    const orderId = e.currentTarget.dataset.orderId;
    wx.showModal({
      title: '取消订单',
      content: '是否确认取消该订单？',
      success: (res) => {
        if (!res.confirm) return;
        wx.showLoading({ title: '处理中...' });
        put(`/orders/${orderId}/cancel`)
          .then(() => {
            wx.showToast({ title: '订单已取消', icon: 'success' });
            this.loadOrders();
          })
          .catch(error => {
            console.error('Cancel order error:', error);
            wx.showToast({ title: error?.message || '取消失败', icon: 'none' });
          })
          .finally(() => wx.hideLoading());
      }
    });
  },

  // 退款/售后 — 弹出客服微信
  refundOrder(e) {
    const orderId = e.currentTarget.dataset.orderId;
    const order = this.data.orders.find(o => o.id === orderId);
    this.setData({
      refundDialogVisible: true,
      refundOrder: order
    });
  },

  closeRefundDialog() {
    this.setData({ refundDialogVisible: false, refundOrder: null });
  },

  copyCustomerWechat() {
    wx.setClipboardData({
      data: this.data.customerWechat || CUSTOMER_SERVICE_WECHAT,
      success: () => wx.showToast({ title: '微信号已复制', icon: 'success' })
    });
  },

  goToProducts() {
    wx.switchTab({ url: '/pages/products/products' });
  },

  goBack() {
    wx.switchTab({ url: '/pages/products/products' });
  }
});