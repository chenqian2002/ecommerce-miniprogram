// pages/order-detail/order-detail.js
import { get, put } from '../../utils/request';

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
    actioning: false
  },

  onLoad(options) {
    const orderId = options.orderId ? parseInt(options.orderId) : null;
    if (!orderId) {
      wx.showToast({ title: '订单参数错误', icon: 'none' });
      return;
    }

    this.setData({ orderId });
    this.loadOrderDetail(orderId);
  },

  onPullDownRefresh() {
    if (this.data.orderId) {
      this.loadOrderDetail(this.data.orderId, true);
    } else {
      wx.stopPullDownRefresh();
    }
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
            wx.showToast({ title: '支付成功', icon: 'success' });
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

  confirmReceive() {
    const { orderId, actioning } = this.data;
    if (actioning) return;

    wx.showModal({
      title: '确认收货',
      content: '确认已经收到商品了吗？',
      success: (res) => {
        if (!res.confirm) return;

        this.setData({ actioning: true });
        put(`/orders/${orderId}/confirm`)
          .then(() => {
            wx.showToast({ title: '已确认收货', icon: 'success' });
            this.loadOrderDetail(orderId);
          })
          .catch(error => {
            console.error('Confirm order error:', error);
            wx.showToast({ title: error?.message || error?.detail || '确认失败', icon: 'none' });
          })
          .finally(() => {
            this.setData({ actioning: false });
          });
      }
    });
  },

  goBack() {
    wx.switchTab({ url: '/pages/orders/orders' });
  }
});