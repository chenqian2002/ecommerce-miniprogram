// pages/merchant/merchant.js
import { get, post, put, del } from '../../utils/request';
import { getUserInfo } from '../../utils/storage';
import { UPLOAD_BASE_URL } from '../../utils/config';

Page({
  data: {
    userInfo: {},
    categories: [],
    products: [],
    filteredProducts: [],
    searchValue: '',
    currentKeyword: '',
    loading: false,
    submitting: false,
    uploadingImage: false,
    selectedCategoryIndex: 0,
    currentFilter: 'all',
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
      category_id: '',
      image_url: '',
      sales: '',
      rating: ''
    }
  },

  onLoad() {
    if (!this.loadUserInfo()) {
      return;
    }
    this.loadCategories();
    this.loadProducts();
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
        category_id: selectedCategory ? selectedCategory.id : ''
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
        category_id: '',
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
        category_id: product.category_id?.toString() || '',
        image_url: product.image_url || '',
        sales: product.sales?.toString() || '',
        rating: product.rating?.toString() || ''
      }
    });
  },

  submitForm() {
    const { form, submitting } = this.data;
    if (submitting) return;

    if (!form.name || !form.price || !form.category_id) {
      wx.showToast({ title: '请填写商品名称、价格和分类', icon: 'none' });
      return;
    }

    const payload = {
      name: form.name,
      description: form.description,
      price: parseFloat(form.price),
      original_price: form.original_price ? parseFloat(form.original_price) : null,
      stock: parseInt(form.stock || '0', 10),
      category_id: parseInt(form.category_id, 10),
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
