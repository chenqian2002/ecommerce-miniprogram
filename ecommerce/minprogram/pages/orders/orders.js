// pages/orders/orders.js
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
    orders: [],
    orderStatus: 'all',
    loading: false
  },

  onLoad() {
    this.loadOrders();
  },

  onShow() {
    this.loadOrders();
  },

  onPullDownRefresh() {
    this.loadOrders(true);
  },

  switchTab(e) {
    const status = e.currentTarget.dataset.status;
    this.setData({ orderStatus: status });
    this.loadOrders();
  },

  loadOrders(fromPullDown = false) {
    this.setData({ loading: true });

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
          items: o.items || []
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
    wx.navigateTo({
      url: `/pages/order-detail/order-detail?orderId=${orderId}`
    });
  },

  payOrder(e) {
    const orderId = e.currentTarget.dataset.orderId;
    wx.showModal({
      title: '立即支付',
      content: '是否确认支付该订单？',
      success: (res) => {
        if (!res.confirm) return;
        wx.showLoading({ title: '支付中...' });
        put(`/orders/${orderId}/pay`)
          .then(() => {
            wx.showToast({ title: '支付成功', icon: 'success' });
            this.loadOrders();
          })
          .catch(error => {
            console.error('Pay order error:', error);
            wx.showToast({ title: error?.message || error?.detail || '支付失败', icon: 'none' });
          })
          .finally(() => {
            wx.hideLoading();
          });
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
            wx.showToast({ title: error?.message || error?.detail || '取消失败', icon: 'none' });
          })
          .finally(() => {
            wx.hideLoading();
          });
      }
    });
  },

    goToProducts() {
    wx.switchTab({
      url: '/pages/products/products'
    });
  },

  goBack() {
    wx.switchTab({
      url: '/pages/products/products'
    });
  }
});


