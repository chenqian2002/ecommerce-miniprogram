// pages/order-detail/order-detail.js
import { get, put } from '../../utils/request';
import { CUSTOMER_SERVICE_WECHAT, CUSTOMER_SERVICE_QR_CODE } from '../../utils/config';

const STATUS_TEXT = {
  pending: '待付款',
  paid: '待发货',
  shipped: '已发货',
  completed: '已完成',
  cancelled: '已取消'
};

Page({
  data: {
    orderId: null,
    order: null,
    loading: false,
    actioning: false,
    customerWechat: CUSTOMER_SERVICE_WECHAT,
    customerQrCode: CUSTOMER_SERVICE_QR_CODE
  },

  onLoad(options) {
    const orderId = options.orderId ? parseInt(options.orderId) : null;
    if (!orderId) {
      wx.showToast({ title: '订单参数错误', icon: 'none' });
      return;
    }

    this.setData({ orderId });
    this.loadPublicSettings();
    this.loadOrderDetail(orderId);
  },

  onPullDownRefresh() {
    if (this.data.orderId) {
      this.loadOrderDetail(this.data.orderId, true);
    } else {
      wx.stopPullDownRefresh();
    }
  },

  loadPublicSettings() {
    get('/settings/public')
      .then(settings => {
        this.setData({
          customerWechat: settings.customer_service_wechat || CUSTOMER_SERVICE_WECHAT,
          customerQrCode: settings.customer_service_qr_code || CUSTOMER_SERVICE_QR_CODE
        });
      })
      .catch(err => {
        console.error('Load public settings error:', err);
      });
  },

  loadOrderDetail(orderId, fromPullDown = false) {
    this.setData({ loading: true });

    get(`/orders/${orderId}`)
      .then(res => {
        const order = res.data || res;
        this.setData({
          order: {
            ...order,
            status_text: STATUS_TEXT[order.status] || order.status,
            items: Array.isArray(order.items) ? order.items : []
          }
        });
      })
      .catch(error => {
        console.error('Load order detail error:', error);
        this.setData({ order: null });
        wx.showToast({ title: error?.message || error?.detail || '订单详情加载失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ loading: false });
        if (fromPullDown) wx.stopPullDownRefresh();
      });
  },

  payOrder() {
    const { orderId, actioning } = this.data;
    if (actioning) return;

    wx.showModal({
      title: '立即支付',
      content: '是否确认支付此订单？',
      success: (res) => {
        if (!res.confirm) return;

        this.setData({ actioning: true });
        put(`/orders/${orderId}/pay`)
          .then(() => {
            const customerWechat = this.data.customerWechat || CUSTOMER_SERVICE_WECHAT;
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
            this.loadOrderDetail(orderId);
          })
          .catch(error => {
            console.error('Pay order error:', error);
            wx.showToast({ title: error?.message || error?.detail || '支付失败', icon: 'none' });
          })
          .finally(() => {
            this.setData({ actioning: false });
          });
      }
    });
  },

  cancelOrder() {
    const { orderId, actioning } = this.data;
    if (actioning) return;

    wx.showModal({
      title: '取消订单',
      content: '取消后将恢复商品库存，是否确认取消？',
      success: (res) => {
        if (!res.confirm) return;

        this.setData({ actioning: true });
        put(`/orders/${orderId}/cancel`)
          .then(() => {
            wx.showToast({ title: '订单已取消', icon: 'success' });
            this.loadOrderDetail(orderId);
          })
          .catch(error => {
            console.error('Cancel order error:', error);
            wx.showToast({ title: error?.message || error?.detail || '取消失败', icon: 'none' });
          })
          .finally(() => {
            this.setData({ actioning: false });
          });
      }
    });
  },

  copyCustomerWechat() {
    wx.setClipboardData({
      data: this.data.customerWechat || CUSTOMER_SERVICE_WECHAT,
      success: () => wx.showToast({ title: '微信号已复制', icon: 'success' })
    });
  },

  goBack() {
    wx.switchTab({ url: '/pages/orders/orders' });
  }
});