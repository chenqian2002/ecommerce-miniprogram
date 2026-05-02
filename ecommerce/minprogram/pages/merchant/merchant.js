// pages/merchant/merchant.js
import { get, post, put, del } from '../../utils/request';
import { getUserInfo } from '../../utils/storage';
import { ensureMerchantLogin } from '../../utils/auth';
import { UPLOAD_BASE_URL } from '../../utils/config';

Page({
  data: {
    userInfo: {},
    categories: [],
    products: [],
    filteredProducts: [],
    merchantOrders: [],
    allMerchantOrders: [],
    orderSearchValue: '',
    orderStatusFilter: 'all',
    orderStatusTabs: [
      { label: '全部', value: 'all' },
      { label: '待发货', value: 'paid' },
      { label: '已发货', value: 'shipped' },
      { label: '待付款', value: 'pending' },
      { label: '已完成', value: 'completed' }
    ],
    salesTotal: '0.00',
    orderStats: [
      { label: '总订单', value: 0, type: 'total' },
      { label: '待发货', value: 0, type: 'paid' },
      { label: '已发货', value: 0, type: 'shipped' },
      { label: '已完成', value: 0, type: 'completed' },
      { label: '总销售额', value: '¥0.00', type: 'sales' }
    ],
    clearingOrders: false,
    searchValue: '',
    currentKeyword: '',
    loading: false,
    ordersLoading: false,
    submitting: false,
    shippingOrderId: null,
    uploadingImage: false,
    uploadingQrCode: false,
    selectedCategoryIndex: 0,
    newCategoryName: '',
    deletingCategoryId: null,
    currentFilter: 'all',
    announcementVisible: false,
    announcement: {
      id: null,
      title: '平台公告',
      content: ''
    },
    announcementEditorVisible: false,
    announcementSaving: false,
    merchantSettingsSaving: false,
    merchantSettingsForm: {
      merchant_id: '',
      official_appid: '',
      official_secret: '',
      customer_service_wechat: 'kefu888888',
      customer_service_qr_code: '/images/kefu-qrcode.png'
    },
    announcementForm: {
      title: '平台公告',
      content: '',
      is_active: true
    },
    filterTabs: [
      { label: '全部', value: 'all' },
      { label: '热销', value: 'hot' },
      { label: '促销', value: 'promo' }
    ],
    form: {
      id: null,
      name: '',
      description: '',
      price: '',
      original_price: '',
      stock: '',
      category_id: null,
      image_url: '',
      sales: '',
      rating: ''
    }
  },

  onLoad() {
    if (!ensureMerchantLogin()) {
      return;
    }
    this.loadUserInfo();
    this.loadCategories();
    this.loadProducts();
    this.loadMerchantOrders();
    this.loadAnnouncement();
    this.loadMerchantSettings();
  },

  onShow() {
    if (!ensureMerchantLogin()) return;
    this.loadMerchantOrders();
  },

  loadAnnouncement() {
    get('/announcement')
      .then(res => {
        const announcement = res || {};
        const hasContent = announcement.is_active && (announcement.content || '').trim() && (announcement.content || '').trim() !== '暂无公告';

        this.setData({
          announcementForm: {
            title: announcement.title || '平台公告',
            content: announcement.content || '',
            is_active: announcement.is_active !== false
          }
        });

        if (!hasContent) return;

        this.setData({
          announcementVisible: true,
          announcement: {
            id: announcement.id || null,
            title: announcement.title || '平台公告',
            content: announcement.content || ''
          }
        });
      })
      .catch(err => {
        console.error('Load announcement error:', err);
      });
  },

  loadMerchantSettings() {
    get('/merchant/settings')
      .then(settings => {
        this.setData({
          merchantSettingsForm: {
            merchant_id: settings.merchant_id || '',
            official_appid: settings.official_appid || '',
            official_secret: settings.official_secret || '',
            customer_service_wechat: settings.customer_service_wechat || 'kefu888888',
            customer_service_qr_code: settings.customer_service_qr_code || '/images/kefu-qrcode.png'
          }
        });
      })
      .catch(err => {
        console.error('Load merchant settings error:', err);
      });
  },

  handleMerchantSettingsInput(e) {
    const { field } = e.currentTarget.dataset;
    this.setData({
      merchantSettingsForm: {
        ...this.data.merchantSettingsForm,
        [field]: e.detail.value
      }
    });
  },

  saveMerchantSettings() {
    if (this.data.merchantSettingsSaving) return;

    const form = this.data.merchantSettingsForm;
    if (!(form.customer_service_wechat || '').trim()) {
      wx.showToast({ title: '请填写客服微信号', icon: 'none' });
      return;
    }

    this.setData({ merchantSettingsSaving: true });
    put('/merchant/settings', form)
      .then(settings => {
        wx.showToast({ title: '商家设置已保存', icon: 'success' });
        this.setData({
          merchantSettingsForm: {
            merchant_id: settings.merchant_id || '',
            official_appid: settings.official_appid || '',
            official_secret: settings.official_secret || '',
            customer_service_wechat: settings.customer_service_wechat || 'kefu888888',
            customer_service_qr_code: settings.customer_service_qr_code || '/images/kefu-qrcode.png'
          }
        });
      })
      .catch(err => {
        console.error('Save merchant settings error:', err);
        wx.showToast({ title: err.message || '保存设置失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ merchantSettingsSaving: false });
      });
  },

  chooseQrCode() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const filePath = res.tempFilePaths?.[0];
        if (!filePath) return;
        this.uploadQrCode(filePath);
      }
    });
  },

  uploadQrCode(filePath) {
    this.setData({ uploadingQrCode: true });

    wx.uploadFile({
      url: `${UPLOAD_BASE_URL}/api/upload/image`,
      filePath,
      name: 'file',
      header: {
        Authorization: `Bearer ${wx.getStorageSync('token')}`
      },
      success: (res) => {
        try {
          const data = JSON.parse(res.data || '{}');
          const imageUrl = data.url ? `${UPLOAD_BASE_URL}${data.url}` : '';
          if (!imageUrl) {
            throw new Error('上传失败');
          }

          this.setData({
            merchantSettingsForm: {
              ...this.data.merchantSettingsForm,
              customer_service_qr_code: imageUrl
            }
          });

          wx.showToast({ title: '二维码已上传', icon: 'success' });
        } catch (error) {
          console.error('Parse QR upload response error:', error);
          wx.showToast({ title: '二维码上传失败', icon: 'none' });
        }
      },
      fail: (error) => {
        console.error('Upload QR code error:', error);
        wx.showToast({ title: '二维码上传失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ uploadingQrCode: false });
      }
    });
  },

  loadMerchantOrders() {
    this.setData({ ordersLoading: true });
    get('/merchant/orders')
      .then(res => {
        const orders = Array.isArray(res) ? res : (res.data || []);
        const merchantOrders = orders.map(order => ({
          ...order,
          status_text: this.getOrderStatusText(order.status),
          total_amount: Number(order.total_price || 0),
          total_items: Number(order.item_count || 0),
          items_summary: order.items_summary || '暂无商品明细',
          receiver_name: order.address?.receiver_name || '未知收货人',
          receiver_phone: order.address?.phone || '暂无电话',
          address_text: order.address?.full_address || '暂无收货地址'
        }));
        const validOrders = merchantOrders.filter(order => order.status !== 'cancelled');
        const salesTotal = validOrders
          .reduce((sum, order) => sum + Number(order.total_amount || 0), 0)
          .toFixed(2);
        const orderStats = [
          { label: '总订单', value: merchantOrders.length, type: 'total' },
          { label: '待发货', value: merchantOrders.filter(order => order.status === 'paid').length, type: 'paid' },
          { label: '已发货', value: merchantOrders.filter(order => order.status === 'shipped').length, type: 'shipped' },
          { label: '已完成', value: merchantOrders.filter(order => order.status === 'completed').length, type: 'completed' },
          { label: '总销售额', value: `¥${salesTotal}`, type: 'sales' }
        ];
        this.setData({ allMerchantOrders: merchantOrders, salesTotal, orderStats }, () => this.applyOrderFilter());
      })
      .catch(err => {
        console.error('Load merchant orders error:', err);
        this.setData({
          merchantOrders: [],
          allMerchantOrders: [],
          salesTotal: '0.00',
          orderStats: [
            { label: '总订单', value: 0, type: 'total' },
            { label: '待发货', value: 0, type: 'paid' },
            { label: '已发货', value: 0, type: 'shipped' },
            { label: '已完成', value: 0, type: 'completed' },
            { label: '总销售额', value: '¥0.00', type: 'sales' }
          ]
        });
      })
      .finally(() => {
        this.setData({ ordersLoading: false });
      });
  },

  getOrderStatusText(status) {
    const statusMap = {
      pending: '待付款',
      paid: '待发货',
      shipped: '已发货',
      completed: '已完成',
      cancelled: '已取消'
    };
    return statusMap[status] || status || '未知状态';
  },

  applyOrderFilter() {
    const { allMerchantOrders, orderStatusFilter, orderSearchValue } = this.data;
    const keyword = (orderSearchValue || '').trim().toLowerCase();
    let merchantOrders = [...allMerchantOrders];

    if (orderStatusFilter !== 'all') {
      merchantOrders = merchantOrders.filter(order => order.status === orderStatusFilter);
    }

    if (keyword) {
      merchantOrders = merchantOrders.filter(order => {
        const searchable = [
          order.order_number,
          order.items_summary,
          order.receiver_name,
          order.receiver_phone,
          order.address_text,
          order.status_text
        ].join(' ').toLowerCase();
        return searchable.includes(keyword);
      });
    }

    this.setData({ merchantOrders });
  },

  handleOrderStatusFilter(e) {
    const status = e.currentTarget.dataset.status || 'all';
    this.setData({ orderStatusFilter: status }, () => this.applyOrderFilter());
  },

  handleOrderSearchInput(e) {
    this.setData({ orderSearchValue: e.detail.value || '' }, () => this.applyOrderFilter());
  },

  clearOrderSearch() {
    this.setData({ orderSearchValue: '', orderStatusFilter: 'all' }, () => this.applyOrderFilter());
  },

  shipOrder(e) {
    const orderId = e.currentTarget.dataset.orderId;
    if (!orderId || this.data.shippingOrderId) return;

    wx.showModal({
      title: '确认发货',
      content: '确定将该订单标记为已发货吗？',
      success: (res) => {
        if (!res.confirm) return;

        this.setData({ shippingOrderId: orderId });
        put(`/merchant/orders/${orderId}/ship`)
          .then(() => {
            wx.showToast({ title: '已发货', icon: 'success' });
            this.loadMerchantOrders();
          })
          .catch(err => {
            console.error('Ship order error:', err);
            wx.showToast({ title: err.message || '发货失败', icon: 'none' });
          })
          .finally(() => {
            this.setData({ shippingOrderId: null });
          });
      }
    });
  },

  clearMerchantOrders() {
    if (this.data.clearingOrders) return;

    wx.showModal({
      title: '清除订单',
      content: '确定清除商家后台订单记录吗？清除后只会在商家后台隐藏，不影响买家订单。',
      confirmText: '确认清除',
      confirmColor: '#dc2626',
      success: (res) => {
        if (!res.confirm) return;

        this.setData({ clearingOrders: true });
        del('/merchant/orders')
          .then(() => {
            wx.showToast({ title: '订单已清除', icon: 'success' });
            this.setData({
              merchantOrders: [],
              allMerchantOrders: [],
              salesTotal: '0.00',
              orderStats: [
                { label: '总订单', value: 0, type: 'total' },
                { label: '待发货', value: 0, type: 'paid' },
                { label: '已发货', value: 0, type: 'shipped' },
                { label: '已完成', value: 0, type: 'completed' },
                { label: '总销售额', value: '¥0.00', type: 'sales' }
              ]
            });
          })
          .catch(err => {
            console.error('Clear merchant orders error:', err);
            wx.showToast({ title: err.message || '清除失败', icon: 'none' });
          })
          .finally(() => {
            this.setData({ clearingOrders: false });
          });
      }
    });
  },

  openAnnouncementEditor() {
    this.setData({
      announcementEditorVisible: true
    });
  },

  closeAnnouncementEditor() {
    this.setData({ announcementEditorVisible: false });
  },

  handleAnnouncementInput(e) {
    const { field } = e.currentTarget.dataset;
    this.setData({
      announcementForm: {
        ...this.data.announcementForm,
        [field]: e.detail.value
      }
    });
  },

  toggleAnnouncementActive(e) {
    const is_active = !!e.detail.value;
    this.setData({
      announcementForm: {
        ...this.data.announcementForm,
        is_active
      }
    });
  },

  submitAnnouncementForm() {
    const { announcementForm, announcementSaving } = this.data;
    if (announcementSaving) return;

    const content = (announcementForm.content || '').trim();
    if (!content) {
      wx.showToast({ title: '请输入公告内容', icon: 'none' });
      return;
    }

    this.setData({ announcementSaving: true });

    post('/announcement', {
      title: (announcementForm.title || '平台公告').trim(),
      content,
      is_active: !!announcementForm.is_active
    })
      .then(res => {
        const announcement = res?.announcement || {};
        wx.showToast({ title: '公告已保存', icon: 'success' });
        this.setData({
          announcementEditorVisible: false,
          announcementVisible: false,
          announcement: {
            id: announcement.id || null,
            title: announcement.title || '平台公告',
            content: announcement.content || ''
          }
        });
        this.loadAnnouncement();
      })
      .catch(err => {
        console.error('Save announcement error:', err);
        wx.showToast({ title: err.message || '保存失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ announcementSaving: false });
      });
  },

  closeAnnouncement() {
    this.setData({
      announcementVisible: false,
      announcement: {
        id: null,
        title: '平台公告',
        content: ''
      }
    });
  },

  loadUserInfo() {
    const userInfo = getUserInfo() || {};
    this.setData({ userInfo });

    if (!userInfo.isMerchant && userInfo.role !== 'merchant') {
      wx.showToast({ title: '请先使用商家账号登录', icon: 'none' });
      setTimeout(() => {
        wx.reLaunch({ url: '/pages/login/login?entry=merchant' });
      }, 1200);
      return false;
    }

    return true;
  },

  loadCategories() {
    get('/categories')
      .then(res => {
        const categories = Array.isArray(res) ? res : (res.data || []);
        this.setData({ categories });
      })
      .catch(err => {
        console.error('Load categories error:', err);
        this.setData({ categories: [] });
      });
  },

  loadProducts() {
    this.setData({ loading: true });
    get('/products?page=1&page_size=100')
      .then(res => {
        const products = Array.isArray(res) ? res : (res.data || []);
        this.setData({ products, loading: false }, () => this.applyFilter());
      })
      .catch(err => {
        console.error('Load merchant products error:', err);
        this.setData({ products: [], filteredProducts: [], loading: false });
      });
  },

  applyFilter() {
    const { products, currentFilter, currentKeyword } = this.data;
    let filteredProducts = [...products];

    if (currentKeyword) {
      const keyword = currentKeyword.toLowerCase();
      filteredProducts = filteredProducts.filter(item => {
        const name = (item.name || '').toLowerCase();
        const desc = (item.description || '').toLowerCase();
        const sku = String(item.sku || '').toLowerCase();
        return name.includes(keyword) || desc.includes(keyword) || sku.includes(keyword);
      });
    }

    if (currentFilter === 'hot') {
      filteredProducts = filteredProducts.filter(item => (item.sales || 0) >= 1000);
    } else if (currentFilter === 'promo') {
      filteredProducts = filteredProducts.filter(item => {
        const hasPromoFlag = item.is_promo || item.promo || item.promotion;
        const hasDiscount = typeof item.original_price === 'number' && typeof item.price === 'number' && item.original_price > item.price;
        return hasPromoFlag || hasDiscount;
      });
    }

    this.setData({ filteredProducts });
  },

  handleFilterChange(e) {
    const currentFilter = e.currentTarget.dataset.filter || 'all';
    if (currentFilter === this.data.currentFilter) return;
    this.setData({ currentFilter }, () => this.applyFilter());
  },

  handleSearchInput(e) {
    const searchValue = e.detail.value || '';
    this.setData({ searchValue });
    if (!searchValue.trim()) {
      this.setData({ currentKeyword: '' }, () => this.applyFilter());
    }
  },

  handleSearch() {
    this.setData({ currentKeyword: (this.data.searchValue || '').trim() }, () => {
      this.applyFilter();
    });
  },

  clearSearch() {
    this.setData({ searchValue: '', currentKeyword: '' }, () => {
      this.applyFilter();
    });
  },

  handleInput(e) {
    const { field } = e.currentTarget.dataset;
    this.setData({
      form: {
        ...this.data.form,
        [field]: e.detail.value
      }
    });
  },

  handleCategoryChange(e) {
    const selectedCategoryIndex = Number(e.detail.value || 0);
    const selectedCategory = this.data.categories[selectedCategoryIndex];
    this.setData({
      selectedCategoryIndex,
      form: {
        ...this.data.form,
        category_id: selectedCategory ? selectedCategory.id : null
      }
    });
  },

  handleNewCategoryInput(e) {
    this.setData({ newCategoryName: e.detail.value || '' });
  },

  createCategory() {
    const name = (this.data.newCategoryName || '').trim();
    if (!name) {
      wx.showToast({ title: '请输入分类名称', icon: 'none' });
      return;
    }

    post('/categories', { name })
      .then(category => {
        wx.showToast({ title: '分类已添加', icon: 'success' });
        this.setData({ newCategoryName: '' });
        this.loadCategories();
        if (category && category.id) {
          this.setData({
            form: { ...this.data.form, category_id: category.id }
          });
        }
      })
      .catch(err => {
        console.error('Create category error:', err);
        wx.showToast({ title: err.message || '添加分类失败', icon: 'none' });
      });
  },

  deleteCategory(e) {
    const categoryId = e.currentTarget.dataset.categoryId;
    const categoryName = e.currentTarget.dataset.categoryName || '该分类';
    if (!categoryId || this.data.deletingCategoryId) return;

    wx.showModal({
      title: '删除分类',
      content: `确定删除「${categoryName}」吗？删除后商品不会被删除，只会变成未分类。`,
      confirmText: '删除',
      confirmColor: '#dc2626',
      success: (res) => {
        if (!res.confirm) return;

        this.setData({ deletingCategoryId: categoryId });
        del(`/categories/${categoryId}`)
          .then(() => {
            wx.showToast({ title: '分类已删除', icon: 'success' });
            const formCategoryId = Number(this.data.form.category_id || 0);
            this.setData({
              form: {
                ...this.data.form,
                category_id: formCategoryId === Number(categoryId) ? null : this.data.form.category_id
              },
              selectedCategoryIndex: 0
            });
            this.loadCategories();
            this.loadProducts();
          })
          .catch(err => {
            console.error('Delete category error:', err);
            wx.showToast({ title: err.message || '删除分类失败', icon: 'none' });
          })
          .finally(() => {
            this.setData({ deletingCategoryId: null });
          });
      }
    });
  },

  chooseImage() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const filePath = res.tempFilePaths?.[0];
        if (!filePath) return;

        this.uploadImage(filePath);
      }
    });
  },

  uploadImage(filePath) {
    this.setData({ uploadingImage: true });

    wx.uploadFile({
      url: `${UPLOAD_BASE_URL}/api/upload/image`,
      filePath,
      name: 'file',
      header: {
        Authorization: `Bearer ${wx.getStorageSync('token')}`
      },
      success: (res) => {
        try {
          const data = JSON.parse(res.data || '{}');
          const imageUrl = data.url ? `${UPLOAD_BASE_URL}${data.url}` : '';
          if (!imageUrl) {
            throw new Error('上传失败');
          }

          this.setData({
            form: {
              ...this.data.form,
              image_url: imageUrl
            }
          });

          wx.showToast({ title: '图片上传成功', icon: 'success' });
        } catch (error) {
          console.error('Parse upload response error:', error);
          wx.showToast({ title: '图片上传失败', icon: 'none' });
        }
      },
      fail: (error) => {
        console.error('Upload image error:', error);
        wx.showToast({ title: '图片上传失败', icon: 'none' });
      },
      complete: () => {
        this.setData({ uploadingImage: false });
      }
    });
  },

  resetForm() {
    this.setData({
      selectedCategoryIndex: 0,
      searchValue: '',
      currentKeyword: '',
      form: {
        id: null,
        name: '',
        description: '',
        price: '',
        original_price: '',
        stock: '',
        category_id: null,
        image_url: '',
        sales: '',
        rating: ''
      }
    }, () => this.applyFilter());
  },

  fillForm(e) {
    const product = e.currentTarget.dataset.product;
    const selectedCategoryIndex = Math.max(
      0,
      this.data.categories.findIndex(item => item.id === product.category_id)
    );

    this.setData({
      selectedCategoryIndex,
      form: {
        id: product.id,
        name: product.name || '',
        description: product.description || '',
        price: product.price?.toString() || '',
        original_price: product.original_price?.toString() || '',
        stock: product.stock?.toString() || '',
        category_id: product.category_id || null,
        image_url: product.image_url || '',
        sales: product.sales?.toString() || '',
        rating: product.rating?.toString() || ''
      }
    });
  },

  submitForm() {
    const { form, submitting } = this.data;
    if (submitting) return;

    if (!form.name || !form.price) {
      wx.showToast({ title: '请填写商品名称和价格', icon: 'none' });
      return;
    }

    const payload = {
      name: form.name,
      description: form.description,
      price: parseFloat(form.price),
      original_price: form.original_price ? parseFloat(form.original_price) : null,
      stock: parseInt(form.stock || '0', 10),
      category_id: form.category_id ? Number(form.category_id) : null,
      image_url: form.image_url,
      sales: parseInt(form.sales || '0', 10),
      rating: form.rating ? parseFloat(form.rating) : 5.0
    };

    this.setData({ submitting: true });

    const requestTask = form.id ? put(`/products/${form.id}`, payload) : post('/products', payload);

    requestTask
      .then(() => {
        wx.showToast({ title: form.id ? '商品已更新' : '商品已上架', icon: 'success' });
        this.resetForm();
        this.loadProducts();
      })
      .catch(err => {
        console.error('Submit product error:', err);
        wx.showToast({ title: err.message || '提交失败', icon: 'none' });
      })
      .finally(() => {
        this.setData({ submitting: false });
      });
  },

  editProduct(e) {
    const product = e.currentTarget.dataset.product;
    if (!product) return;
    this.fillForm({ currentTarget: { dataset: { product } } });
    wx.showToast({ title: '已进入编辑模式', icon: 'none' });
  },

  offShelfProduct(e) {
    const productId = e.currentTarget.dataset.productId;
    wx.showModal({
      title: '下架商品',
      content: '确定要下架这个商品吗？下架后将从前台列表移除。',
      success: (res) => {
        if (!res.confirm) return;
        del(`/products/${productId}`)
          .then(() => {
            wx.showToast({ title: '商品已下架', icon: 'success' });
            if (this.data.form.id === productId) {
              this.resetForm();
            }
            this.loadProducts();
          })
          .catch(err => {
            console.error('Off shelf product error:', err);
            wx.showToast({ title: err.message || '下架失败', icon: 'none' });
          });
      }
    });
  },

  deleteProduct(e) {
    this.offShelfProduct(e);
  },

  goBack() {
    wx.switchTab({ url: '/pages/products/products' });
  }
});

